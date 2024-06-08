# 더모아 카드 아마존 자동 결제 스크립트

## 기능

- Playwright 기반 자동화
    1. [TheMore.App](https://themore.app) 에서 구매 가능한 아마존 기프트 카드 목록 중 가장 저렴한 가격의 기프트 카드 추출
        - 환율 보정 등의 기능을 사용하여 사용자가 원하는 정책 기반으로 설정
    2. 아마존 기프트 카드 구매 페이지에 접속하여 추출한 달러 금액으로 기프트 카드 구매 시도
    3. 입력한 계정 정보로 로그인 시도
        - 기본적인 Captcha의 경우 자동으로 처리되나, OTP, 이메일 인증 등은 처리 불가
    4. 주 거래 카드로 구매 시도

## 사용법

1. 프로젝트 클론
    - `git clone https://github.com/cda2/themore_amazon`
2. `config.json` 파일을 열어서 설정 파일 수정
    1. 아마존 계정 정보를 입력
        1. `email`: 아마존 이메일
        2. `password`: 아마존 비밀번호
    2. 브라우저 관련 설정 (관심 없는 경우 수정 불필요)
        1. `timeout`: 브라우저 타임아웃, 기본 값은 `10000.0`
        2. `headless`: 브라우저를 숨김 모드로 실행할지 여부, 기본 값은 `False` (`xvfb` 미 사용 시 `True` 로 설정)
    3. 가격, 환율 보정 등의 기능이 기본적으로 설정되어 있으나, 필요에 따라 수정 가능 (환율 보정 관련 내용은 [TheMore.App](https://themore.app) 참고)
        1. `min_order_price`: 최소 주문 금액, 기본 값은 `5.0` (달러 기준, 최소 금액 기준이 이후 변경되는 경우 설정 값을 수정할 것)
        2. `is_safe`: `True` 인 경우 환율 보정 처리를 수행, 기본 값은 `True`
        3. `safe_gap`: 환율 보정 시 사용할 환율 오차, 기본 값은 `1.0`
            - 필자가 사용해 본 바로는 환율 보정을 지나치게 높게 사용해도, 안정적인 환율 변화가 장시간 지속 시 손해가 됨
3. `docker` 환경 구성
4. `docker run --mount type=bind,source="$(pwd)"/config.yml,target=/app/config.yml,readonly --init $(docker build -q .)`
   명령어 실행

### 올인원 스크립트 (`docker` 필요, `EMAIL`, `PASSWORD` 환경변수 설정 필요)

```shell
# EMAIL="아마존 이메일"
# PASSWORD="아마존 비밀번호"
sed -i -e "s/your_email@example.com/$EMAIL/" -e "s/your_password/$PASSWORD/" config.yml
docker run --mount type=bind,source="$(pwd)"/config.yml,target=/app/config.yml,readonly --init $(docker build -q .)
```

## 유의사항

- 브라우저 옵션에서 `headless` 를 `True` 로 설정 시 아마존에서 높은 확률로 이메일 인증을 요구할 수 있음
    - 가상 디스플레이 등으로 해결 가능
        - [xvfb](https://en.wikipedia.org/wiki/Xvfb) 등 참고
        - 또는 설정 파일 수정 후 Dockerfile 실행
- 스크립트 실행 시 자주 사용하던 IP 주소가 아닌 경우 아마존에서 재로그인, 캡챠 등을 요구할 수 있음
    - 프록시 설정 등으로 해결 가능
    - 가급적 자주 사용하는 IP 주소에서 실행할 것을 권장

## 실행 환경

Python 3.10+

## Thanks to

- [TheMore.App](https://themore.app)
- [www.thecashback.kr](https://www.thecashback.kr/exchangerate.php)

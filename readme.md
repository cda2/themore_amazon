# 더모아 카드 아마존 자동 결제 스크립트

## 기능

- Playwright 기반 자동화
    1. [www.thecashback.kr](https://www.thecashback.kr/exchangerate.php) 에 접속하여
       5999에 가장 가까운 달러 금액을 추출
    2. 아마존 기프트 카드 구매 페이지에 접속하여 추출한 달러 금액으로 기프트 카드 구매 시도
    3. 입력한 계정 정보로 로그인 시도
        - 기본적인 Captcha의 경우 자동으로 처리되나, OTP, 이메일 인증 등은 처리 불가
    4. 주 거래 카드로 구매 시도

## 사용법

1. 프로젝트 클론
    - `git clone https://github.com/cda2/themore_amazon`
2. `config.json` 파일을 열어서 아마존 계정 정보를 입력
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

[www.thecashback.kr](https://www.thecashback.kr/exchangerate.php)

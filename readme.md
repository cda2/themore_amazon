# 더모아 카드 아마존 자동 결제 스크립트

## 사용법

1. `config.json` 파일을 열어서 아마존 계정 정보를 입력
2. `poetry` 를 이용해 패키지 설치하여 실행

## 유의사항

- 브라우저 옵션에서 `headless` 를 `True` 로 설정 시 아마존에서 높은 확률로 이메일 인증을 요구할 수 있음
    - 가상 디스플레이 등으로 해결 가능
- 스크립트 실행 시 자주 사용하던 IP 주소가 아닌 경우 아마존에서 재로그인, 캡챠 등을 요구할 수 있음
    - 프록시 설정 등으로 해결 가능

## 실행 환경
Python 3.9+

## Thanks to
[www.thecashback.kr](https://www.thecashback.kr/exchangerate.php)

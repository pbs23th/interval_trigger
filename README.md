<img src="https://capsule-render.vercel.app/api?type=waving&color=auto&height=200&section=header&text=interval trigger&fontSize=90" /></n>
# 
# GMC-LABS
## _급등 급락 트리거 발생 프로그램_

- <img src="https://img.shields.io/badge/PYTHON-3776AB?style=flat&logo=Python&logoColor=white" />
- <img src="https://img.shields.io/badge/REDIS-4479A1?style=flat&logo=Redis&logoColor=white&color=inactive" />


## 사용 거래소
 - okx 현물 / 선물
 - upbit

## 프로그램 설명
 - 티커 수집해서 5분단위 첫 데이터 레디스에 저장후 들어오는 데이터와 저장된 데이터를 비교
 - 간격이 5%가 넘어갈시 트리거 발생, 현재는 슬랙으로 내용 전송
 - 슬랙전송, pub/sub 채널명, 트리거 발동 간격 기준 모두 하드코딩 되어있음

## 설치

우분투 사용시 설치

```sh
sudo apt update
sudo apt install python3.11, python3-pip
sudo apt install redis-server
sudo apt install npm
sudo npm install -g npm
sudo npm install -g pm2 #백그라운드 실행 프로그램
sudo pip3 install requirments.txt #python 모듈 리스트 설치
```

## 실행

```sh
sudo pm2 start --interpreter=python3 interval_trigger/pubsub/sub.py #레디스 sub 핸들러 
sudo pm2 start --interpreter=python3 interval_trigger/ws/upbit_ws.py #업비트 웹소켓
sudo pm2 start --interpreter=python3 interval_trigger/ws/okx_ws_swap.py #okx선물 웹소켓
sudo pm2 start --interpreter=python3 interval_trigger/ws/okx_ws_spot.py #okx현물 웹소켓
```

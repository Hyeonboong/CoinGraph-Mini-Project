import requests

url = "https://api.upbit.com/v1/market/all"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

data = response.json()

tickers = []

for market in data:
    if "KRW-" in market['market']:  # "market" key 에 KRW- 로 시작되면,  
        tickers.append(market['korean_name']) # tickers 리스트에 KRW 코인의 한국 명칭을 넣는다.

print(tickers)


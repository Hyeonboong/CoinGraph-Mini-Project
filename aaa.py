import requests

url = "https://api.upbit.com/v1/candles/months?market=KRW-BTC&count=13"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)
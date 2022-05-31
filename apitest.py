import requests
import time

header = {
    "Username": "admin1",
    "Password": "the1stpass"
}
resp = requests.get('http://127.0.0.1:5000/api/login', headers=header)

token = resp.json()['token']

for i in range(0,7):
    time.sleep(1)
    resp = requests.get('http://127.0.0.1:5000/api/all?token=' + token)

    print(resp.text)
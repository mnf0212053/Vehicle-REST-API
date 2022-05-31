import requests
import time

header_admin1 = {
    "Username": "admin1",
    "Password": "the1stpass"
}

header_admin2 = {
    "Username": "admin2",
    "Password": "admin2pwd"
}


def checkAuthorization(header):
    print("\nChecking " + header["Username"] + " authorization...")
    resp = requests.get('http://127.0.0.1:5000/api/login', headers=header)

    token = resp.json()['token']

    for i in range(0,2):
        time.sleep(1)
        resp = requests.get('http://127.0.0.1:5000/api/all?token=' + token)

        print(resp.text)
    print("Checking for " + header["Username"] + " finished.\n")
    time.sleep(1)

checkAuthorization(header_admin1)
checkAuthorization(header_admin2)
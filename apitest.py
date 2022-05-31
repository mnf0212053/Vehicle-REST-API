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

class Tester:
    def __init__(self):
        pass

    def login(self, header):
        resp = requests.get('http://127.0.0.1:5000/api/login', headers=header)
        return resp.json()['token']

    def checkNoAuthorization(self):
        print("\nRequesting without token:")
        try:
            resp = requests.get('http://127.0.0.1:5000/api/all')
            print(resp.text)
        except:
            print("\bUnable to access.")
        time.sleep(1)

    def checkAuthorization(self, header):
        print("\nChecking " + header["Username"] + " authorization...")
        resp = requests.get('http://127.0.0.1:5000/api/login', headers=header)

        token = resp.json()['token']

        for i in range(0,2):
            time.sleep(1)
            resp = requests.get('http://127.0.0.1:5000/api/all?token=' + token)

            print(resp.text)
        print("Checking for " + header["Username"] + " finished.\n")
        time.sleep(1)

    def checkInputNoAuthorization(self):
        print("Check input data without authorization:")
        body = {
            "entry": {
                "columns": ['code', 'price', 'year_id', 'model_id'],
                "data":["23", 13999999, 2, 3]
            }
        }

        resp = requests.post('http://127.0.0.1:5000/api/input_price', data=body)
        print(resp.text)
        print("Checking finished")

    def checkInputAuthorization(self, header):
        print("Check input data with authorization for " + header["Username"] + ":")
        token = self.login(header)

        body = {
            "columns": ['code', 'price', 'year_id', 'model_id'],
            "data": [['23', 13999999, 2, 3]]
        }

        for i in range(0, 2):
            time.sleep(1)
            resp = requests.post('http://127.0.0.1:5000/api/input_price?token=' + token, data=body)
            print(resp.text)
        print("Checking finished")

    def checkUpdateNoAuthorization(self):
        print('Checking for update without authorization:')
        body = {
            "column-to-update": ['price', 'year-id'],
            "data-to-update": [19999999, 3],
            "column-search": ['code'],
            "data-search": ['23']
        }

        resp = requests.post('http://127.0.0.1:5000/api/update_price', data=body)
        print(resp.text)
        print("Checking finished")

    def checkUpdateAuthorization(self, header):
        print("Check update data with authorization for " + header["Username"] + ":")
        token = self.login(header)
        body = {
            "column-to-update": ['price', 'year_id'],
            "data-to-update": [19999999, 3],
            "column-search": ['code'],
            "data-search": ['23']
        }

        resp = requests.post('http://127.0.0.1:5000/api/update_price?token=' + token, data=body)
        print(resp.text)
        print("Checking finished")

test = Tester()
test.checkNoAuthorization()
test.checkAuthorization(header_admin1)
test.checkAuthorization(header_admin2)

test.checkInputNoAuthorization()
test.checkInputAuthorization(header_admin1)
test.checkInputAuthorization(header_admin2)
test.checkAuthorization(header_admin1)

test.checkUpdateNoAuthorization()
test.checkAuthorization(header_admin1)
test.checkUpdateAuthorization(header_admin2)
test.checkUpdateAuthorization(header_admin1)
test.checkAuthorization(header_admin1)

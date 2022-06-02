from flask import Flask, jsonify, Request
from flask_restful import Api, Resource, reqparse
import os
import sqlite3
import jwt
import hashlib
import datetime
import sql
import json

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()

f = open(os.path.dirname(__file__) + '\\config.json', 'r')
conf_data = json.load(f)
f.close()

app.config['SECRET_KEY'] = '2un29hd2982'
def generateCode(id1, id2):
    return str(id1) + str(id2)

def data_init():
    sql.remove_db()
    
    sql.create_table('users', ['name', 'is_admin', 'pass'], ['varchar(30)', 'integer', 'varchar(255)'])
    sql.create_table('vehicle_brand', ['name'], ['varchar(30)'])
    sql.create_table('vehicle_type', ['name', 'brand_id'], ['varchar(30)', 'integer'], ['brand_id'], ['vehicle_brand'])
    sql.create_table('vehicle_model', ['name', 'type_id'], ['varchar(30)', 'integer'], ['type_id'], ['vehicle_type'])
    sql.create_table('vehicle_year', ['year'], ['integer'])
    sql.create_table('pricelist', ['code', 'price', 'year_id', 'model_id'], ['varchar(30)', 'integer', 'integer', 'integer'], ['year_id', 'model_id'], ['vehicle_year', 'vehicle_model'])
    
    pass1 = hashlib.sha256(b'the1stpass').hexdigest()
    pass2 = hashlib.sha256(b'admin2pwd').hexdigest()

    users = [['admin1', 1, pass1], ['admin2', 0, pass2]]
    brands = [['Honda'], ['Toyota'], ['Mitsubishi']]
    types = [['Vario', 1], ['Spacy', 1], ['Avanza', 2], ['Pajero', 3]]
    models = [['125cc', 1], ['2014', 2], ['MPV', 2], ['SUV', 4], ['250cc', 1], ['MPV', 3]]
    years = [[2014], [2015], [2016], [2017]]

    pricelists = [[generateCode(1,1), 9999999, 1, 1], [generateCode(1,2), 8888888, 1, 2]]

    sql.insert_data_init(users, 'users', ['name', 'is_admin', 'pass'])
    sql.insert_data_init(brands, 'vehicle_brand', ['name'])
    sql.insert_data_init(types, 'vehicle_type', ['name', 'brand_id'])
    sql.insert_data_init(models, 'vehicle_model', ['name', 'type_id'])
    sql.insert_data_init(years, 'vehicle_year', ['year'])
    sql.insert_data_init(pricelists, 'pricelist', ['code', 'price', 'year_id', 'model_id'])

class Authorization:
    def __init__(self):
        self.isAuthorized = False
        self.errorMsg = ""

    def authorize(self, readOnly = True):
        self.isAuthorized = False
        parser.add_argument('token', location = 'args')
        args = parser.parse_args()

        if args['token'] == None:
            return False
        else:
            try:
                decoded = jwt.decode(args['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.exceptions.ExpiredSignatureError:
                self.errorMsg = "Signature has expired."
                return False
        
        if not readOnly:
            if sql.get_userAuthr(decoded["username"])[0] == 0:
                self.errorMsg = "Authorization blocked"
                return False
        self.isAuthorized = True
        return True

auth = Authorization()

class VehicleApp(Resource):
    def get(self):
        parser.add_argument('foo', location = 'args')
        args = parser.parse_args()
        return jsonify({'text': args['foo']})

class GetAll(Resource):
    def get(self):
        if not auth.authorize():
            return jsonify({"message": auth.errorMsg})

        join_result = sql.inner_join()

        data = join_result["data"]
        col_arr = join_result["columns"]

        data_dict = {}

        data_array = []

        for i in data:
            for j in range(0, len(col_arr)):
                data_dict[col_arr[j]] = i[j]
            data_array.append(data_dict)
            data_dict = {}

        return jsonify(data_array)

class Search(Resource):
    def get(self):
        if not auth.authorize(readOnly=False):
            return jsonify({"message": auth.errorMsg})
            
        parser.add_argument('q', location = 'args')
        parser.add_argument('b', location = 'args')
        args = parser.parse_args()

        join_result = sql.inner_join(query = args['q'].capitalize(), by = args['b'])
        if join_result["data"] == None:
            return jsonify({"msg": "Entry Not Found"})
        
        data = join_result["data"]
        col_arr = join_result["columns"]

        data_dict = {}

        data_array = []

        for i in data:
            for j in range(0, len(col_arr)):
                data_dict[col_arr[j]] = i[j]
            data_array.append(data_dict)
            data_dict = {}

        return jsonify(data_array)

class InputPrice(Resource):
    def post(self):
        if not auth.authorize(readOnly=False):
            return jsonify({"message": auth.errorMsg})

        parser.add_argument('columns', action = 'append')
        parser.add_argument('data', action = 'append')

        args = parser.parse_args()
        sql.insert_data_init([args['data']], 'pricelist', args['columns'])

        return jsonify({"message": "Input Success!"})

class UpdatePrice(Resource):
    def post(self):
        if not auth.authorize(readOnly=False):
            return jsonify({"message": auth.errorMsg})

        parser.add_argument('column-to-update', action = 'append')
        parser.add_argument('data-to-update', action = 'append')
        parser.add_argument('column-search', action = 'append')
        parser.add_argument('data-search', action = 'append')

        args = parser.parse_args()

        sql.update_data(args['column-to-update'], args['data-to-update'], 'pricelist', args['column-search'], args['data-search'])

        return jsonify({"message": "Update Success!"})

class DeletePriceByID(Resource):
    def delete(self):
        if not auth.authorize(readOnly=False):
            return jsonify({"message": auth.errorMsg})

        parser.add_argument('id')
        args = parser.parse_args()

        if not sql.check_if_exist('pricelist',['id'], [args['id']]):
            return jsonify({"message": "Data doesn't exist"})

        sql.delete_by_id(args['id'])

        return jsonify({"message": "Delete Successful!"})

class Authentication(Resource):
    def get(self):
        parser.add_argument('Username', location = 'headers')
        parser.add_argument('Password', location = 'headers')

        args = parser.parse_args()

        passq = hashlib.sha256(bytes(args['Password'], 'utf-8')).hexdigest()

        if args['Password'] == None or passq != sql.get_userpw(args['Username'])[0]:
            return jsonify({"message": "Authentication error"}, 401)
        else:
            payload = {
                "username": args["Username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=conf_data['login-expired-in-sec'])
            }
            jwt_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({"token": jwt_token})

api.add_resource(VehicleApp, '/api')
api.add_resource(GetAll, '/api/all')
api.add_resource(Search, '/api/search')
api.add_resource(Authentication, '/api/login')
api.add_resource(InputPrice, '/api/input_price')
api.add_resource(UpdatePrice, '/api/update_price')
api.add_resource(DeletePriceByID, '/api/delete_price_by_id')

data_init()

if __name__ == '__main__':
    app.run(debug=True)
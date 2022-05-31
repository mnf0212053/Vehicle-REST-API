from flask import Flask, jsonify, Request
from flask_restful import Api, Resource, reqparse
import os
import sqlite3
import jwt
import hashlib
import datetime

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()

app.config['SECRET_KEY'] = '2un29hd2982'

db = os.path.dirname(__file__) + '\\vehicle_db.db'

def insert_data_init(data, table, columns):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    sql = " INSERT INTO " + table + "("
    for i in range(0, len(columns)):
        sql += columns[i]
        if i < len(columns) - 1:
            sql += ","
    
    sql += ") VALUES ("

    for i in range(0, len(columns)):
        sql += "?"
        if i < len(columns) - 1:
            sql += ","

    sql += ");"

    for i in data:
        cur.execute(sql, tuple(i))
        conn.commit()

    conn.close()
    
def create_table(name, columns, dtypes, fkey = [], tabref = []):
    sql = " CREATE TABLE IF NOT EXISTS " + name + "(id integer PRIMARY KEY,"
    for i in range(0, len(columns)):
        sql += columns[i]
        sql += " "
        sql += dtypes[i]
        if i < len(columns) - 1:
            sql += ", "

    for i in range(0, len(fkey)):
        if i == 0:
            sql += ", "
        sql += "FOREIGN KEY (" + fkey[i] + ") REFERENCES " + tabref[i] + "(id)"
        if i < len(fkey) - 1:
            sql += ", "
    sql += ");"

    conn = sqlite3.connect(db)

    cur = conn.cursor()
    cur.execute(sql)

    conn.close()

def get_columns(table):
    sql = " PRAGMA table_info(" + table + ");"

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute(sql)

    cols = cur.fetchall()

    conn.close()

    return cols

def get_userpw(username):
    sql = 'SELECT pass FROM users WHERE name=?'

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql, (username,))

    pw = cur.fetchone()
    conn.close()

    return pw

def get_userAuthr(username):
    sql = 'SELECT is_admin FROM users WHERE name=?'

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql, (username,))

    authr = cur.fetchone()
    conn.close()

    return authr

def generateCode(id1, id2):
    return str(id1) + str(id2)

def inner_join(query = None, by = 'type'):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    sql = "SELECT p.code, b.name, t.name, m.name, p.price, y.year FROM pricelist p "
    sql += "INNER JOIN vehicle_model m ON p.model_id = m.id "
    sql += "INNER JOIN vehicle_year y ON p.year_id = y.id "
    sql += "INNER JOIN vehicle_type t ON m.type_id = t.id "
    sql += "INNER JOIN vehicle_brand b ON t.brand_id = b.id"

    if query != None:
        if by == 'type':
            sql += " WHERE t.name=?"
        elif by == 'brand':
            sql += " WHERE b.name=?"
        elif by == 'model':
            sql += " WHERE m.name=?"
        elif by == 'code':
            sql += " WHERE p.code=?"
        elif by == 'price':
            sql += " WHERE p.price=?"
        elif by == 'year':
            sql += " WHERE y.year=?"
        else:
            sql += " WHERE t.name=?"

        cur.execute(sql, (query,))
    else:
        cur.execute(sql)

    data = cur.fetchall()

    conn.close()

    data_dict = {
        "data": data,
        "columns": ['code', 'brand', 'type', 'model', 'price', 'year']
    }

    return data_dict

def data_init():
    os.remove(db)
    
    create_table('users', ['name', 'is_admin', 'pass'], ['varchar(30)', 'integer', 'varchar(255)'])
    create_table('vehicle_brand', ['name'], ['varchar(30)'])
    create_table('vehicle_type', ['name', 'brand_id'], ['varchar(30)', 'integer'], ['brand_id'], ['vehicle_brand'])
    create_table('vehicle_model', ['name', 'type_id'], ['varchar(30)', 'integer'], ['type_id'], ['vehicle_type'])
    create_table('vehicle_year', ['year'], ['integer'])
    create_table('pricelist', ['code', 'price', 'year_id', 'model_id'], ['varchar(30)', 'integer', 'integer', 'integer'], ['year_id', 'model_id'], ['vehicle_year', 'vehicle_model'])
    
    pass1 = hashlib.sha256(b'the1stpass').hexdigest()
    pass2 = hashlib.sha256(b'admin2pwd').hexdigest()

    users = [['admin1', 1, pass1], ['admin2', 0, pass2]]
    brands = [['Honda'], ['Toyota'], ['Mitsubishi']]
    types = [['Vario', 1], ['Spacy', 1], ['Avanza', 2], ['Pajero', 3]]
    models = [['125cc', 1], ['2014', 2], ['MPV', 2], ['SUV', 4], ['250cc', 1], ['MPV', 3]]
    years = [[2014], [2015], [2016], [2017]]

    pricelists = [[generateCode(1,1), 9999999, 1, 1], [generateCode(1,2), 8888888, 1, 2]]

    insert_data_init(users, 'users', ['name', 'is_admin', 'pass'])
    insert_data_init(brands, 'vehicle_brand', ['name'])
    insert_data_init(types, 'vehicle_type', ['name', 'brand_id'])
    insert_data_init(models, 'vehicle_model', ['name', 'type_id'])
    insert_data_init(years, 'vehicle_year', ['year'])
    insert_data_init(pricelists, 'pricelist', ['code', 'price', 'year_id', 'model_id'])

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
            if get_userAuthr(decoded["username"])[0] == 0:
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

        join_result = inner_join()

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

        join_result = inner_join(query = args['q'].capitalize(), by = args['b'])
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
        insert_data_init([args['data']], 'pricelist', args['columns'])

        return jsonify({"message": "Input Success!"})

class Authentication(Resource):
    def get(self):
        parser.add_argument('Username', location = 'headers')
        parser.add_argument('Password', location = 'headers')

        args = parser.parse_args()

        passq = hashlib.sha256(bytes(args['Password'], 'utf-8')).hexdigest()

        if args['Password'] == None or passq != get_userpw(args['Username'])[0]:
            return jsonify({"message": "Authentication error"}, 401)
        else:
            payload = {
                "username": args["Username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
            }
            jwt_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({"token": jwt_token})

api.add_resource(VehicleApp, '/api')
api.add_resource(GetAll, '/api/all')
api.add_resource(Search, '/api/search')
api.add_resource(Authentication, '/api/login')
api.add_resource(InputPrice, '/api/input_price')

data_init()

if __name__ == '__main__':
    app.run(debug=True,)
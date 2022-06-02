import sqlite3
import os


db = os.path.dirname(__file__) + '\\vehicle_db.db'

def remove_db():
    os.remove(db)

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
    
def update_data(column_update, dataupdate, table, column_cond, datacond):
    columns = get_columns(table)

    columnupdate = []
    columncond = []
    for i in column_update:
        for j in columns:
            if i == j[1]:
                columnupdate.append(i)
                
    for i in column_cond:
        for j in columns:
            if i == j[1]:
                columncond.append(i)

    data = []
    for i in dataupdate:
        data.append(i)
    for i in datacond:
        data.append(i)

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    sql = "UPDATE " + table + " SET "
    for i in range(0, len(columnupdate)):
        sql += columnupdate[i] + "=?"
        if i < len(columnupdate)-1:
            sql += ","

    sql += ' WHERE '
    for i in range(0, len(datacond)):
        sql += columncond[i] + "=?"
        if len(datacond) > 1:
            if i < len(datacond)-1:
                sql += " AND "
    
    print(sql)
    cur.execute(sql, tuple(data))
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

def delete_by_id(id):
    sql = "DELETE FROM pricelist WHERE id=?"
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    conn.close()

def check_if_exist(table, column_cond, datacond):
    sql = "SELECT * FROM " + table + " WHERE "
    for i in range(0, len(column_cond)):
        sql += column_cond[i] + "=?"
        if i < len(column_cond)-1:
            sql += " AND "
    
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql, tuple(datacond))
    data = cur.fetchall()
    conn.close()

    if len(data) == 0:
        return False
    return True

def placeholder():
    pass
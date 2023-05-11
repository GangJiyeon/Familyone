from flask import jsonify
import pymysql
from py.config import dbconn

# mysql 연결
def db_connector():

    db = pymysql.connect(
                        host=dbconn.host, 
                        port=dbconn.port, 
                        user=dbconn.user, 
                        passwd=dbconn.passwd, 
                        db=dbconn.db 
                        #charset='utf8'
                        )
    
    print("mysql 연결")

    
    return db

def db_select_by_q(query):
    db = db_connector()
    cursor = db.cursor(pymysql.cursors.DictCursor)  # return type => dictionary
    cursor.execute(query)            
    result = cursor.fetchall()
    return result

def select_by_qNd(query, data):

    result = ""
    db = db_connector()
    cursor = db.cursor(pymysql.cursors.DictCursor)  # return type => dictionary
    cursor.execute(query, data)         
    if(cursor.rowcount == 0 or cursor.rowcount == -1):
        result = "null"
        return result
    else:
        result = cursor.fetchall()
        return result

    
    
    
    

def select_by_qNd_notDic(query, data):
    db = db_connector()
    cursor = db.cursor()  # return type => dictionary
    cursor.execute(query, data)            
    result = cursor.fetchall()
    return result

def db_select_by_q2(query):
    db = db_connector()
    cursor = db.cursor()  # return type => dictionary
    cursor.execute(query)            
    result = cursor.fetchall()
    return result

def db_else_by_q(query, data):
    db = db_connector()
    cursor = db.cursor()
    cursor.execute(query, data)
    db_close(db)

def db_else_by_q_all(query, data):
    db = db_connector()
    cursor = db.cursor()
    cursor.executemany(query, data)
    db_close(db)

def db_close(db):
    db.commit()
    db.close()
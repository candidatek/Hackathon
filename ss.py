from __future__ import print_function # In python 2.7
from flask import Flask, redirect, url_for, session, request, jsonify ,render_template
from flask_oauthlib.client import OAuth
from flask_mysqldb import MySQL
from base64 import b64encode
import json
import datetime , uuid
import smtplib
import sys
import config
import yaml
import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mysql = MySQL(app)

@app.route('/')
def first():
    return render_template('ask.html')

@app.route('/ask')
def ask():
    print("ASK")
    username = session['ss']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE scholar SET viva = 'REQUEST' WHERE username = %s " ,[username])
    cur.connection.commit()
    cur.execute("SELECT id ,gid , name , username , viva FROM scholar WHERE username = %s ", [username])
    jdata = cur.fetchone()
    print(jdata)
    return jsonify(jdata)

@app.route('/slogin' , methods=['GET', 'POST'])
def slogin():
    if request.method == 'POST':
        frm = request.form
        cur = mysql.connection.cursor()
        username = frm['susername']
        password = frm['spassword']
        print(username)
        cur.execute("SELECT password FROM scholar WHERE username = %s ", [username])
        passcheck = cur.fetchone()[0]
        if password == passcheck :
            session['ss'] = username
            cur.execute("SELECT name FROM scholar WHERE username = %s ", [username])
            name = cur.fetchone()[0]
            if name == None:
                return render_template('sdetails.html')
            return render_template('inter.html')
        else :
            return 'Wrong Combination'
    return render_template('slogin.html')


@app.route('/glogin' , methods =['GET' , 'POST'])
def glogin():
    if request.method == 'POST' :
        frm = request.form
        cur = mysql.connection.cursor()
        username = frm['gusername']
        password = frm['gpassword']
        cur.execute("SELECT password FROM guide WHERE username = %s ", [username])
        passcheck = cur.fetchone()[0]
        if password == passcheck :
            session['gusername'] = username
            return render_template('adds.html')
        else :
            return 'Failed'
    return render_template('glogin.html')


@app.route('/addscholar' , methods=['GET' , 'POST'])
def addscholar():
    #try:
    #    gusersession = session['gusername']
    #except:
    #    return render_template('index.html')
    if request.method == 'POST':
        gusersession = session['gusername']
        frm = request.form
        cur = mysql.connection.cursor()
        suname = frm['suname']
        spass = frm['spassword']
        cur.execute("SELECT id FROM guide WHERE guide.username = %s ", [gusersession])
        gid = cur.fetchone()
        id = str(uuid.uuid4().fields[-1])[:4]
        cur.execute("INSERT INTO scholar(username , password , gid , id ) VALUES (%s , %s , %s , %s )" , [suname , spass , gid , id])
        cur.connection.commit()
        return 'true'
    return 'ERROR'

@app.route('/addtopic',methods = ['GET','POST'])
def addtopic():
    cur = mysql.connection.cursor()
    name = request.args.get('sname')
    topic = request.args.get('stopic')
    topicid = request.args.get('stopicid')
    dob = request.args.get('age')
    sub1 = request.args.get('s1')
    sub2  = request.args.get('s2')
    sub3 = request.args.get('s3')
    sub4 = request.args.get('s4')
    username = session['ss']
    cur.execute("UPDATE scholar SET name = %s , DOB = %s WHERE username = %s " ,[name ,  dob , username ])
    cur.connection.commit()
    cur.execute("SELECT id FROM scholar WHERE username = %s ", [username])
    id = cur.fetchone()[0]
    cur.execute("INSERT INTO acadamics (sid , subid) VALUES(%s , %s) " ,[id , sub1])
    cur.execute("INSERT INTO acadamics (sid , subid) VALUES(%s , %s) " ,[id , sub2])
    cur.execute("INSERT INTO acadamics (sid , subid) VALUES(%s , %s) " ,[id , sub3])
    cur.execute("INSERT INTO acadamics (sid , subid) VALUES(%s , %s) " ,[id , sub4])
    cur.connection.commit()
    return render_template('ask.html')


if __name__ == '__main__':

    app.run(debug=True)

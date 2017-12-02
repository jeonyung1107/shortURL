from __future__ import with_statement
from contextlib import closing
from urllib.parse import urlparse
import os
import sqlite3
from string import digits, ascii_lowercase,ascii_uppercase
from flask import Flask,request,g,url_for,abort,render_template,flash, redirect
import validators
import base64
import random

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'short.db'),
    SECRET_KEY='hello',
    USERNAME='admin',
    PASSWORD='admin'
))
@app.route('/',methods =['POST','GET'])
def input_long():
    error = None
    shorted = None
    if request.method =='POST':

        url = str.encode(request.form.get('url'))
        if url==None:
            error = 'URL을 입력해 주십시오.'
        else:
            url = checkURL(url)

            if url == None:
                error = 'URL이 형식에 맞는지 확인해 주십시오.'
                return render_template('main.html',error=error,shorted=shorted)

            cur = g.db.cursor().execute('select id from entries where long=?',[base64.urlsafe_b64encode(url)])
            id = cur.fetchone()

            if id ==None:
                cur.execute('insert into entries(long) values(?)',
                            [base64.urlsafe_b64encode(url)])
                g.db.commit()
                id = cur.lastrowid
            else:
                id = id[0]

            shorted ='localhost:5000/'+ encodeURL(id)


    return render_template('main.html',error=error,shorted=shorted)

@app.route('/<url>')
def redirectForShort(url):
    decoded = decodeURL(url)
    cur = g.db.cursor().execute('select long from entries where id=?',[decoded])

    try:
        long = cur.fetchone()[0]
        if long is not None:
            url = base64.urlsafe_b64decode(long)
    except Exception as e:
        print(e)
    return redirect(url)

@app.route('/test/<url>')
def url_test(url):
    cur = g.db.cursor().execute('select short from entries where long=?',[url])

    short = cur.fetchone()
    if short is not None:
        short = short[0]

    return render_template('test.html',long=url,short = short)


def checkURL(URL):
    url = URL.decode('utf-8')
    if urlparse(url).path !='' or urlparse(url).netloc !='':
        if urlparse(url).scheme=='':
            url = 'http://' + url
        return str.encode(url)
    else:
        return None

def encodeURL(ID):
    base = digits + ascii_lowercase + ascii_uppercase
    result = ''

    while True:
        mod = ID%62
        ID = ID//62
        result = base[mod] + result

        if not ID:
            break

    return result

def decodeURL(short):
    base = digits + ascii_lowercase + ascii_uppercase

    result = 0
    for i in range(len(short)):
        result = result*62 + base.find(short[i])

    return result

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_reqest():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql','r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    app.run()

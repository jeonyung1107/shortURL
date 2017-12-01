from __future__ import with_statement
from contextlib import closing
from urllib.parse import urlparse
import os
import sqlite3
import string
from string import ascii_lowercase,ascii_uppercase
from flask import Flask,request,g,url_for,abort,render_template,flash, redirect
import base64

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
            if url != None:
                shorted = encodeURL(url)
            else:
                shorted = '다시 입력해주십시오'

        cur = g.db.excute('select long from entries where long=?',(url))
        if cur.fetchone() ==None:
            cur.execute('insert into entries(long) values(?)',
                        (base64.urlsafe_b64encode(url)))
    return render_template('main.html',error=error,shorted=shorted)

@app.route('/<url>')
def redirectForShort(url):
    decoded = decodeURL(url)
    cur = g.db.excute('select long from entries where id=?',(decoded))

    try:
        long = cur.fetchone()
        if long is not None:
            url = base64.urlsafe_b64decode(long)
    except Exception as e:
        print(e)
    return redirect(url)

def checkURL(URL):
    url = URL
    if urlparse(url).netloc !='':
        if urlparse(url).scheme=='':
            url = 'http://' + url
        return url
    else:
        return None

def encodeURL(ID):
    base = string.digits + ascii_lowercase + ascii_uppercase
    result = ''

    while True:
        mod = ID%62
        ID = ID//62
        result = base[mod] + result

        if not ID:
            break

    return result

def decodeURL(short):
    base = string.digits + ascii_lowercase + ascii_uppercase

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
    init_db()
    app.run()

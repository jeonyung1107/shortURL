from __future__ import with_statement
from urllib.parse import urlparse
from string import digits, ascii_lowercase,ascii_uppercase
from flask import Flask,request,g,url_for,render_template, redirect
import os,base64,sqlite3,requests

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
    '''
    메인 페이지
    URL입력을 받는다.
    함수들이 실제로 적용되는 부분이다.
    :return:
    '''
    error = None
    shorted = None
    if request.method =='POST':

        url = str.encode(request.form.get('url'))

        #URL이 입력되지 않은 경우
        if url==None:
            error = 'URL을 입력해 주십시오.'
        else:
            #URL이 입력된 경우 제대로된 URL인지 확인한다.
            url = checkURL(url)

            #확인한 URL이 제대로 된 형식이 아닌 경우
            if url == None:
                error = 'URL이 형식에 맞는지 확인해 주십시오.'
                return render_template('main.html',error=error,shorted=shorted)

            #입력된 URL이 DB에 저장되어 있는지 확인한다.
            cur = g.db.cursor().execute('select id from entries where long=?',[base64.urlsafe_b64encode(url)])
            id = cur.fetchone()

            #DB에 URL이 없는 경우 새로 저장한다.
            if id ==None:
                cur.execute('insert into entries(long) values(?)',
                            [base64.urlsafe_b64encode(url)])
                g.db.commit()
                id = cur.lastrowid
            else:
                id = id[0]

            #변환된 URL
            shorted ='localhost:5000/'+ encodeURL(id)

    return render_template('main.html',error=error,shorted=shorted)

@app.route('/<url>')
def redirectForShort(url):
    '''
    주어진 짧은 URL에 해당하는 원래의 URL로 연결해주는 함수
    decodeURL을 호출하여 짧은 URL을 ID로 변환한다.
    ID에 해당하는 URL을 찾아 연결한다.
    :param url:
    :return:
    '''
    if url == 'favicon.ico':
        return redirect(url_for('input_long'))

    #짧은 URL을 원래의 ID로 변환후 해당하는 URL을 찾는다.
    decoded = decodeURL(url)
    cur = g.db.cursor().execute('select long from entries where id=?',[decoded])

    try:
        long = cur.fetchone()[0]
        if long is not None:
            #인코딩 되었던 URL을 원래의 형태로 돌린다.
            url = base64.urlsafe_b64decode(long)
    except Exception as e:
        print(e)
    return redirect(url)


def checkURL(URL):
    '''
    URL이 제대로 입력되었는지 체크하는 함수
    URL의 형태를 확인하고, 수정된 URL로 접속 후 에러가 나는지 확인한다.
    :param URL: 바이트로 변환된 URL
    :return: scheme이 붙은 URL을 반환한다. 만약 제대로된 URL이 아닐 경우 None
    '''
    url = URL.decode('utf-8')
    #URL이 제대로 된 형태를 갖추었는지 확인한다.
    if urlparse(url).path !='' or urlparse(url).netloc !='':
        if urlparse(url).scheme=='':
            url = 'http://' + url
            try:
                #변환된 URL이 실제로 접속 가능한지 확인한다.
                req = requests.get(url)
            except Exception as e:
                print(e)
                return None
        return str.encode(url)
    else:
        return None

def encodeURL(ID):
    '''
    주어진 ID를 이용하여 짧은 주소 생성
    62진법으로 변환하는 원리를 이용한다.
    :param ID:
    :return:
    '''
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
    '''
    주어진 짧은 주소를 이용하여 원래의 ID 반환
    진법 변환의 원리를 이용한다.
    :param short:
    :return:
    '''
    base = digits + ascii_lowercase + ascii_uppercase

    result = 0
    for i in range(len(short)):
        result = result*62 + base.find(short[i])

    return result

def connect_db():
    '''
    설정에 따라 데이터베이스 연결
    :return:
    '''
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_reqest():
    '''
    요청시 데이터베이스 연결
    :return:
    '''
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    '''
    요청 이후 데이터베이스 연결 해제
    :param exception:
    :return:
    '''
    g.db.close()

if __name__ == '__main__':
    app.run()

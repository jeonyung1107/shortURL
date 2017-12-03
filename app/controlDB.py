import  sqlite3, os

dbPass = os.getcwd() + '/short.db'

def connect_db():
    return sqlite3.connect(dbPass)

def init_db():
    '''
    DB 생성하는 함수
    :return:
    '''
    with connect_db() as db:
        with open('schema.sql','r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def checkDB():
    with connect_db() as db:
        cur = db.cursor()
        cur.execute('select * from entries')
        res = cur.fetchall()
        if res is None:
            print ('nothing')
        else:
            print(cur.fetchall())

if __name__ == '__main__':
    init_db()
    checkDB()

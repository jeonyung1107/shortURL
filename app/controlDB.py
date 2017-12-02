from string import digits ,ascii_uppercase, ascii_lowercase
import random, base64, sqlite3

def makeTest():
    urlList=[]
    base = digits + ascii_lowercase + ascii_uppercase
    while len(urlList) <10000:
        urlTmp = ''
        for i in range(20):
            urlTmp = urlTmp + base[random.randrange(0,62)]

        urlTmp = str.encode('localhost:5000/test/'+urlTmp)
        urlList.append([base64.urlsafe_b64encode(urlTmp)])

    with sqlite3.connect('short.db') as conn:
        cur = conn.cursor()
        res = cur.executemany('insert into entries(long) values(?)',urlList)
        conn.commit()

if __name__ == '__main__':
    makeTest()

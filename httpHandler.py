import os
import urllib
import urllib2
from BaseHTTPServer import HTTPServer , BaseHTTPRequestHandler
import time
import sqlite3
import hashlib
import thread

import dataAnalysis

incrementDone = True

def md5(string) :
        hasher = hashlib.md5()
        hasher.update(string.lower())
        return hasher.hexdigest().lower()


def titleLessQuery(url) :
        title = urllib.unquote(url.split('&')[0].split('=')[1]).strip()
        artist = urllib.unquote(url.split('&')[1].split('=')[1]).strip()
        album = urllib.unquote(url.split('&')[2].split('=')[1]).strip()
        genre = urllib.unquote(url.split('&')[3].split('=')[1]).strip()
        year = urllib.unquote(url.split('&')[4].split('=')[1]).strip()
        con = sqlite3.connect('Data.db')
        con.text_factory = str 
        cur = con.cursor()
        ids = []
        key = [title,artist,album,genre,year]
        KEY = ['title','artist','album','genre','year']
        for i in range(len(key)) :
                if key[i] == '' :
                        pass
                else :
                        sql = 'SELECT id FROM Data WHERE ' + KEY[i] + ' LIKE ? '
                        cur.execute(sql,('%' + key[i] +'%',))
                        ids.append(cur.fetchall())
        init = set(ids[0])
        for i in range(1,len(ids)) :
                init = init.intersection(set(ids[i]))
        init = list(init)[:40]
        results = []
        for Id in init :
                sql = 'SELECT * FROM Data where id = ?'
                cur.execute(sql,(Id[0],))
                results.append(cur.fetchall()[0])
        content = '''<br><table border="1" style="width:100%; height:auto"><tr><td width="5%"></td><td width="25%"><h2>Title<h/2></td><td width="25%"><h2>Artist</h2></td>
                        <td width="25%"><h2>Album</h2></td><td width="8%"><h2>Genre</h2></td><td width="7%"><h2>Year</h2></td><td width="5%"><h2>Played</h2></td></tr>'''
        for item in results :
                content += '<tr><th><button id="playButton" data-value="' + item[0] + '">Play</button></th>'
                sub = [1,2,3,4,5,7]
                for i in range(len(sub)) :
                        content += '<td>'                        
                        if str(sub[i]) == '###' :
                                content+= 'data not available'
                        else :
                                content += str(item[sub[i]])
                        content += '</a></td>'
                content += '</tr>'
        content += '</table>'
        return content

def processQuery(url) :
        title = urllib.unquote(url.split('&')[0].split('=')[1]).strip()
        artist = urllib.unquote(url.split('&')[1].split('=')[1]).strip()
        album = urllib.unquote(url.split('&')[2].split('=')[1]).strip()
        genre = urllib.unquote(url.split('&')[3].split('=')[1]).strip()
        year = urllib.unquote(url.split('&')[4].split('=')[1]).strip()
        
        tokens = title.split(' ')
        if title == '':
                if artist == '' and album == '' and genre == '' and year == '' :
                        content = '''<br><table border="1" style="width:100%; height:auto"><tr><td width="5%"></td><td width="25%"><h2>Title<h/2></td><td width="25%"><h2>Artist</h2></td>
                                <td width="25%"><h2>Album</h2></td><td width="8%"><h2>Genre</h2></td><td width="7%"><h2>Year</h2></td><td width="5%"><h2>Played</h2></td></tr></table>'''
                else  :
                        content = titleLessQuery(url)
        else :
                IdList = []
                for token in tokens :
                        #print os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])),md5(str(len(token))))+'.db'
                        con = sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])),md5(str(len(token))))+'.db')
                        con.text_factory = str
                        cur = con.cursor()
                        sql = 'SELECT id FROM Data WHERE pattern = ?'
                        cur.execute(sql,(token.lower(),))
                        temp = cur.fetchall()                
                        IdList.append([ str(i[0]) for i in temp])        
                IdSet = set(IdList[0])
                for List in IdList[1:] :
                        IdSet = IdSet.intersection(set(List))
                IdList = list(IdSet)        
                Results = []
                key = [artist,album,genre,year]
                KEY = ['artist','album','genre','year']
                filteredId = []
                results = []
                for Id in IdList :
                        ids = []
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
                        cur = con.cursor()
                        try :
                                for i in range(len(key)) :
                                        if key[i] == '' :
                                                pass
                                        else :
                                                sql = 'SELECT id FROM Data WHERE ' + KEY[i] + ' LIKE ? AND id =?'
                                                cur.execute(sql,('%' + key[i] +'%',Id))
                                                ids.append([ str(i[0]) for i in cur.fetchall()])
                                init = set(ids[0])                
                                for i in range(1,len(ids)) :
                                        init = init.intersection(set(ids[i]))
                                filteredId += list(init)
                        except IndexError :
                                sql = 'SELECT id FROM Data WHERE id =?'
                                cur.execute(sql,(Id,))
                                ids.append([ str(i[0]) for i in cur.fetchall()])                        
                                filteredId += list(ids[0])
                for Id in filteredId :
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
                        con.text_factory = str
                        cur = con.cursor()        
                        sql = 'SELECT * FROM Data where id = ?'
                        cur.execute(sql,(Id,))
                        results += cur.fetchall()
                content = '''<br><table border="1" style="width:100%; height:auto"><tr><td width="5%"></td><td width="25%"><h2>Title<h/2></td><td width="25%"><h2>Artist</h2></td>
                                <td width="25%"><h2>Album</h2></td><td width="8%"><h2>Genre</h2></td><td width="7%"><h2>Year</h2></td><td width="5%"><h2>Played</h2></td></tr>'''
                for item in results :
                        content += '<tr><th><button id="playButton" data-value="' + item[0] + '">Play</button></th>'
                        sub = [1,2,3,4,5,7]
                        for i in range(len(sub)) :
                                content += '<td>'                        
                                if str(sub[i]) == '###' :
                                        content+= 'data not available'
                                else :
                                        content += str(item[sub[i]])
                                content += '</a></td>'
                        content += '</tr>'
                content += '</table>'
        return content

IncrementStatus = False

def playId(url) :
        global IncrementStatus
        IncrementStatus = False
        Id = url.split('=')[1].strip()        
        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
        con.text_factory = str
        cur = con.cursor()        
        sql = 'SELECT * FROM Data WHERE id LIKE ?'        
        cur.execute(sql,('%'+Id+'%',))   
        result = cur.fetchall()
        print result
        played = result[0][7]        
        played += 1        
        sql = 'UPDATE Data SET played = ? WHERE id = ?'
        cur.execute(sql,(played,Id))
        con.commit()
        con.close()
        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
        con.text_factory = str
        cur = con.cursor()        
        sql = 'SELECT * FROM Data WHERE id LIKE ?'        
        cur.execute(sql,('%'+Id+'%',))
        result = cur.fetchall()                
        os.system('"'+ result[0][6] +'"')
        return str(result[0][6])
        
def getIncrementStatus() :
        global IncrementStatus
        return IncrementStatus

class handler(BaseHTTPRequestHandler) :

        def do_GET(self) :
                print self.client_address[0]+self.path 
                if 'fetchRecord' in self.path :
                        content = processQuery(self.path)
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)
                elif 'playId' in self.path :
                        reqPath = playId(self.path)
                        self.send_response(200)                        
                        content = '<html></html>'
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)                        
                elif '.js' in self.path :                        
                        with open(self.path[1:],'r') as f :
                                content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)
                #elif 'data' in self.path :
                 #       getVars = self.path.split('?')[1].split('&')
                #      VisualOn = getVars[0].split('=')[1].strip()
                #        VisualType = getVars[1].split('=')[1].strip()
                 #       content = dataAnalysis.getHTML(VisualOn,VisualType)                        
                  #      self.send_response(200)
                   #     self.send_header('Content-type','text/html')
                    #    self.end_headers()
                     #   self.wfile.write(content)

                elif 'fetchtrackdata' in self.path :
                        Id = self.path.split('=')[1]
                        con = sqlite3.connect('Data.db')
                        cur = con.cursor()
                        sql = 'SELECT * FROM Data WHERE id = ?'
                        cur.execute(sql,(Id,))
                        record = cur.fetchall()[0]
                        with open(record[6],'rb') as f :
                                content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)
                else :
                        try :
                                with open(self.path[1:].split('?')[0]+'.html','r') as f :
                                        content = f.read()
                        except IOError :
                                content = '<html><body><h1>Page not found</h1></body></html>'
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)


        def log_request(self, code=None, size=None):
                pass

        def log_message(self, format, *args):
                pass

def openHome(CLIENT_PORT) :
        time.sleep(2)
        with open('startup.html','w') as f :
                f.write('<script type="text/javascript">window.location = "http://localhost:'+str(CLIENT_PORT)+'/home";</script>')
        os.system('start startUp.html')

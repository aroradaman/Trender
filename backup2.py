from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import sqlite3
import glob
import unicodedata
import os
import thread
import re
from operator import itemgetter
import hashlib
from mutagen.mp3 import MP3
import time
import unicodedata
from BaseHTTPServer import HTTPServer , BaseHTTPRequestHandler
import urllib
import subprocess
PORT = 5000
parentDir =r'C:\python\trend'
os.chdir(parentDir)
shared = [r'C:\Users\Daman Arora']
#shared = ['/home']
hasher = hashlib.md5()
incrementDone = True
done = False
def md5(string) :
        hasher = hashlib.md5()
        hasher.update(string.lower())
        return hasher.hexdigest().lower()

def dataIndexer(Id,title) :
        for token in title.split(' ') :
                        if token.isalpha() :
                                if len(token) >= 1 :
                                        for i in range(1,len(token)+1) :
                                                #print os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token[0])),md5(str(i)))+'.db',token,i,token[:i],Id
                                                con = sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token[0])),md5(str(i)))+'.db')
                                                cur = con.cursor()                        
                                                sql = 'CREATE TABLE IF NOT EXISTS Data ( pattern varchar(100), id varchar(100))'
                                                cur.execute(sql)
                                                sql = ' SELECT * FROM Data WHERE pattern= ? AND id = ?'
                                                cur.execute(sql,(token[:i],Id))
                                                if len(cur.fetchall()) == 0 :
                                                        con.commit()
                                                        sql = 'INSERT INTO Data VALUES (?,?)'
                                                        cur.execute(sql,(token[:i].lower(),Id))
                                                        con.commit()
                                                        con.close()

def idIndexer(dataSet) :
                con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1]))+'/Data.db')
                con.text_factory = str
                cur = con.cursor()
                sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) , played int)'
                cur.execute(sql)
                sql = 'SELECT * FROM Data WHERE id = ?'
                cur.execute(sql,(dataSet[0],))
                if len(cur.fetchall())== 0 :
                       sql = 'INSERT INTO Data VALUES (?,?,?,?,?,?,?,?)'
                       cur.execute(sql,tuple(dataSet))
                       con.commit()
                       con.close()
                        
def uni(File) :
        try :
                return unicodedata.normalize('NFKD',File).encode('ascii','ignore')
        except TypeError :
                return File

def getTags(path) :
        craps = [' - www.Songs.PK','(williswho.com)' ,'www.downloadming.com','DownloadMing.Com','www.Songs.Pk','www.Songs.PK','(www.SongsLover.com)','www.SongsLover.com','(MyMp3Singer.com)',' - www.SongsLover.com',' - MyMp3Singer.com','DownloadMing.SE','MyMp3Singer.com',' - DJMaza.Info',' - www.DJMaza.Com','[2013-Mp3-320kbps]',' - www.Songs.PK',' @ SongsDL.com','SongsDL.com','www.freshnewtracks.com','www.RnBXclusive.com',' - www.GRIZZLIS.LT','www.Webmusic.IN',' [www.DJLUV.in]',' - www.SongsLover.pk','www.Songs.PK','www.Songs.PK','--[CooL GuY] {{a2zRG}}','[Full-Movie-Album]',' SongsLover.pk ','SongsLover.pk','[CooL GuY] {{a2zRG}} [2013-Mp3-320kbps] [Full-Movie-Album]','DownloadMing.Com','- DownloadMing.Com',' - DownloadMing.Com','www.sites.google.com/site/ring2mobile/','rnb-lounge.6x.to','..:: www.x-raid.nu ::..','www.x-raid.nu','[Want3d]','www.DJMaza.Com',' - www.DJMaza.Com']
        craps = list(set(craps))
        Tags = []
        try :
                tags = EasyID3(path)
        except ID3NoHeaderError :
                tags = { 'title' : '###' , 'artist' : '###' , 'album' : '###' , 'genre' : '###', 'date' : '###'}
        for tag in ['title','artist','album','genre','date'] :
                try :
                        tAg = tags[tag][0]
                        Tags.append(tAg)
                except KeyError :
                        Tags.append('###')
        for index in range(len(Tags)) :
                temp = []
                for crap in craps :
                        if crap in Tags[index] :
                                temp.append(crap)
                temp = map ( lambda x : [x,len(x)], temp)
                temp = sorted(temp,key=itemgetter(1))
                if temp == [] :
                        Tags[index] = Tags[index].strip()
                else :
                        Tags[index] = Tags[index].replace(temp[-1][0],'').strip()        
        return Tags

def idGenerator(path,title) :           
        string = title.strip() + str( MP3(path).info.length )
        return md5(string)
        
def handleData( pathList ) :
        global done
        con = sqlite3.connect('Data.db')
        con.text_factory = str
        cur = con.cursor()
        for path in pathList :
                tags = getTags(path)
                for i in range(len(tags)) :
                        tags[i] = uni(tags[i])
                Id = idGenerator(path,tags[0])
                sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) , played int)'
                cur.execute(sql)
                sql = 'SELECT * FROM Data WHERE id = ?'
                cur.execute(sql,(Id,))
                ret = cur.fetchall()
                if len(ret) == 0 :
                        sql = 'INSERT INTO Data VALUES (?,?,?,?,?,?,?,?)'
                        cur.execute(sql,(Id,uni(tags[0]),uni(tags[1]),uni(tags[2]),uni(tags[3]),uni(tags[4]),path,0))
                        con.commit()
                        thread.start_new_thread(dataIndexer,(Id,uni(tags[0])))
                        thread.start_new_thread(idIndexer,([Id,uni(tags[0]),uni(tags[1]),uni(tags[2]),uni(tags[3]),uni(tags[4]),path,0],))
        con.close()
        done = True

def scanner(dir_) :
        over = False
        while not over :
                contents =  glob.glob(dir_)
                mp3 = [ path for path in contents if path[-4:] == '.mp3']
                handleData(mp3)
                dirs = [ path for path in contents if os.path.isdir(path)]
                #for item in dirs :
                #       print item
                if len(dirs) == 0 :
                        over = True
                dir_ += '/*'

def removePatterns(Id,title) :
        tokens = title.split(' ')
        for token in tokens :
                if len(token) >= 1 :
                        for i in range(1,len(token)+1) :                                
                                con = sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token.lower() [0])),md5(str(i)))+'.db')
                                cur = con.cursor()
                                sql = 'DELETE FROM Data WHERE id = ?'
                                cur.execute(sql,(Id,))
                                con.commit()
                                con.close()

def updateData() :
        var = list('0123456789ABCDEF')
        for inner in var :
                for outer in var :
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(outer)),md5(inner))+'/Data.db')                                
                        con.text_factory = str
                        cur = con.cursor()
                        try :
                                sql = 'SELECT * FROM Data'
                                cur.execute(sql)
                                con.commit()
                                Data = cur.fetchall()
                                for item in Data :                                        
                                        if not os.path.exists(str(item[6])) :
                                                thread.start_new_thread(removePatterns,(str(item[0]),str(item[1])))
                                                print str(item[6])
                                                sql = 'DELETE FROM Data WHERE id LIKE ?'
                                                cur.execute(sql,('%'+str(item[0])+'%',))
                                                con.commit()
                                                
                        except sqlite3.OperationalError :
                                sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) ,played int)'
                                cur.execute(sql)
                                con.commit()
        Data = cur.fetchall()
        for track in Data :
                if not os.path.exists(track[6]) :
                        sql = 'DELETE FROM Data WHERE id = ?'
                        cur.execute(sql,(track[0],))
                        con.commit()
        con.close()
        time.sleep(1)
        thread.start_new_thread(updateData,())

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
                        #print os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token[0])),md5(str(len(token))))+'.db'
                        con = sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token[0])),md5(str(len(token))))+'.db')
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
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
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
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
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

def getincrementDone() :
        global incrementDone
        return incrementDone

def playId(url) :
        global incrementDone
        Id = url.split('=')[1].strip()
        incrementDone = False
        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(Id[0])),md5(Id[1]))+'/Data.db')
        cur = con.cursor()
        sql = 'SELECT * FROM Data WHERE id LIKE ?'        
        cur.execute(sql,(Id,))   
        result = cur.fetchall()
        played = result[0][7]
        played += 1        
        sql = 'UPDATE Data SET played = ? WHERE id = ?'
        cur.execute(sql,(played,url.split('=')[1].strip()))
        con.commit()
        con.close()
        incrementDone = True        
        getincrementDone()
        os.system('"'+ result[0][6] +'"')
        

class handler(BaseHTTPRequestHandler) :

        def do_GET(self) :
                #print self.path[1:]
                if 'fetchRecord' in self.path :
                        content = processQuery(self.path)
                        self.send_response(200)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(content)
                elif 'playId' in self.path :
                        thread.start_new_thread(playId,(self.path,))
                        while True :
                                incrementDone = getincrementDone()
                                if incrementDone :
                                        break
                        self.send_response(200)
                elif 'jquery.min.js' in self.path :
                        with open('jquery.min.js','r') as f :
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

def openHome() :
        time.sleep(2)
        with open('startup.html','w') as f :
                f.write('<script type="text/javascript">window.location = "http://localhost:'+str(PORT)+'/home";</script>')
        os.system('start startUp.html')

def findMusic(shared) :
        while True :
                for path in shared :
                        scanner(path)
                time.sleep(2)
                
###############################################################
###############################################################

os.chdir(parentDir)

try :                
        os.mkdir('data')
        abcd = list('QWERTYUIOPASDFGHJKLZXCVBNM')
        for token in abcd :
                try :
                        os.mkdir(os.path.join(os.path.join(parentDir,'data'),md5(token[0])))
                except WindowsError :
                        pass
                for count in range(1,16):
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'data'),md5(token[0])),md5(str(count))+'.db'))
                        con.close()
except WindowsError :
        pass

try :                
        os.mkdir('tracer')
        var = list('0123456789ABCDEF')
        for outer in var :
                try :
                        os.mkdir(os.path.join(os.path.join(parentDir,'tracer'),md5(outer)))
                except WindowsError :
                        pass
                for inner in var:
                        try :
                                os.mkdir(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(outer)),md5(inner)))
                        except WindowsError :
                                pass
                        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(parentDir,'tracer'),md5(outer)),md5(inner))+'/Data.db')
                        con.close()
except WindowsError :
        pass

thread.start_new_thread(updateData,())
thread.start_new_thread(findMusic,(shared,))
thread.start_new_thread(openHome,())
server = HTTPServer(('',PORT),handler)
server.serve_forever()

###############################################################
###############################################################

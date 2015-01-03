import os
import sqlite3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import glob
import unicodedata
from operator import itemgetter
import hashlib
from mutagen.mp3 import MP3
import time
import subprocess
import thread
import calendar

try :
    os.mkdir('data')
except :
    pass
try :
    os.mkdir('tracer')
except :
    pass    
shared = ['/home']

def md5(string) :
    hasher = hashlib.md5()
    hasher.update(string.lower())
    return hasher.hexdigest().lower()

def getPathTime(path) :
    months = dict((v,str(k)) for k,v in enumerate(calendar.month_abbr))
    sList = time.ctime(os.path.getctime(path)).split(' ')
    if len(months[sList[1]]) == 1 :                
        cTime = sList[4] + '0' + months[sList[1]] + sList[2]
    else :
        cTime = sList[4] + months[sList[1]] + sList[2]        
    return cTime

def uni(File) :
    try :
        return unicodedata.normalize('NFKD',File).encode('ascii','ignore')
    except TypeError :
        return File
                
def getTags(path) :
    craps = [' - www.Songs.PK','mp3sansar.blogspot.com','www.FulFun.com','www.doregama.com','www.robsonmichel.blogspot.com','g.ortha.ii@ferialaw.com','<Unknown>','MastiMaza.com','[www.Djluv.net]','(williswho.com)' ,'www.downloadming.com','DownloadMing.Com','www.Songs.Pk','www.Songs.PK','(www.SongsLover.com)','www.SongsLover.com','(MyMp3Singer.com)',' - www.SongsLover.com',' - MyMp3Singer.com','DownloadMing.SE','MyMp3Singer.com',' - DJMaza.Info',' - www.DJMaza.Com','[2013-Mp3-320kbps]',' - www.Songs.PK',' @ SongsDL.com','SongsDL.com','www.freshnewtracks.com','www.RnBXclusive.com',' - www.GRIZZLIS.LT','www.Webmusic.IN',' [www.DJLUV.in]',' - www.SongsLover.pk','www.Songs.PK','www.Songs.PK','--[CooL GuY] {{a2zRG}}','[Full-Movie-Album]',' SongsLover.pk ','SongsLover.pk','[CooL GuY] {{a2zRG}} [2013-Mp3-320kbps] [Full-Movie-Album]','DownloadMing.Com','- DownloadMing.Com',' - DownloadMing.Com','www.sites.google.com/site/ring2mobile/','rnb-lounge.6x.to','..:: www.x-raid.nu ::..','www.x-raid.nu','[Want3d]','www.DJMaza.Com',' - www.DJMaza.Com']
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


def dataIndexer(Id,title) :
    for token in title.split(' ') :
        if token.isalpha() :
            if len(token) >= 1 :
                for i in range(1,len(token)+1) :                    
                    ##print os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])),md5(str(i)))+'.db'
                    try :                        
                        con = sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])),md5(str(i)))+'.db')
                    except sqlite3.OperationalError :
                        os.mkdir(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])))
                        con = sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token[0])),md5(str(i)))+'.db')
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
    ##print os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1]))+'/Data.db'
    try :
        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1]))+'/Data.db')
    except sqlite3.OperationalError :
        try :
            os.mkdir(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])))
        except OSError :
            pass
        try :
            ##print os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1]))
            os.mkdir(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1])))
        except OSError :
            pass
        con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(dataSet[0][0])),md5(dataSet[0][1]))+'/Data.db')
    con.text_factory = str
    cur = con.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) , played int, ctime varchar(100))'
    cur.execute(sql)
    sql = 'SELECT * FROM Data WHERE id = ?'
    cur.execute(sql,(dataSet[0],))
    if len(cur.fetchall())== 0 :
        sql = 'INSERT INTO Data VALUES (?,?,?,?,?,?,?,?,?)'
        cur.execute(sql,tuple(dataSet))
        con.commit()
        con.close()

def idGenerator(path,title) :           
    string = title.strip() + str( MP3(path).info.length )
    return md5(string)
        
def handleData(pathList) :
    con = sqlite3.connect(os.path.join(os.getcwd(),'Data.db'))
    con.text_factory = str
    cur = con.cursor()
    for path in pathList :
        tags = getTags(path)
        ##print path
        #for item in tags :
            #print item
        for i in range(len(tags)) :
            tags[i] = uni(tags[i])
        Id = idGenerator(path,tags[0])
        sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) , played int , ctime varchar(100))'
        cur.execute(sql)
        sql = 'SELECT * FROM Data WHERE id = ?'
        cur.execute(sql,(Id,))
        ret = cur.fetchall()
        if len(ret) == 0 :
            sql = 'INSERT INTO Data VALUES (?,?,?,?,?,?,?,?,?)'
            cur.execute(sql,(Id,uni(tags[0]),uni(tags[1]),uni(tags[2]),uni(tags[3]),uni(tags[4]),path,0,getPathTime(path)))
            con.commit()
            dataIndexer(Id,uni(tags[0]))
            idIndexer([Id,uni(tags[0]),uni(tags[1]),uni(tags[2]),uni(tags[3]),uni(tags[4]),path,0,getPathTime(path)],)
    con.close()

def scanner(dir_) :
    over = False
    while not over :
        contents =  glob.glob(dir_)
        mp3 = [ path for path in contents if path[-4:].lower() == '.mp3']
        handleData(mp3)
        dirs = [ path for path in contents if os.path.isdir(path)]
        if len(dirs) == 0 :
            over = True
        dir_ += '/*'

def removePatterns(Id,title) :
    tokens = title.split(' ')
    for token in tokens :
        if len(token) >= 1 :
            for i in range(1,len(token)+1) :                                
                con = sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'data'),md5(token.lower() [0])),md5(str(i)))+'.db')
                cur = con.cursor()
                sql = 'DELETE FROM Data WHERE id = ?'
                print title
                cur.execute(sql,(Id,))
                con.commit()
                con.close()

def updateData() :
    var = list('0123456789ABCDEF')
    for inner in var :
        for outer in var :
            try :
                con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(outer)),md5(inner))+'/Data.db')
            except sqlite3.OperationalError :
                try :   
                    os.mkdir(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(outer)))
                except OSError :
                    pass
                try :
                    os.mkdir(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(outer)),md5(inner)))
                except OSError :
                    pass
                con=sqlite3.connect(os.path.join(os.path.join(os.path.join(os.getcwd(),'tracer'),md5(outer)),md5(inner))+'/Data.db')
            con.text_factory = str
            cur = con.cursor()
            try :
                sql = 'SELECT * FROM Data'
                cur.execute(sql)
                con.commit()
                Data = cur.fetchall()
                for item in Data :                                        
                    if not os.path.exists(str(item[6])) :
                        removePatterns(str(item[0]),str(item[1]))
                        print str(item[6])
                        sql = 'DELETE FROM Data WHERE id LIKE ?'
                        cur.execute(sql,('%'+str(item[0])+'%',))
                        con.commit()
            except sqlite3.OperationalError :
                sql = 'CREATE TABLE IF NOT EXISTS Data (id varchar(100), title varchar(100), artist varchar(100), album varchar(100), genre varchar(100), year varchar(100) , path varchar(200) ,played int, ctime varchar(100))'
                cur.execute(sql)
                con.commit()
        Data = cur.fetchall()
        for track in Data :
            if not os.path.exists(track[6]) :
                sql = 'DELETE FROM Data WHERE id = ?'
                cur.execute(sql,(track[0],))
                con.commit()
    con.close()
    time.sleep(5)
    updateData()

def findMusic(shared) :
    while True :
        for path in shared :
            scanner(path)
    time.sleep(5)

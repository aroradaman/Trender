import os
import sqlite3
from operator import itemgetter
import hashlib
from random import randrange
from operator import itemgetter
from collections import Counter
import sys
import time
import json
import pymongo

IP = '127.0.0.1'
mongoPort = 27017
#time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))

def md5(string) :
	hasher = hashlib.md5()
	hasher.update(string.lower())
	return hasher.hexdigest().lower()

def analyse(VisualType,VisualOn) :
	content = ''	
	if VisualType == 'pie' :
		con = sqlite3.connect(os.path.join(os.getcwd(),'Data.db'))
		con.text_factory = str
		cur = con.cursor()
		sql = 'SELECT ' + VisualOn + ' FROM Data'
		cur.execute(sql)
		Data = cur.fetchall()
		con.close()
		Data = map(lambda x:str(x[0]),Data)
		Data = Counter(Data)
		Max = 0
		MaxC = ''
		LowC = ''
		Avg = 0
		Low = 500000
		Tot = 0
		count = 0
		for part in Data :
			Tot += Data[part]
			if Data[part] > Max :
				Max = Data[part]
				MaxC = part
			if Data[part] < Low :
				Low = Data[part]
				LowC = partud
			count += 1
		Avg = float(Tot) / count
		Table = []
		for part in Data :
			if float(Data[part])/(Avg/2) :
				Table.append([part, (float(Data[part])*100)/Tot  ])

	elif VisualType == 'line' :
		print '\t\t',VisualOn
		con = sqlite3.connect(os.path.join(os.getcwd(),'Data.db'))
		con.text_factory = str
		cur = con.cursor()
		Data = {}
		for param in ['artist','album','genre','title'] :
			sql = 'SELECT * FROM Data WHERE ' + param + ' LIKE ? '
			cur.execute(sql,('%'+VisualOn+'%',))
			temp = cur.fetchall()
			temp = map(lambda x:{x[0]:x[1:]} ,temp)
			for item in temp :
				Data.update(item)
		con.close()
		newArr = []
		for key in Data.keys() :
			for inner in json.loads(Data[key][6]) :
				temp = time.strftime('%Y::%m::%d::%H::%M::%S', time.localtime(inner)).split('::')
				for val in Data[key][:5] :
					if VisualOn.lower() in val.lower() :
						match = val
						newArr.append(match+'<>'+temp[4])
		newArr = Counter(newArr)
		arr =  [ [newArr[x],int(x.split('<>')[1])] for x in newArr ]
		arr = sorted(arr,key=itemgetter(1))
		yVal = map(lambda x:x[0],arr)
		xVal = map(lambda x:x[1],arr)
		try :
			temp = json.dumps({'on': match, 'y' : yVal, 'x' : xVal})
		except :
			temp = json.dumps({'on':None,'y':[],'x':[]	})
		return temp


def globalAnalyse(VisualType,VisualOn,column) :
	if VisualType == 'line' :
		client = pymongo.MongoClient(IP,mongoPort)
		db = client.Central
		newArr = []
		for item in db.Data.find({column:{'$regex':VisualOn,'$options':'-i'}}) :
			for times in item['played'] :
				temp = time.strftime('%Y::%m::%d::%H::%M::%S', time.localtime(times)).split('::')				
				newArr.append(item[column]+'<>'+temp[4])
		newArr = Counter(newArr)
		arr =  [ [newArr[x],int(x.split('<>')[1])] for x in newArr ]		
		arr = sorted(arr,key=itemgetter(1))		
		yVal = map(lambda x:x[0],arr)
		xVal = map(lambda x:x[1],arr)
		try :
			temp = json.dumps({'on': VisualOn	, 'y' : yVal, 'x' : xVal})
		except Exception as error :
			print error
			temp = json.dumps({'on':None,'y':[],'x':[]	})
		return temp
#	analyse('line','linkin')

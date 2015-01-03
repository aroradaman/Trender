import os
import sqlite3
from operator import itemgetter
import hashlib
from random import randrange
from operator import itemgetter
def md5(string) :
        hasher = hashlib.md5()
        hasher.update(string.lower())
        return hasher.hexdigest().lower()

def analyse(VisualType,VisualOn) :
        content = ''
        if VisualType == 'pie' :
                content = '''
<!doctype html>
<html>
<head>
<title>data</title>
<script src="Chart.js"></script>
</head>
<body>
<div id="canvas-holder">
<canvas id="chart-area" width="900" height="900"/>
</div>
<script>
var pieData = [ '''
                con = sqlite3.connect(os.path.join(os.getcwd(),'Data.db'))
                con.text_factory = str
                cur = con.cursor()
                sql = 'SELECT ' + VisualOn + ' FROM Data'
                cur.execute(sql)
                Data = cur.fetchall()
                con.close()
                Data = map(lambda x:str(x[0]),Data)                
                UniqData = list(set(Data))
                GroupData = []
                total = 0
                for outer in UniqData :                        
                        if outer == '###' or outer == '#' or outer == '' or outer =='genre':
                                count = 1
                        else :                                
                                count = 1
                                for inner in Data :
                                        if inner == outer :
                                                count+=1
                                total += count
                                GroupData.append([outer,count])
                for item in GroupData :
                        if float(item[1])/total*100 > 0.7 :
                                content += '{ value : ' + str(float(item[1])/total*100)[:4] + ', color : "#'   + md5(str(randrange(100,200)))[:6]+ '", highlight : "#'   + md5(str(randrange(100,200)))[:6]+ '", label : "' + item[0] + '"},\n'
                content += '''
	];	
	window.onload = function(){
	var ctx = document.getElementById("chart-area").getContext("2d");
	window.myPie = new Chart(ctx).Pie(pieData);
	};
</script>
</body>
</html>'''
                return content
        elif VisualType == 'bar' :
                content =  '''<!DOCTYPE HTML>
<html>
<head>
<script type="text/javascript">
window.onload = function () {
var chart = new CanvasJS.Chart("chartContainer", {
title:{ text:"Fortune Global 500 Companies by Country"},
axisX:{	interval: 1, gridThickness: 0, labelFontSize: 10, labelFontStyle: "normal",labelFontWeight: "normal",labelFontFamily: "Lucida Sans Unicode"},
axisY2:{interlacedColor: "rgba(1,77,101,.2)",gridColor: "rgba(1,77,101,.1)"},
data: [{ type: "bar",name: "companies",	axisYType: "secondary",	color: "#014D65",
dataPoints: [
'''
                con = sqlite3.connect(os.path.join(os.getcwd(),'Data.db'))
                con.text_factory = str
                cur = con.cursor()
                sql = 'SELECT ' + VisualOn + ' FROM Data'
                cur.execute(sql)
                Data = cur.fetchall()
                con.close()
                Data = map(lambda x:str(x[0]),Data)                
                UniqData = list(set(Data))
                GroupData = []
                total = 0
                for outer in UniqData :                        
                        if outer == '###' or outer == '#' or outer == '' or outer =='genre':
                                count = 1
                        else :                                
                                count = 1
                                for inner in Data :
                                        if inner == outer :
                                                count+=1
                                total += count
                                GroupData.append([outer,count])
                GroupData = sorted(GroupData,key=itemgetter(1))
                for item in GroupData :
                        if float(item[1])/total*100 > 0.7 :
                                content += '{ y : ' + str(float(item[1])/total*100)[:4] + ', label : "' + item[0] + '"},\n'
                content += ''']}
]});
chart.render();
}
</script>
<script type="text/javascript" src="canvasjs.min.js"></script>
<script type="text/javascript" src="Chart.min.js"></script>
</head>
<body>
<div id="chartContainer" style="height: 100%; width: 100%;">
</div>
</body>
</html>'''
                return content
                
        

def getHTML(VisualOn ,VisualType) :
        html = analyse(VisualType,VisualOn)
        return html
        

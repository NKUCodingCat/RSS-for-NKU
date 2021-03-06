#encoding=utf8
#==========================================================
#getPages():  根据链接获取网页内容
#getURLs():  从网页内容中获取新闻的链接
#getTitles():  从网页内容中获取新闻的标题
#check_updated():  检查某个新闻分类是否有更新
#do_update():  更新某个新闻分类的XML文件
#creat_item():  根据新闻链接和标题创建XML格式的新闻内容节点
#getNewItems():  根据有更新的内容创建XML格式的新闻节点
#==========================================================
import httplib
import re
import Date
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import mail



def sub(NAME):
	f = open(NAME,"r")
	Con = f.read()
	f.close()
	if Con [0:19] == "<rss version=\"2.0\">":
		f = open(NAME,"w")
		Con = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n<?xml-stylesheet type=\"text/css\" href=\"a.css\"?>\n" +Con
		f.write(Con)
		f.close()






def getTime(content):
	Time=re.findall('\d\d\d\d\.\d\d\.\d\d',content)
	return Time

def getURLs(content):
	result_re=re.compile('<a.+href="(/html/.+html)">')
	result=result_re.findall(content)
	return result
	
def getPages(context, pageURL):
	context.request('GET',pageURL)
	content=context.getresponse()
	if content.status!=200:
		print 'http error:',content.status
		exit(-1)
	return content.read()
	
def getTitles(content):
	title=re.findall('<a.+href="/html/.+html">(.+)</a>',content)
	return title

def check_updated(url, latest_url):
	return (url==latest_url)

def do_update(Time , urls, titles, latest_url, xml_file):
	try:
		tree=ET.parse("/s/test/"+xml_file)
	except:
		f = open("/s/test/"+xml_file,"w")
		f.close()
		tree=ET.parse("/s/test/"+xml_file)
	root=tree.getroot()
	channel=root.find('channel')
	latest_update=latest_url
	for new_item in getNewItems(Time ,urls,titles,latest_url):
		channel.insert(3,create_item(new_item[0],unicode(new_item[1],'utf8'),Date.DateTran(new_item[2])))
		latest_update=new_item[0]
	tree.write("/s/test/"+xml_file)
	sub("/s/test/"+xml_file)
	return latest_update

def create_item(url, title ,Time):
	element_item = Element('item')
	element_title = Element('title')
	element_link = Element('link')
	element_time = Element('time')
	element_des = Element('description')
	element_title.text=title
	element_link.text="http://sms.nankai.edu.cn"+url
	element_time.text = Time
	element_des.text = title
	element_item.insert(0,element_des)
	element_item.insert(0,element_link)
	element_item.insert(0,element_time)
	element_item.insert(0,element_title)
	return element_item

def getNewItems(Time , urls, titles, latest_url):
	newItems=[]
	for i in range(len(urls)):
		if urls[i] == latest_url:
			break
		else:
			newItems.append((urls[i],titles[i],Time[i]))
	newItems.reverse()
	return newItems
	
def up():
	Ver = int(time.time())
	NEWITEM = []
	isnew = False
	page_set=[
		'/html/kydt/all/page1',
		'/html/xwzx/xyxw/page1',
		'/html/bksjx/all/page1',
		'/html/yjsjx/all/page1',
		'/html/xsgz/all/page1',
		'/html/zsxx/all/page1'
	]#科研动态，学院新闻，本科生教育，研究生教育，学生工作，公共数学
	xml_set=[
		'kydt.xml',
		'xwzx.xml',
		'bksjx.xml',
		'yjsjx.xml',
		'xsgz.xml',
		'zsxx.xml'
	]

	file=open('/s/test/latest','r')
	latest=file.read()
	file.close()
	New = []
	st = ""
	for i in range(len(latest)):
		if latest[i] != "\n":
			st += latest[i]
		else:
			New.append(st)
			st = ""
	latest = New[:]
	print latest
	conn=httplib.HTTPConnection('sms.nankai.edu.cn')
	for i in range(len(page_set)):
		page=getPages(conn, page_set[i])
		urls=getURLs(page)
		titles=getTitles(page)
		Time = getTime(page)
		if not check_updated(urls[0], latest[i]):
			latest_update=do_update(Time , urls, titles, latest[i], xml_set[i])
			latest[i]=latest_update
			NEWITEM.append((latest_update,titles[0]))
			isnew = True
	conn.close()
	f = open("/s/test/"+"Now","w")
	f.write(str(Ver))
	f.close()
	if isnew:
		file=open("/s/test/"+'latest','w')
		for line in latest:
			file.write(str(line))
			file.write("\n")
		file.close()
		f = open("/s/test/"+"Version","w")
		f.write(str(Ver))
		f.close()
	return NEWITEM
if __name__ == "__main__":
	up()
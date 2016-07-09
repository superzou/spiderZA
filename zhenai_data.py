#-*-coding:utf-8-*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time,csv,os
import re,requests
from bs4 import BeautifulSoup
import pymongo

connection = pymongo.MongoClient()

db = connection.zhenaidata

wd = webdriver.Firefox()
wd.implicitly_wait(60)

def saveZAdata(str):
    db.ZAdata.insert(str)

if os.path.exists('./za_pic'):
        pass
else:
        os.mkdir('./za_pic')

url = 'http://www.zhenai.com/'

def scroll(driver):                 #模拟鼠标下滑的动作
    driver.execute_script("""
        (function () {
            var y = document.body.scrollTop;
            var step = 2000;
            window.scroll(0, y);
            function f() {
                if (y < document.body.scrollHeight) {
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 50);
                }
                else {
                    window.scroll(0, y);
                    document.title += "scroll-done";
                }
            }
            setTimeout(f, 1000);
        })();
        """)
def spiderZA(name,password,n):
    try:
    ###     模拟浏览器动作

        wd.get(url)
        wd.find_element_by_id("jcLoginName").click()
        wd.find_element_by_id("jcLoginName").clear()
        wd.find_element_by_id("jcLoginName").send_keys(name)
        wd.find_element_by_id("jcLoginPass").click()
        wd.find_element_by_id("jcLoginPass").clear()
        wd.find_element_by_id("jcLoginPass").send_keys(password)
        wd.find_element_by_link_text("登录").click()
        wd.find_element_by_link_text("搜索").click()
        wd.find_element_by_css_selector("a.btnR2").click()

        for i in range(1,n):        ###设置执行下滑的次数
            scroll(wd)
            time.sleep(5)           ###下滑后给一个加载时间
        memberid = re.findall('data-memberid="(.*?)"',wd.page_source,re.S)

    finally:
        wd.quit()
        if not True:
            raise Exception("Test failed.")

    fp = open('./data.txt','w')
    for i in memberid:          #将用户id写在本地
        fp.write(str(i)+'\n')
    fp.close()

    base_info = []
    base_answer = []
    index = 1
    for each in memberid:
        print each
        url_1 = 'http://album.zhenai.com/u/'+ each +'?flag=s'
        html = requests.get(url_1).text
        soup = BeautifulSoup(html,'lxml')
        pic_url = re.findall('<img data-big-img="(.*?)"',html,re.S)

        for i in range(0,len(pic_url)):     #下载用户大图像
            pic = requests.get(pic_url[i])
            fp = open('za_pic/'+str(index)+'_'+str(i)+'.jpg','wb')
            fp.write(pic.content)
            fp.close()

        for item in soup.select('.p20'):
            for item_1 in item.select('td'):
                base_info.append(item_1.contents[0].text)
                base_answer.append(item_1.contents[1])
        temp_dict = dict(zip(base_info,base_answer))        #构造成员基本信息字典
        temp_dict['Number'] = index                         #增加成员序号索引
        saveZAdata(temp_dict)                               #将数据保存到mongodbdb
        index += 1

    print 'done\n'


name = 'your name'
password = 'password'
spiderZA(name,password,n)  #n 你要执行的次数



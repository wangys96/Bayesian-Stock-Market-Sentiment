import os
import time as t
import json
import jieba
import numpy
import tushare
import pymysql
import requests
from lxml import etree
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.externals import joblib
from datetime import datetime as dt
from datetime import timedelta
hot_cache={"timeout":timedelta(minutes=10)}
ts_k_cache={"timeout":timedelta(minutes=60),"update":(15,1)}
ts_data_cache={"timeout":timedelta(minutes=60)}


def load_dict(path='worddict'):
    '''
    加载本地情感词典worddict，返回dict
    '''
    with open(path,'r',encoding='utf-8') as f:
        content = json.load(f)
    #return content['positiveWord'],content['negativeWord'],content['neutralWord']
    return content

def dump_dict(dic,path):
    '''
    将情感词典保存至本地worddict
    '''
    with open(path,'w',encoding='utf-8') as f:
        json.dump(dic,f)

def get_data(start_page,end_page,sector='gssz',newthan=None,mul=None):
    '''
    从股吧指定板块抓取文章，输入起止页码，返回[(id，标题，时间，内容),...]
    '''
    error = []
    sess = requests.Session()
    data = {'latest':0,'articles':[]}
    for page_num in range(start_page, end_page+1):
        if mul and page_num%mul[0]!=mul[1]:continue
        print("[Worker{}]正爬取{}页".format(mul[1],page_num))
        url = 'http://guba.eastmoney.com/list,{},f_{}.html'.format(sector,page_num)
        try:
            res = sess.get(url)#访问文章列表
        except requests.exceptions.RequestException:
            print(" [Worker{}]ReqError:".format(mul[1]),url)
            error.append(url)
            continue
        #获取网页xml树
        e = etree.HTML(res.text).xpath("//div[@id='articlelistnew']/div[starts-with(@class,'articleh normal')]/span[@class='l3']") 
        #取得每一个帖子的标题和链接
        target = [(x.xpath("a/@title")[0], x.xpath("a/@href")[0]) for x in e if x.xpath("a/@href")[0][:6]=='/news,']
        for title, href in target:#每一页所有帖子
            aid = int(href.split(".")[0].split(",")[2])
            if newthan and aid<=newthan:continue
            if href[0]=="/":
                url1="http://guba.eastmoney.com"+href
            else:
                url1="http://guba.eastmoney.com/"+href
            try:
                res1 = sess.get(url1)#访问文章内容页面
            except requests.exceptions.RequestException:#处理HTTP超时等错误
                print(" [Worker{}]ReqError:".format(mul[1]),title,href,url1)
                error.append(href)
                continue            
            e1=etree.HTML(res1.text)#获取网页xml树
            try: 
                time_raw = e1.xpath("//div[@class='zwfbtime']/text()")[0].split(" ")#获取发表时间                
                time = time_raw[1].strip()+" "+time_raw[2].strip()
                #获取文章内容  
                content = "".join(e1.xpath("//div[@id='zwconbody']//text()")).replace('\u3000','').replace('\xa0','').strip() 
            except Exception:#处理文章列表的错误
                print(" [Worker{}]IndexError:".format(mul[1]),title,href,url1)
                error.append(int(href.split(".")[0].split(",")[2]))
                continue
            data['articles'].append((aid,title,time,content))#存入dict
            if data['latest']<aid:data['latest']=aid
            t.sleep(1)
    sess.close()
    print(" [Worker{}]finished. Errs:".format(mul[1]),error)
    return data, error

def get_data_quick(start_page,end_page,sector='gssz',newthan=None,mul=None,proxy=True):
    '''
    从股吧指定板块抓取文章标题，输入起止页码，返回[(id，标题，时间),...]
    '''    
    error = []
    sess = requests.Session()
    data = {'latest':0,'articles':[]}
    guba_headers={"Host":"guba.eastmoney.com",
            "Referer":"http://guba.eastmoney.com/list,{},f.html".format(sector),
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}    
    for page_num in range(start_page, end_page+1):
        if mul and page_num%mul[0]!=mul[1]:continue
        print(" [Worker{}]正爬取{}页".format(mul[1],page_num))
        url = 'http://guba.eastmoney.com/list,{},f_{}.html'.format(sector,page_num)
        try:
            res = sess.get(url,headers=guba_headers)
        except requests.exceptions.RequestException:
            print(" [Worker{}]ReqError:".format(mul[1]),url)
            error.append(url)
            continue
        e = etree.HTML(res.text).xpath("//div[@id='articlelistnew']/div[starts-with(@class,'articleh')]")
        target = [(x.xpath("./span[@class='l3']/a/@title")[0], 
                   x.xpath("./span[@class='l3']/a/@href")[0],
                   x.xpath("./span[@class='l5']/text()")[0]) 
                   for x in e if not x.xpath("./@id") and x.xpath("./span[@class='l3']/a/@href")[0][:6]=='/news,']
        for title, href, atime in target:
            aid = int(href.split(".")[0].split(",")[2])
            if aid>799843705:atime = "2019-"+atime.strip()+":00"                
            else:atime = atime = "2018-"+atime+":00"
            if atime[:7]<"2018-09":continue
            data['articles'].append((aid,title, atime))
            if data['latest']<aid:data['latest']=aid
        t.sleep(0.2)
    print(" [Worker{}]finished. Errs:".format(mul[1]),error)
    sess.close()
    return data, error

def get_data_nocontent(start_page,end_page,sector='gssz',newthan=None,mul=None,proxy=True):
    '''
    从股吧指定板块抓取文章标题，输入起止页码，返回[(id，标题，时间),...]
    '''    
    prox = Proxies()
    if not proxy:cur_prox={}
    error = []
    sess = requests.Session()
    data = {'latest':0,'articles':[]}
    guba_headers={"Host":"guba.eastmoney.com",
            "Referer":"http://guba.eastmoney.com/list,{},f.html".format(sector),
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}    
    for page_num in range(start_page, end_page+1):
        if mul and page_num%mul[0]!=mul[1]:continue
        print(" [Worker{}]正爬取{}页".format(mul[1],page_num))
        url = 'http://guba.eastmoney.com/list,{},f_{}.html'.format(sector,page_num)
        try:
            res = sess.get(url,headers=guba_headers)
        except requests.exceptions.RequestException:
            print(" [Worker{}]ReqError:".format(mul[1]),url)
            error.append(url)
            continue
        e = etree.HTML(res.text).xpath("//div[@id='articlelistnew']/div[starts-with(@class,'articleh')]/span[@class='l3']")#获取网页xml树           
        #取得每一个帖子的标题和链接
        target = [(x.xpath("a/@title")[0], x.xpath("a/@href")[0]) for x in e if x.xpath("a/@href")[0][:6]=='/news,']
        #每一页所有帖子
        if proxy:cur_prox = prox.get_proxy(mul[1])
        for title, href in target:
            aid = int(href.split(".")[0].split(",")[2])
            if newthan and aid<=newthan:continue
            if href[0]=="/":
                url1="http://guba.eastmoney.com"+href
            else:
                url1="http://guba.eastmoney.com/"+href
            try:
                res1 = sess.get(url1,headers=guba_headers,proxies=cur_prox)
            except requests.exceptions.RequestException:
                print(" [Worker{}]ReqError:".format(mul[1]),title,href,url1)
                error.append(href)
                continue
            #获取网页xml树
            e1=etree.HTML(res1.text)
            try:
                time_raw = e1.xpath("//div[@class='zwfbtime']/text()")[0].split(" ")
                #获取发表时间
                time = time_raw[1].strip()+" "+time_raw[2].strip()
                if time_raw[1].strip()[:7]<"2018-09":
                    print(" [Worker{}]finished. Errs:".format(mul[1]),error)
                    sess.close()
                    return data, error
            except Exception :
                print(" [Worker{}]IndexError:".format(mul[1]),title,href,url1)
                error.append(href)
                if proxy:
                    cur_prox = prox.get_proxy(mul[1],1)
                    continue                
                if len(error)>15:
                    print(" [Worker{}]Exit".format(mul[1]))
                    return
                continue
            #存入dict
            data['articles'].append((aid,title,time))
            if data['latest']<aid:data['latest']=aid

    print(" [Worker{}]finished. Errs:".format(mul[1]),error)
    sess.close()
    return data, error

def get_hotlist():
    timenow=dt.now()
    if 'res' in hot_cache and timenow-hot_cache['res'][0]<=hot_cache['timeout']:
        return hot_cache['res'][1]
    try:
        res=requests.get('http://guba.eastmoney.com/')
        res.encoding='utf-8'
        e=etree.HTML(res.text)
        data = [[x[5:11],y[:-1]] for x,y in \
            zip(e.xpath("//ul[@class='list']/li/a/@href")[:21],
                e.xpath("//ul[@class='list']/li/a/text()")[:21])]
        hot_cache['res']=(timenow,data)
        return data
        if data:return data
        res=requests.get('http://guba.eastmoney.com/')
        res.encoding='utf-8'
        e=etree.HTML(res.text)
        data = [[x[5:11],y[:-1]] for x,y in \
            zip(e.xpath('/html/body/div[4]/div[2]/div[3]/div/ul/li/a/@href'),
                e.xpath('/html/body/div[4]/div[2]/div[3]/div/ul/li/a/text()'))]
        hot_cache['res']=(timenow,data)
        return data
    except Exception as e:
        print(e.__repr__())
        return []

def load_data(path,newthan=None,freq='h'):
    '''
    读取本地爬取的文章，newthan是日期时间字符串，如果为其他类型则返回最新一期开始时间
    '''
    if os.path.exists(path):
        with open(path,'r',encoding='utf-8') as f:
            old = json.load(f)
        if type(newthan)==str and len(newthan)==19:
            for i,v in enumerate(old['articles']):
                if v[2]<newthan:break
            old['articles']=old['articles'][:i]
        elif newthan:
            if freq=='h':timebyte=13
            else: timebyte=10
            latest = old['articles'][0][2][:timebyte]
            for i,v in enumerate(old['articles']):
                if v[2][:timebyte]<latest:break
            old['articles']=old['articles'][:i]
        return old
    return None

def dump_data(path,newdata,append=False):
    '''
    保存爬取的文章，已存在则追加，不存在就创建。无返回值
    '''
    #先读取已存在的文件
    new = {x:y for x,y in newdata.items()}
    archive = []
    archive_dict = {}        
    if append and os.path.exists(path):
        with open(path,'r',encoding='utf-8') as f:
            old = json.load(f)
            archive = old['articles']
            for a in archive:
                archive_dict[a[0]]=1
            print("[Main]已打开旧文件，原有{}".format(len(archive)))
        #更新数据
        new['articles'].extend(archive)
    new['articles'].sort(key=lambda x:x[0],reverse=1)
    new['latest']=new['articles'][0][0]
    print("[Main]现有{}".format(len(new['articles'])))
    #写到硬盘
    with open(path,'w',encoding='utf-8') as f:
        f.write(json.dumps(new))

def dump_data_nocontent(path,newdata):
    '''
    保存爬取的文章（仅题目），已存在则追加，不存在就创建。无返回值
    '''
    #先读取已存在的文件
    archive = []
    archive_dict = {}
    new = {x:y for x,y in newdata.items()}
    if os.path.exists(path):
        with open(path,'r',encoding='utf-8') as f:
            old = json.load(f)
            archive = old['articles']
            for a in archive:
                archive_dict[a[0]]=1
            print("[Main]已打开旧文件，原有{}".format(len(archive)))
    #更新数据
    temp=[x for x in new['articles'] if x[0] not in archive_dict]
    new['articles'] = temp
    new['articles'].extend(archive)
    new['articles'].sort(key=lambda x:x[0],reverse=1)
    print("[Main]现有{}".format(len(new['articles'])))
    new['latest']=new['articles'][0][0]
    #写到硬盘
    with open(path,'w',encoding='utf-8') as f:
        f.write(json.dumps(new))
                
def predict_nb(data,freq='h',old={},model_path='data/'):
    '''
    分词并使用朴素贝叶斯进行情感归类，返回按指定频率统计数dict
    '''
    #情绪计数字典
    length=len(data['articles'])
    senti = {x:y for x,y in old.items()}
    clf = joblib.load(model_path+'clf')
    vectorizer = joblib.load(model_path+'vect')
    transformer = joblib.load(model_path+'tfidf')
    if freq=='h':timebyte,suffix=13,":00:00"
    else: timebyte,suffix=10," 00:00:00"
    print("[Main]正在进行文本分类计算")
    for idx,i in enumerate(data['articles']):
        if idx%(length//10+1)==0:print("正在处理{}/{} 已完成{}%".format(idx,length,round(idx/length*100,3)))
        title,time=i[1],i[2]
        text_predict=numpy.array([" ".join([x for x in jieba.cut(title, cut_all=1) if x!=''])])
        text_frequency = vectorizer.transform(text_predict)
        new_tfidf = transformer.transform(text_frequency)
        predicted = clf.predict(new_tfidf)
        predicted_score = clf.predict_proba(new_tfidf)[0]
        if time[:timebyte]+suffix not in senti:
            senti[time[:timebyte]+suffix] = [0,0,0,0,0,0,0]
        #记录当天帖子数
        #senti[time[:timebyte]+suffix][0]+=1
        #匹配计数
        if predicted == '积极':
            senti[time[:timebyte]+suffix][0] += 1
        elif predicted == '消极':
            senti[time[:timebyte]+suffix][1] += 1
        elif predicted == '中立':
            senti[time[:timebyte]+suffix][2] += 1
        senti[time[:timebyte]+suffix][3] += predicted_score[3] #积极
        senti[time[:timebyte]+suffix][4] += predicted_score[2] #消极
        senti[time[:timebyte]+suffix][5] += predicted_score[0] #中立
    return senti

def download_data_nocontent_mp(start,target='gssz',proc_num=10,multip=10,newthan=0):
    '''
    多进程爬虫函数，爬取指定板块的指定页数的文章标题
    '''
    from multiprocessing import Pool
    p = Pool(proc_num)
    res=[]    
    for i in range(proc_num):
        res.append(p.apply_async(get_data_quick,(start,start+proc_num*multip-1,
                                                    target,newthan,(proc_num,i))))
    p.close()
    p.join()
    new = {'latest':0,'articles':[]}
    for p_ret in res:
        data,err = p_ret.get()
        for aid,title,time in data['articles']:
            new['articles'].append((aid,title,time))
            if aid>new['latest']:new['latest']=aid
    return new

def download_data_mp(start,target='gssz',proc_num=10,multip=10,newthan=0):
    '''
    多进程爬虫函数，爬取指定板块的指定页数的文章+全文
    '''
    from multiprocessing import Pool    
    p = Pool(proc_num)#建立进程池
    res=[]
    for i in range(proc_num):#为每个进程分配下载任务，调用get_data函数
        res.append(p.apply_async(get_data,(start,start+proc_num*multip-1,
                                                    target,newthan,(proc_num,i))))
    p.close()#封闭进程池
    p.join()#进程运行
    new = {'latest':0,'articles':[]}
    title_dict = {}
    for p_ret in res:#获取每个进程返回结果
        data,err = p_ret.get()        
        for aid,title,time,content in data['articles']:
            if aid>new['latest']:new['latest']=aid
            if title in title_dict:continue
            new['articles'].append((aid,title,time,content))#将文本数据存入dict
            title_dict[title]=1                
    return new

def get_tushare_data(api_name,params,fields):
    '''
    获取tushare其他讯息，
    '''
    timenow = dt.now()
    cache_target = "_".join([api_name,str(params),str(fields)])
    if cache_target in ts_data_cache and timenow-ts_data_cache[cache_target][0]<=ts_data_cache['timeout']:
        return ts_data_cache[cache_target][1]
    res=requests.post(url="http://api.tushare.pro",data=json.dumps({
        "api_name":api_name,
        "token" :"6dfdd73e113b535573dcfa339dba3edf623e93d498daa729468974db",
        "params" :params,
        "fields" :fields})).json()
    if res['code']:
        raise IOError("Tushare:"+str(res['msg']))
    data = [res['data']['fields']]+res['data']['items']
    ts_data_cache[cache_target] = (timenow,data)
    return data

def get_stock_data(start,end,tscode='000001.SZ',type='E',adj='qfq'):
    '''
    获取股票历史数据，type: I-指数,E-股票，adj: qfq-前复权,None-不复权
    返回格式：
    [[trade_date, open, close, high, low, vol]...]
    '''
    cache_target = "_".join([tscode,start,end])
    timenow = dt.now()
    if cache_target in ts_k_cache and timenow-ts_k_cache[cache_target][0]<=ts_k_cache['timeout']:
        return ts_k_cache[cache_target][1]
    pro = tushare.pro_api('6dfdd73e113b535573dcfa339dba3edf623e93d498daa729468974db')
    df = tushare.pro_bar(pro_api=pro,ts_code=tscode, asset=type,adj=adj,start_date=start,\
                        end_date=end)[['trade_date','open','close','high','low','vol']]
    data = [["{}-{}-{}".format(r[0][:4],r[0][4:6],r[0][6:]),*r[1:]]for i,r in df.iterrows()]
    if timenow.hour==ts_k_cache['update'][0] and \
      timenow.minute+ts_k_cache['timeout'].seconds/60<=60+ts_k_cache['update'][1]:
        ts_k_cache[cache_target] = (timenow,data)
    else:
        ts_k_cache[cache_target] = (dt(year=timenow.year,month=timenow.month,\
        day=timenow.day,hour=ts_k_cache['update'][0],\
        minute=60+ts_k_cache['update'][1]-round(ts_k_cache['timeout'].seconds/60)),data)
    return data

class DataBase(object):
    '''
    数据库上下文对象
    '''
    time0 = dt.now()
    k_cache = {"timeout":timedelta(minutes=60),"update":(15,1)}
    def __init__(self,cn_to=7200, host='cdb-enj5kzuv.gz.tencentcdb.com',
        port=10068,user='root',password="Wys360403",database="InvisibleHand"):
        self.cn_to = cn_to
        self.host = host
        self.port = port
        self.user = user
        self.pw = password
        self.db = database
        self.connect(self.host,self.port,self.user,self.pw,self.db)
    
    def connect(self,host='cdb-enj5kzuv.gz.tencentcdb.com',port=10068,user='root',password="Wys360403",database="InvisibleHand"):
        if database:
            self.conn = pymysql.connect(host=host,port=port,user=user,password=str(password),database=database)
        else:
            self.conn = pymysql.connect(host=host,port=port,user=user,password=str(password))
        self.time0 = dt.now()
        self.cursor = self.conn.cursor()

    def _exe(self,sql):
        timenow=dt.now()
        if (timenow-self.time0).seconds>self.cn_to:
            self.conn.close()
            self.connect(self.host,self.port,self.user,self.pw,self.db)
        self.cursor.execute(sql)
        self.time0 = timenow
        return self.cursor.fetchall()

    def _tolist(self,tuple_data,reverse=False):
        if reverse:
            return [[*x] for x in tuple_data[::-1]]
        return [[*x] for x in tuple_data]

    def select(self,target='*',table='senti',where='',order='datetime desc',limit=''):
        if self.cursor:
            if where:where='where '+where
            if order:order='order by '+order
            if limit:limit='limit '+str(limit)
            else:limit=''
            return self._exe("select {} from {} {} {} {};".format(target,table,where,order,limit))
    
    def select_k_data(self,ts_code,period=60,order='desc'):
        """
        返回k线数据 [date,ts_code,open,close,high,low,vol]
        """
        timenow = dt.now()
        cache_target = "_".join([ts_code,str(period)])        
        if cache_target in self.k_cache and timenow-self.k_cache[cache_target][0]<self.k_cache['timeout']:            
            return self.k_cache[cache_target][1]
        if self.cursor:
            data = self._exe("select * from k_data where ts_code=\"{}\"\
                    order by date {} limit {};".format(ts_code,order,period))
            if timenow.hour==self.k_cache['update'][0] and \
                timenow.minute+self.k_cache['timeout'].seconds/60<=60+self.k_cache['update'][1]:
                    self.k_cache[cache_target] = (timenow,data)
            else:
                self.k_cache[cache_target] = (dt(year=timenow.year,month=timenow.month,\
                day=timenow.day,hour=self.k_cache['update'][0],\
                minute=60+self.k_cache['update'][1]-round(self.k_cache['timeout'].seconds/60)),data)
            return data

    def insert(self,dataset,table='senti',\
           col='datetime,code,pos,neg,neu,posscore,negscore,neuscore',\
           is_str=[1,1,0,0,0,0,0,0],method='INSERT'):
        tar=""
        if type(col)==list:col_name=",".join(col)
        else:col_name=col
        val_format="("
        for i in is_str:
            if i:val_format+="\'{}\',"
            else:val_format+="{},"
        val_format=val_format[:-1]+"),"
        for i,v in enumerate(dataset):
            tar+=val_format.format(*v)
        sql = method+" INTO "+table+"("+col_name+")VALUES"+tar[:-1]+";"
        self._exe(sql)
        self.conn.commit()
        print("[DB]已插入数据",table,i+1)

    def create(self,name,cols=''):
        sql = "CREATE TABLE {} ({});".format(name,cols)
        self._exe(sql)
        self.conn.commit()

    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

def data_h2d(sorted_data=None,target='gssz'):
    """
    将小时数据转化为每日数据，存于数据库
    """
    if not sorted_data:
        with DataBase() as dbo:
            old = dbo.select(table="senti",where="code='{}'".format(target),limit="")
        add,d = lambda x,y:[x+y for x,y in zip(x,y)],{}
        for i in old:
            d[i[0][:10]]=add(d.setdefault(i[0][:10],[0]*6),i[2:])
        res = [[x,target,*y] for x,y in d.items()]
        res.sort(key=lambda x:x[0],reverse=True)
        return res

    with DataBase() as dbo:
        old = dbo.select(table="senti_daily",where="code='{}'".format(target),limit="1")
    if len(old)>0:
        add,d = lambda x,y:[x+y for x,y in zip(x,y)],{old[0][0]:[*old[0][2:]]}
        for i in sorted_data:
            d[i[0][:10]]=add(d.setdefault(i[0][:10],[0]*6),i[2:])
        res = [[x,target,*y] for x,y in d.items()]
        res.sort(key=lambda x:x[0],reverse=True)
    else:
        add,d = lambda x,y:[x+y for x,y in zip(x,y)],{}
        for i in sorted_data:
            d[i[0][:10]]=add(d.setdefault(i[0][:10],[0]*6),i[2:])
        res = [[x,target,*y] for x,y in d.items()]
        res.sort(key=lambda x:x[0],reverse=True)
    return res

def update_k_data():
    with DataBase() as dbo:
        latest = dbo._exe('select date from k_data  order by date desc limit 1')[0][0]
    latest=latest[:4]+latest[5:7]+latest[8:]

    res=requests.post(url="http://api.tushare.pro",data=json.dumps({
        "api_name":"trade_cal",
        "token" :"6dfdd73e113b535573dcfa339dba3edf623e93d498daa729468974db",
        "params" :{"start_date":latest,"end_date":dt.now().strftime("%Y%m%d")},
        "fields" :""
        })).json()
    tc=[x[1] for x in res['data']['items'] if x[2] and latest<x[1] and x[1]<=dt.now().strftime("%Y%m%d")]
    for date in tc:
        res=requests.post(url="http://api.tushare.pro",data=json.dumps({
            "api_name":"index_daily",
            "token" :"6dfdd73e113b535573dcfa339dba3edf623e93d498daa729468974db",
            "params" :{"ts_code":"000001.SH","trade_date":date},
            "fields" :"trade_date,ts_code,open,close,high,low,vol"
            })).json()
        data = [[x[0],x[1][:4]+"-"+x[1][4:6]+"-"+x[1][6:],*x[2:]] for x in res['data']['items']]
        if not data:break
        with DataBase() as dbo:
            dbo.insert(data,"k_data","ts_code,date,close,open,high,low,vol",
                [1,1,0,0,0,0,0])         
        res=requests.post(url="http://api.tushare.pro",data=json.dumps({
            "api_name":"daily",
            "token" :"6dfdd73e113b535573dcfa339dba3edf623e93d498daa729468974db",
            "params" :{"trade_date":date},
            "fields" :"trade_date,ts_code,open,close,high,low,vol"
            })).json()
        data = [[x[0],x[1][:4]+"-"+x[1][4:6]+"-"+x[1][6:],*x[2:]] for x in res['data']['items']]        
        with DataBase() as dbo:
            dbo.insert(data,"k_data","ts_code,date,open,high,low,close,vol",
                [1,1,0,0,0,0,0]) 
        print("[Main]已更新K线",date)

def update_nocontent(target='gssz',p=10,m=10,start=1,path="data/"):
    with DataBase() as dbo:
        latest = dbo._exe(sql="select * from latest where code='{}';".format(target))
        if len(latest)>0:
            latest=latest[0][1]
        else:latest=0
    result = download_data_nocontent_mp(start,target=target,proc_num=p,multip=m,newthan=latest)
    with DataBase() as dbo:
        if latest:
            old = dbo.select(table="senti",where="code='{}'".format(target),limit=1)[0]
            last = {old[0]:[*old[2:]]}
            print('[Main]载入上次数据',last)
        else:last={}
        senti = predict_nb(result,'h',last)
        print("[Main]计算完毕，正在保存数据")
        s = sorted([(i,target,*v) for i,v in senti.items()],key=lambda x:x[0],reverse=1)
        dbo.insert(s,table="senti",method='REPLACE')
        s24 = dbo._exe("select * from senti where code='{}' order by datetime desc limit 24".format(target))
        s24 = sum([x[5] for x in s24])/(sum([x[5] for x in s24])+sum([x[6] for x in s24]))
        dbo.insert([[target,result['latest'],result['articles'][0][2],s24]],'latest','code,id,datetime,senti',
                    [1,0,1,0],method='REPLACE')
        dump_data_nocontent(path+"guba_{}_nocontent.json".format(target),result)
        print('[Main]文件保存完成')
        print("[Main]正在计算日频数据")
        senti_daily = data_h2d(s,target)
        print("[Main]正在保存日频数据")
        dbo.insert(senti_daily,"senti_daily",method="REPLACE")    

def supply_nocontent(target='gssz',p=10,m=10,start=3000,path="data/"):
    result = download_data_nocontent_mp(start,target=target,proc_num=p,multip=m,newthan=0)
    temp = {"latest":result["latest"],"articles":[x for x in result["articles"]]}
    dtdict,iddict = {x[2][:13]:1 for x in temp['articles']},{x[0]:1 for x in temp['articles']}
    old = load_data(path+"guba_{}_nocontent.json".format(target))
    for i in old['articles']:
        if i[2][:13] in dtdict and i[0] not in iddict:
            temp['articles'].append(i)
            iddict[i[0]:1]
    print("[Main]数据对比完成")
    dump_data_nocontent(path+"guba_{}_nocontent.json".format(target),result)
    print('[Main]文件保存完成')
    senti = predict_nb(temp,'h')
    with DataBase() as dbo:        
        print("[Main]计算完毕，正在导入")
        s = sorted([(i,target,*v) for i,v in senti.items()],key=lambda x:x[0],reverse=1)
        dbo.insert(s,table="senti",method='REPLACE')
    print("[Main]正在计算日频")
    senti_daily = data_h2d(None,target)
    print("[Main]正在导入日频")
    dbo.insert(senti_daily,"senti_daily",method="REPLACE")

def get_hot_word(num=50,p=1,m=10,data=False,path="data/",period=12):
    stop_n=set(["市场","板块","公司","大盘","股票","个股","经济","股市","交易","资金",
        "指数","行情","时间","关注","A股","企业","了定","计划"])
    if data:
        res=load_data(path+"guba_gssz.json",
            (dt.now()-timedelta(hours=period)).strftime("%Y-%m-%d %H:%M:%S"))
    else:res=download_data_mp(1,'gssz',p,m)
    import jieba.analyse
    jieba.load_userdict(path+"user_dict.txt")
    jieba.analyse.set_stop_words(path+"stop_words.txt")    
    total,length={},len(res['articles'])
    print("[Main]正在进行关键词提取")
    for n,i in enumerate(res['articles']):
        a=jieba.analyse.textrank(i[3], topK=5, withWeight=True, allowPOS=('an','n','v','vd'))
        for j in a:
            if j[0] not in stop_n:
                total[j[0]]=total.setdefault(j[0],j[1])+j[1]
        #if n%(length//20+1)==0:print("正在处理{}/{} 已完成{}%".format(n,length,round(n/length*100,3))) 
    print("[Main]提取完成")
    return sorted([(x,y) for x,y in total.items()],key=lambda x:x[1],reverse=1)[:num]

def save_hot_word(data):
    final = "|".join(["_".join((x,str(round(y,3)))) for x,y in data])
    with DataBase() as dbo:
        dbo.insert([[dt.now().strftime("%Y-%m-%d %H:00:00"),final]],"words",
            'datetime,text',[1,1],"REPLACE")
    print("[Main]热点词保存完毕")

def load_hot_word():
    with DataBase() as dbo:
        res=dbo.select(table="words",limit=1)
    if len(res)>0:
        return [x.split("_") for x in res[0][1].split("|")] 
        
def init_utils():
    db = DataBase()
    to_tscode,to_name = {},{}
    for i in db._exe("select * from stock_list"):
        to_name[i[0]]=i[2]                          # ts_code->name
        to_tscode[i[1]]=i[0]                        # code->ts_code
        if i[2][0]=="*":to_tscode[i[2][1:]]=i[0]    # name->ts_code
        else:to_tscode[i[2]]=i[0]
    to_tscode['gssz']=1
    return db,to_tscode,to_name

def scheduled_tasks():
    #更新情感
    today=dt.now().strftime("%Y-%m-%d")
    with DataBase() as dbo:
        latest=[x[0] for x in dbo._exe("select * from latest") if x[2][:10]<today]
    db,to_tscode,to_name = init_utils()
    hot_list=[x[0] for x in get_hotlist()[0:10]]
    #update_list=set(latest)
    update_list=set(hot_list+latest)
    print("[Main]任务列表:",update_list)
    for n,i in enumerate(update_list):
        if i in to_tscode:
            print("-----------------------\n[Main]正在更新",i,"{}/{}".format(n+1,len(update_list)))
            t1=t.time()
            if i in latest:
                if i=="gssz" or i=="szzs":
                    update_nocontent(i,10,20,1)
                else:update_nocontent(i,10,20,1)
            else:
                print("[Main]记录新数据",i)
                update_nocontent(i,10,30,1)
            print("[Main]{}用时".format(i),t.time()-t1)
        else:
            print("排除",i)
    #更新k线
    print("[Main]正在更新K线数据")
    update_k_data()
    #更新热词
    print("[Main]正在热点词汇数据")
    w = get_hot_word()
    save_hot_word(w)

def load_update_param():
    with DataBase() as dbo:
        out=dbo._exe("select item,value from Sentiment_settings")
    d = {x:y for x,y in out}
    print("[{}]载入参数：".format(dt.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("  数据源：{}  舆情更新频率：{}  K线更新时间：{}  热点词更新频率：{}  热门股票更新频率：{}"
        .format(d['sources'],d['senti_update_freq'],d['k_data_update_time'],
                d['hot_update_freq'],d['hot_update_freq'],))
    print("[{}]开始自动更新舆情数据".format(dt.now().strftime("%Y-%m-%d %H:%M:%S")))            

if __name__=='__main__':
    #load_update_param()
    #scheduled_tasks()
    w = get_hot_word()
    save_hot_word(w)



import json
import tushare
import requests
from lxml import etree
from datetime import datetime as dt
from datetime import timedelta


import jieba
import numpy
import jieba.analyse
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.externals import joblib

hot_cache={"timeout":timedelta(minutes=10)}
ts_data_cache={"timeout":timedelta(minutes=60)}
stop_n=set(["市场","板块","公司","大盘","股票","个股"])

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

class DjangoDataBase(object):
    '''
    Django数据库上下文对象
    '''
    s_cache = {"timeout":timedelta(minutes=60)}
    k_cache = {"timeout":timedelta(minutes=60)}
    l_cache = {"timeout":timedelta(minutes=60)}
    cache_list = [s_cache,k_cache,l_cache]
    def __init__(self,django_conn):
        self.conn = django_conn
        self.cursor = django_conn.cursor()
        self.set_udt()
        self.next_udt()

    def set_udt(self,hour=15,minute=1):
        timenow = dt.now()
        for i in self.cache_list:
            i["update"] = dt(year=timenow.year,month=timenow.month,day=timenow.day,
                hour=hour,minute=minute)

    def next_udt(self):
        timenow = dt.now()
        for i in self.cache_list:
            if timenow>i["update"]:i["update"]+=timedelta(days=1)

    def _exe(self,sql):
        timenow=dt.now()
        try:
            self.cursor.execute(sql)
        except:
            self.cursor = self.conn.cursor()
            self.cursor.execute(sql)
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
    
    def select_s_data(self,code,daily=False,period=60,order='desc'):
        """
        返回k线数据 [date,ts_code,open,close,high,low,vol]
        """
        timenow = dt.now()
        cache = self.s_cache
        cache_target = "_".join([code,str(daily),str(period),order])        
        if cache_target in cache and timenow-cache[cache_target][0]<cache['timeout']:            
            return cache[cache_target][1]
        if self.cursor:
            if daily:
                data = self._exe("select * from senti_daily where code=\"{}\"\
                        order by datetime {} limit {};".format(code,order,period))
            else:
                data = self._exe("select * from senti where code=\"{}\"\
                        order by datetime {} limit {};".format(code,order,period))
            self.next_udt()
            if (cache["update"]-timenow)>cache["timeout"]:
                cache[cache_target] = (timenow,data)
            else:
                cache[cache_target] = (cache["update"]-cache["timeout"],data)
            return data
    
    def select_k_data(self,ts_code,period=60,order='desc'):
        """
        返回k线数据 [date,ts_code,open,close,high,low,vol]
        """
        timenow = dt.now()
        cache = self.k_cache
        cache_target = "_".join([ts_code,str(period),order])        
        if cache_target in cache and timenow-cache[cache_target][0]<cache['timeout']:            
            return cache[cache_target][1]
        if self.cursor:
            data = self._exe("select * from k_data where ts_code=\"{}\"\
                    order by date {} limit {};".format(ts_code,order,period))
            self.next_udt()
            if (cache["update"]-timenow)>cache["timeout"]:
                cache[cache_target] = (timenow,data)
            else:
                cache[cache_target] = (cache["update"]-cache["timeout"],data)
            return data

    def select_latest(self):
        """
        返回latest数据 [[code,senti]...]
        """
        timenow = dt.now()
        cache = self.l_cache
        cache_target = "0"       
        if cache_target in cache and timenow-cache[cache_target][0]<cache['timeout']:            
            return cache[cache_target][1]
        if self.cursor:
            data = self._exe("select code,senti from latest")
            self.next_udt()
            if (cache["update"]-timenow)>cache["timeout"]:
                cache[cache_target] = (timenow,data)
            else:
                cache[cache_target] = (cache["update"]-cache["timeout"],data)
            return data

    def select_words(self):
        res = self.select(table="words",limit=1)
        if res: return [x.split("_") for x in res[0][1].split("|")]

class TextModel():    
    def __init__(self,path='data/'):
        self.clf = joblib.load(path+'clf')
        self.vectorizer = joblib.load(path+'vect')
        self.transformer = joblib.load(path+'tfidf')
        jieba.analyse.set_stop_words(path+"stop_words.txt")

    def predict(self,data):
        """
        返回（预测结果str，4类概率[中，无，消极，积极]）
        """
        text_predict=numpy.array([" ".join([x for x in jieba.cut(data, cut_all=1) if x!=''])])
        text_frequency = self.vectorizer.transform(text_predict)
        new_tfidf = self.transformer.transform(text_frequency)
        predicted = self.clf.predict(new_tfidf)[0]
        predicted_score = self.clf.predict_proba(new_tfidf)[0]
        return predicted,predicted_score
    
    def textrank(self,data,k,scope,exc=None):
        a = jieba.analyse.textrank(data, topK=k, withWeight=True, allowPOS=scope)
        if exc:a = [[*x] for x in a if x[0] not in stop_n]
        else:a = [[*x] for x in a]
        return sorted(a,key=lambda x:x[1],reverse=1)

def init_utils(connection): 
    db = DjangoDataBase(connection)
    to_tscode,to_name = {},{}
    for i in db._exe("select * from stock_list"):
        to_name[i[0]]=i[2]                          # ts_code->name
        to_tscode[i[1]]=i[0]                        # code->ts_code
        if i[2][0]=="*":to_tscode[i[2][1:]]=i[0]    # name->ts_code
        else:to_tscode[i[2]]=i[0]
    to_tscode["上证指数"]="000001.SH"
    to_name["000001.SH"]="000001"
    return db,to_tscode,to_name,TextModel()
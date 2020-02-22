
股票市场舆情文本分析系统 
===

### China Stock Market Text Sentiment Anlysis

本科毕业设计存档。利用网络爬虫从东方财富股吧自动提取文本数据，使用jieba分词、贝叶斯算法进行情感分析，给出市场、个股的舆情量化分数，使用MySQL存储数据，使用Django和ECharts进行可视化展示。

## 概览
![主页1](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/home.png)

![主页2](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/home2.png)

![交互演示](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/interact.png)

![个股](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/indiv.png)

![近期热点](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/hot.png)

![搜索](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/search.png)

![文本分析](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/text.png)

![文本分析](https://raw.githubusercontent.com/wangys96/Bayesian-Stock-Market-Sentiment/master/pic/text2.png)

## 依赖
```
Python>=3.6.0  
Django>=2.1.0  
requests>=2.19.0  
scikit-learn>=0.19  
tushare  
jieba  
mysqlclient  
```

## 文件目录
```
├── data  
│   ├── clf                  #贝叶斯模型  
│   ├── tfidf                #TF-IDF模型  
│   ├── vect                 #词频模型  
│   ├── worddict             #用户词典  
│   ├── stop_words.txt       #停用词词典   
├── InvisibleHand  
│   ├── settings.py          #项目配置  
│   ├── urls.py              #项目路由定义  
│   └── wsgi.py              #HTTP服务器的接口  
└── Sentiment  
    └── templates            #网页静态文件目录
        └── Sentiment  
            ├── home.js      #主页脚本  
            ├── 404.js       #未找到页面脚本  
            ├── search.js    #搜索页脚本  
            ├── hot.js       #近期热点页面脚本  
            ├── text.js      #文本分析页面脚本   
            ├── detial.js    #个股详情页面脚本  
            ├── global.js    #网站全局脚本  
            └── global.css   #网站全局样式  
    ├── static               #网页静态文件目录  
        └── Sentiment   
            ├── home.html    #主页模板  
            ├── 404.html     #未找到页面模板  
            ├── search.html  #搜索页模板  
            ├── hot.html     #近期热点页面模板  
            ├── text.html    #文本分析页面模板   
            └── detail.html  #个股详情页面模板  
    ├── admin.py             #Django后台的管理页面  
    ├── apps.py              #应用配置  
    ├── models.py            #数据模型定义  
    ├── urls.py              #路由设置  
    ├── views.py             #Django视图  
    ├── tests.py             #单元测试  
    └── front_utils.py       #数据访问模块、部分文本算法  
```

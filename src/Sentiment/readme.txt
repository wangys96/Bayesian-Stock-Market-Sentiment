本目录为 爬虫和Django网站view

|-- Sentiment/                   
    |-- templates/           #网页静态文件目录
        |-- Sentiment/
            |-- home.js      #主页脚本
            |-- 404.js       #未找到页面脚本
            |-- search.js    #搜索页脚本
            |-- hot.js       #近期热点页面脚本
            |-- text.js      #文本分析页面脚本 
            |-- detial.js    #个股详情页面脚本
            |-- global.js    #网站全局脚本
            |-- global.css   #网站全局样式
 
    |-- static/              #网页静态文件目录
        |-- Sentiment/
            |-- home.html    #主页模板
            |-- 404.html     #未找到页面模板
            |-- search.html  #搜索页模板
            |-- hot.html     #近期热点页面模板
            |-- text.html    #文本分析页面模板 
            |-- detail.html  #个股详情页面模板
    |-- admin.py             #Django后台的管理页面
    |-- apps.py              #应用配置
    |-- models.py            #数据模型定义
    |-- urls.py              #路由设置
    |-- views.py             #Django视图
    |-- tests.py             #单元测试
    |-- front_utils.py       #数据访问模块、部分文本算法

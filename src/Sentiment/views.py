from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db import connection
from . import front_utils as u

#初始化数据库连接、股票代码映射字典
db,to_tscode,to_name,tm = u.init_utils(connection)

def home(request):
    '''
    主页视图
    '''
    stock_data = db._tolist(db.select_k_data('000001.SH',60),True)
    senti24h_data = db._tolist(db.select_s_data("gssz",False,24),True)
    senti60d_data = db._tolist(db.select_s_data("gssz",True,120),True)
    kset=set(x[0] for x in stock_data)
    f = [x for x in senti60d_data if x[0] in kset]
    return render(request, "home.html",
        {"stock_data":stock_data,"senti60d_data":f,"senti24h_data":senti24h_data})

def detail(request,code):
    '''
    详情视图
    '''
    try:
        name = to_name[to_tscode[code]]
    except:
        return render(request,"404.html",{"search_target":code},status="404")
    stock_data = db._tolist(db.select_k_data(to_tscode[code],60),True)
    senti24h_data = db._tolist(db.select_s_data(code,False,24),True)
    senti60d_data = db._tolist(db.select_s_data(code,True,120),True)
    kset=set(x[0] for x in stock_data)
    f = [x for x in senti60d_data if x[0] in kset]
    return render(request, "detail.html",{'title':"{}({})".format(name,code),
        "stock_data":stock_data,"senti60d_data":f,"senti24h_data":senti24h_data})

def hot(request):
    '''
    热点视图
    '''    
    data = []
    hot_list=u.get_hotlist()    
    senti24h_data = {c:s for c,s in db.select_latest()}
    for i in hot_list:
        if i[0] in to_tscode:
            stock_data = db._tolist(db.select_k_data(to_tscode[i[0]],1))            
            if len(stock_data)>0:
                data.append([i[0],i[1],stock_data[0][2], stock_data[0][3],senti24h_data.setdefault(i[0],-1)]) 
        else:
            data.append([i[0],i[1],-1,-1,-1]) 
    words = db.select_words()
    return render(request, "hot.html",{"table_data":data,"wordcloud_data":words})

def search(request):
    '''
    搜索视图
    '''
    if 'target' not in request.GET:#search页面
        hot_list=u.get_hotlist()
        return render(request, "search.html",{"hot_data":hot_list})
    #search跳转
    target = str(request.GET['target']).strip()
    if target in to_tscode: 
        if target=="上证指数" or target=="上证综指":
            return redirect('detail/szzs')
        return redirect('detail/{}'.format(to_tscode[target][:6]))
    #搜索不合法
    return render(request,"404.html",{"search_target":target},status="404")

def text(request):
    if request.method == 'POST' and request.POST['textdata']:
        data = str(request.POST['textdata'])
        k = request.POST['topk']
        
        if len(k)>3:k=5
        else:k=int(k)
        scope,param=[],[k,0,0]
        if 'n' in request.POST:
            scope.extend(['an','n'])
            param[1]=1
        if 'v' in request.POST:
            scope.extend(['vd','v'])
            param[2]=1
        if not len(scope): 
            scope=['an','v','vd']
            param[1],param[2]=1,1
        res,score = tm.predict(data)
        words = tm.textrank(data,k,scope)
        return render(request,"text.html",{"result_data":[res,*score],"text":data,"param":param,"words":words})
    return render(request,"text.html",{"result_data":[],"param":[]})



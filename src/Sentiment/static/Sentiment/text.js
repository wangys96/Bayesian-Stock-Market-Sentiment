result=document.getElementById("result");
if(rdata.length==5){
    if(rdata[0]=="中立"||rdata[0]=="无立场"){
        result.innerHTML+="<h4>贝叶斯文本情感分类：中立/无关</h4>";
    }
    else if(rdata[0]=="积极"){
        result.innerHTML+="<h4>贝叶斯文本情感分类：<font class=\"text-danger\">"+rdata[0]+"</font></h4>";
    }
    else if(rdata[0]=="消极"){
        result.innerHTML+="<h4>贝叶斯文本情感分类：<font class=\"text-success\">"+rdata[0]+"</font></h4>";
    }
    result.innerHTML+="\
    <h6>积极</h6>\
    <div class=\"progress\" style=\"height:20px;\">\
        <div class=\"progress-bar progress-bar-striped bg-danger progress-bar-animated\" role=\"progressbar\" style=\"width:"+(rdata[4]*100).toFixed(2)+"%\">"+(rdata[4]*100).toFixed(2)+"%</div>\
    </div>\
    <h6>消极</h6>\
    <div class=\"progress\" style=\"height:20px;\">\
        <div class=\"progress-bar progress-bar-striped bg-success progress-bar-animated\" role=\"progressbar\" style=\"width:"+(rdata[3]*100).toFixed(2)+"%\">"+(rdata[3]*100).toFixed(2)+"%</div>\
    </div>\
    <h6>中立/无关</h6>\
    <div class=\"progress\" style=\"height:20px;\">\
        <div class=\"progress-bar progress-bar-striped bg-secondary progress-bar-animated\" role=\"progressbar\" style=\"width:"+((rdata[1]+rdata[2])*100).toFixed(2)+"%\">"+((rdata[1]+rdata[2])*100).toFixed(2)+"%</div>\
    </div>\
    ";
}
if(param.length==3){
    if(param[0]==5){document.getElementById("inlineFormCustomSelect").selectedIndex=1}
    else if(param[0]==10){document.getElementById("inlineFormCustomSelect").selectedIndex=2}
    else if(param[0]==15){document.getElementById("inlineFormCustomSelect").selectedIndex=3}
    else if(param[0]==20){document.getElementById("inlineFormCustomSelect").selectedIndex=4}
    if(param[1]==1){document.getElementById("cn").checked=true;}
    if(param[2]==1){document.getElementById("cv").checked=true;}
}else{
    document.getElementById("cn").checked=true;
    document.getElementById("cv").checked=true;
}
if(wdata.length>0){
    result.innerHTML+=("<hr><h4>TextRank关键词提取：</h4>");
    for(var i=0,len=wdata.length;i<len;i++){
        result.innerHTML+=("<p>"+wdata[i][0]+" "+wdata[i][1].toFixed(2)+"</p>");
    }    
}
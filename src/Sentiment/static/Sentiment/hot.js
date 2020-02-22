var target = document.getElementById("hot_list");
var html="<tbody style=\"font-size:16px\">";
var name,price,pcolor,senti,scolor;
//[600001,"中国平安",open,close,55.55]
for(var i=0,len=tdata.length;i<len;i++){
    name=tdata[i][1]+"("+tdata[i][0]+")";
    if(tdata[i][4]==-1){
        senti="-";
        scolor="";
    }
    else{
        senti=(tdata[i][4]*100).toFixed(2)+"%";
        if(tdata[i][4]>0.5){scolor="text-danger";}else{scolor="text-success";}
    }    
    if(tdata[i][2]==-1&&tdata[i][3]==-1){
        html+="<tr><th scope=\"row\">"+String(i+1)+"</th>"+
            "<td><a href=\"detail/"+tdata[i][0]+"\" class=\"alert-link\">"+name+"</a></td>"+
            "<td>--</td>"+
            "<td class=\""+scolor+"\">"+senti+"</td></tr>";
            continue;
    }
    price=tdata[i][3].toFixed(2)+" ("+(tdata[i][3]-tdata[i][2]).toFixed(2)+")";
    if(tdata[i][3]>tdata[i][2]){pcolor="text-danger";}else{pcolor="text-success";}
    
    html+="<tr><th scope=\"row\">"+String(i+1)+"</th>"+
            "<td><a href=\"detail/"+tdata[i][0]+"\" class=\"alert-link\">"+name+"</a></td>"+
            "<td class=\""+pcolor+"\">"+price+"</td>"+
            "<td class=\""+scolor+"\">"+senti+"</td></tr>";
}
html+="</tbody>";
target.innerHTML+=html;

var wdata=[];
for(var i=0,len=wdata_raw.length;i<len;i++){
    wdata[i]={name:wdata_raw[i][0],value:Number(wdata_raw[i][1])};
}
var WChart = echarts.init(document.getElementById('echarts_wc'));
woption = {
    title: {
        text: '热点词汇',//标题
        left:10,
        textStyle: {
            fontSize: 20
        }
 
    },
    backgroundColor: "#FFF",
    tooltip: {
        show: true
    },
    toolbox: {
        feature: {
            saveAsImage:{},  
            dataView: {}
        }
    },
    series: [{
        name: '热点分析',//数据提示窗标题
        type: 'wordCloud',
        gridSize:6,
        sizeRange: [12, 100],//画布范围，如果设置太大会出现少词（溢出屏幕）
        rotationRange: [0,0],//数据翻转范围
        height:400,
        textPadding: 0,
        autoSize: {
            enable: true,
            minSize: 20
        },
        textStyle: {
            normal: {
                color: function() {
                    return 'rgb(' + [
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160)
                    ].join(',') + ')';
                }
            },
            emphasis: {
                shadowBlur: 10,
                shadowColor: '#333'
            }
        },
        data: wdata
    }]
};
WChart.setOption(woption, true);
window.onresize = function() {  
    WChart.resize();
};
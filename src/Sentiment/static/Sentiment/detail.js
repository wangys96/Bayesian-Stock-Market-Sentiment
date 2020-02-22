//K线图
var kdom = document.getElementById("echarts_k");
var KChart = echarts.init(kdom);
var krange=0;
for(var j=0,len1=kdata.length;j<len1;j++){for(var c=0;c<5;c++){kdata[j].push("-");}}   
for (var i=0,len=sdata.length;i<len; i++) {
    for(var j=0,len1=kdata.length;j<len1;j++){
        if(sdata[i][0]==kdata[j][0]){
            if(Math.max(Math.abs(sdata[i][3]),sdata[i][2])>krange){krange=Math.max(Math.abs(sdata[i][3]),sdata[i][2]);}
            kdata[j][7]=(sdata[i][2]); //积极 7
            kdata[j][8]=(-sdata[i][3]);//8
            kdata[j][9]=(sdata[i][5].toFixed(2)); //积极概率 9
            kdata[j][10]=(sdata[i][6].toFixed(2)); //10
            kdata[j][11]=((sdata[i][5]/(sdata[i][5]+sdata[i][6])*100).toFixed(2));//11
            break;
        }
    }
} 
var koption = {
      dataset: {
          source: kdata
      },
      title: {
          left:'1%',
          text:ktitle,
          textStyle:{
              left:20,
              align: 'center'
            }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross'
        },
        backgroundColor: 'rgba(245, 245, 245, 0.8)',
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        textStyle: {
            color: '#000'
        }

        // extraCssText: 'width: 170px'
      },
      axisPointer: {
        link: {xAxisIndex: 'all'},
        label: {
            backgroundColor: '#777'
        }
      },
      toolbox: {
          right:10,
          feature: {
              saveAsImage:{},
              dataZoom: {yAxisIndex: false},
              restore:{},
              dataView:{},                  
          }
      },
      grid: [
          {
            top:50,  
            left: '5%',
            right: '5%',
            bottom: 300
          },
          {
              left: '5%',
              right: '5%',
              height: 200,
              bottom: 50
          }
      ],
      xAxis: [
          {
              type: 'category',
              scale: true,
              boundaryGap : false,
              axisLine: {onZero: false},
              splitLine: {show: false},
              splitNumber: 20,
              min: 'dataMin',
              max: 'dataMax'
          },
          {
              type: 'category',
              gridIndex: 1,
              scale: true,
              boundaryGap : false,
              axisLine: {onZero: false},
              axisTick: {show: false},
              splitLine: {show: false},
              axisLabel: {show: false},
              splitNumber: 20,
              min: 'dataMin',
              max: 'dataMax'
          }
      ],
      yAxis: [
          {
              scale: true,
              splitArea: {
                  show: true
              }
          },
          {
            gridIndex: 1,
            inverse: false,
            splitArea: {show: false},
            min:-krange-5,
            max:krange+5
          },
          {
              gridIndex: 1,
              type: 'value',
              max: 100,
              min: 0,
          },
      ],
      dataZoom: [
          {
              type: 'inside',
              xAxisIndex: [0, 1],
              start: 0,
              end: 100
          },
          {
              show: true,
              xAxisIndex: [0, 1],
              type: 'slider',
              bottom: 10,
              start: 0,
              end: 100,
              handleIcon: 'M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
              handleSize: '105%'
          }
      ],
      series: [
          {
              type: 'candlestick',
              encode: {
                  x: 0,
                  // [o, c, h ,l]
                  y: [2, 3, 4, 5]
              }
          },
          {
              name: 'MA5',
              type: 'line',
              data: calculateMA(5,kdata,3),
              smooth: true,
              lineStyle: {
                  normal: {opacity: 0.5}
              }
          },
          {
              name: '看涨',
              type: 'bar',
              stack: 'one',
              xAxisIndex: 1,
              yAxisIndex: 1,
              itemStyle: {
                  color:'#c23531'
              },
              emphasis: {
                itemStyle: {
                    barBorderWidth: 1,
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowOffsetY: 0,
                    shadowColor: 'rgba(0,0,0,0.5)'
                }  
            },           
              encode: {
                  x: 0,
                  y: 7
              }
          },
          {
              name: '看跌',
              type: 'bar',
              stack: 'one',
              xAxisIndex: 1,
              yAxisIndex: 1,
              itemStyle: {
                  color:'#2f4954',
              },
              emphasis: {
                  itemStyle: {
                      barBorderWidth: 1,
                      shadowBlur: 10,
                      shadowOffsetX: 0,
                      shadowOffsetY: 0,
                      shadowColor: 'rgba(0,0,0,0.5)'
                  }  
              },            
              encode: {
                  x: 0,
                  y: 8
              }
          },
          {
              name: '贝叶斯上涨概率',
              type: 'line',
              smooth: true,
              xAxisIndex: 1,
              yAxisIndex: 2,
              itemStyle: {
                  color: '#6AB0B8'
              },
              encode: {
                  x: 0,
                  y: 11
              }
          }
      ]
  };
KChart.setOption(koption, true);

//柱形图
var bdom = document.getElementById("echarts_b");
var BChart = echarts.init(bdom);
var up=0,down=0,neu=0;
var p_up=0,p_down=0,p_neu=0,range=0;
for (var i=0,len=bdata.length;i<len; i++) {
    if(Math.max(Math.abs(bdata[i][3]),bdata[i][2])>range){range=Math.max(Math.abs(bdata[i][3]),bdata[i][2]);}        
    bdata[i][3]=-bdata[i][3];
    bdata[i].push((bdata[i][5]/(bdata[i][5]+bdata[i][6])*100).toFixed(2));
    up+=bdata[i][2];
    down+=bdata[i][3];
    neu+=bdata[i][4];
    p_up+=bdata[i][5];
    p_down+=bdata[i][6];
    p_neu+=bdata[i][7];
}  
var boption = {
    title:{
        text:btitle,
        left:'1%',
        textStyle:{
          left:20,  
          align: 'center'
        }
    },
    dataset: {
        source: bdata
    },
    legend: {
        data: ['看涨', '看跌'],
        align: 'left',
        bottom: 10
    },
    brush: {
        toolbox: ['lineX', 'clear'],
        xAxisIndex: 0
    },
    toolbox: {
        feature: {
            saveAsImage:{},  
            magicType: {
                type: ['stack', 'tiled']
            },
            dataView: {}
        }
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross'
        },
        backgroundColor: 'rgba(245, 245, 245, 0.8)',
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        textStyle: {
            color: '#000'
        },
    },
    xAxis: {
        nameGap:5,
        type: 'category',
        silent: false,
        axisLine: {onZero: true},
        splitLine: {show: false},
        splitArea: {show: false}
    },
    yAxis: [
      {
        inverse: false,

        min:-range-5,
        max:range+5
      },
      {
        gridIndex: 0,
        type: 'value',
        max: 100,
        min: 0
      },
    ],
    grid: {
        left: '5%',
        right: '5%',
        top:40
    },
    series: [
        {
            name: '看涨',
            type: 'bar',
            stack: 'one',
            itemStyle: {
                color:'#c23531',
                normal: {},
                emphasis: {
                    barBorderWidth: 1,
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowOffsetY: 0,
                    shadowColor: 'rgba(0,0,0,0.5)'
                }
            },
            encode: {
                x: 0,
                y: 2
            }
        },
        {
            name: '看跌',
            type: 'bar',
            stack: 'one',
            itemStyle: {
                color:'#2f4954',
                normal: {},
                emphasis: {
                    barBorderWidth: 1,
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowOffsetY: 0,
                    shadowColor: 'rgba(0,0,0,0.5)'
                }
            },
            encode: {
                x: 0,
                y: 3
            }
        },
        {
            name:"贝叶斯上涨概率",
            type:'line',
            animation: false,
            yAxisIndex:1,
            smooth: true,
            itemStyle: {
                color: '#6AB0B8'
            },
            encode:{
                x:0,
                y:8
            }
        }
    ]
};
BChart.setOption(boption, true);

//饼图
var pdom = document.getElementById("echarts_p");
var PChart = echarts.init(pdom);
poption = {
  tooltip: {
      trigger: 'item',
      formatter: "{a} <br/>{b}: {c} ({d}%)"
  },
  legend: {
      orient: 'vertical',
      x: 'right',
      data:['看涨','看跌','中性']
  },
  grid: {
    left: '5%',
    right: '5%'
 },
  series: [
      {
          name:'舆情统计',
          type:'pie',
          radius: ['50%', '80%'],
          avoidLabelOverlap: false,
          label: {
              normal: {
                  show: false,
                  position: 'center'
              },
              emphasis: {
                  show: true,
                  textStyle: {
                      fontSize: '30',
                      fontWeight: 'bold'
                  }
              }
          },
          labelLine: {
              normal: {
                  show: false
              }
          },
          data:[
              {value:up, name:'看涨'},//,selected:Boolean(up+down>0)},
              {value:-down, name:'看跌'},//,selected:Boolean(-down-up>0)},
              {value:neu, name:'中性'}//,selected:false},
          ]
      }
  ]
};
PChart.setOption(poption, true);

//最后，自动调整尺寸
window.onresize = function() {  
    KChart.resize();  
    BChart.resize();
    PChart.resize();
};

//修改标题
up_rate=(p_up/(p_up+p_down)*100).toFixed(2);
up_prog = document.getElementById("up_prog");
up_prog.innerText=String(up_rate)+"%";
up_prog.style.width=String(up_rate)+"%";

down_rate=(p_down/(p_up+p_down)*100).toFixed(2);
down_prog = document.getElementById("down_prog");
down_prog.innerText=String(down_rate)+"%";
down_prog.style.width=String(down_rate)+"%";

title=document.getElementById("titledom");
if (p_up>=p_down){
  title.innerHTML+='：<font class="text-danger">看涨📈</font>';
}else{
  title.innerHTML+='：<font class="text-success">看跌📉</font>';
}

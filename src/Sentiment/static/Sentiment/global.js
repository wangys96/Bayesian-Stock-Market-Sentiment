function search_check_top(){
    var target = document.getElementById("search_input_top").value;
    if(target ==  null || target == ''){
        alert("请输入有效名称或代码");
        return false;
    }
    return true;
}

function search_check(){
    var target = document.getElementById("search_input").value;
    if(target ==  null || target == ''){
        alert("请输入有效名称或代码");
        return false;
    }
    return true;
}

function format_data(data) {
    var final_data = [];
    for (var i=0,len=data.length;i<len; i++) {
      final_data[i]=[
        echarts.format.formatTime('yyyyMMdd', String(data[i][0])),
        data[i][1].toFixed(2), // open
        data[i][2].toFixed(2), // highest
        data[i][3].toFixed(2), // lowest
        data[i][4].toFixed(2),  // close
        data[i][5].toFixed(0)];
    }       
    return final_data;
  }

function calculateMA(dayCount,data,index) {
    var result = [];
    for (var i = 0, len = data.length; i < len; i++) {
        if (i < dayCount) {
        result.push('-');
        continue;
        }
        var sum = 0;
        for (var j = 0; j < dayCount; j++) {
        sum += data[i - j][index];
        }
        result.push((sum / dayCount).toFixed(2));
    }
    return result;
}


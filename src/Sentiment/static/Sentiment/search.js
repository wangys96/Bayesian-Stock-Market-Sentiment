function render_table(data,dom_id,col=6){
    var target = document.getElementById(dom_id);
    var html="<tbody>";
    //[600001,"中国平安",open,close,55.55]
    for(var i=0,len=col-1;i<len;i++){
        name=data[i][1]+"("+data[i][0]+")";
        html+="<td><a href=\"detail/"+data[i][0]+"\" class=\"link\">"+name+"</a></td>";
    }
    html+="<td><a href=\"/hot\" class=\"link\">更多...</a></td></tbody>";
    target.innerHTML+=html;
}
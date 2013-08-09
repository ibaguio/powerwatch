//refreshes the dashboard info every few seconds

window.pdu_count = 1;
function ajaxRequest(){
    var xmlhttp;
    if (window.XMLHttpRequest)// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    else// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    return xmlhttp;
}
function requestInfo(pdu){
    var xmlhttp = ajaxRequest();
    xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState === 4){
            if (xmlhttp.status === 200){
                var jdata=JSON.parse(xmlhttp.responseText);
                $("td#stat_pdu_"+pdu).text(jdata['status'])
                $("td#uptime_pdu_"+pdu).text(jdata['uptime'])
                $("td#cons_pdu_"+pdu).text(jdata['consumption'])
            }else{
            }
        }
    }
    xmlhttp.open("GET","/pdu/info/"+pdu);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.send();
}
function setCount(count){
   window.pdu_count = count
}
window.setInterval(function refresh(){
   for (var pdu_ = 1 ; pdu_ <= window.pdu_count; pdu_++) {
      requestInfo(pdu_);
   };
},5000)

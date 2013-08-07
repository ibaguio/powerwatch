/*$(function() {
  $.get('http://localhost:5000/card', function(data) {


    /*$("#test").html(data); //render template data
    //create cards + link with ahref link
  });
  return false;
});*/

$('tr.clickable').click(function () {
   var url = $(this).find('a:first').attr('href');
   window.location.href = url;
});
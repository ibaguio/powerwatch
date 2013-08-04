$(function() {
  $.get('http://localhost:5000/card', function(data) {


    $("#test").html(data); //render template data
    //create cards + link with ahref link
  });
  return false;
});
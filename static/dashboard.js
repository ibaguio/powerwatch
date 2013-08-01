$(function() {
  $.get('http://localhost:5000/card', function(data) {
    $("#test").html(data);
  });
  return false;
});
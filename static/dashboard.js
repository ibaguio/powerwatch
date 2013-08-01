$(function() {
  $.get('http://localhost:5000/card', function(data) {
    $("#test").text(data);
  });
  return false;
});


function del_cal(pic, e) {
//var target = e.target, 
url = "/pycgi/del_cal.py?file=" + pic 

fetch(url) 
   .then(function(response) {
      return response.json();
   })
   .then(function(myJson) {
      console.log(myJson);
   }) 
   .catch(function(error) {
      alert(error)
      console.log(error)
   })

}




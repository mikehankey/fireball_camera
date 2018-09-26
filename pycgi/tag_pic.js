

function tag_pic(pic, tag, e) {

var target = e.target, 
    status = e.target.classList.contains('active');
url = "tag.py?file=" + pic + "&status=" + status + "&tag=" + tag
e.target.classList.add(status ? 'inactive' : 'active');
e.target.classList.remove(status ? 'active' : 'inactive');

fetch(url) // Call the fetch function passing the url of the API as a parameter
.then(function() {
    // Your code for handling the data you get from the API
})
.catch(function() {
    // This is where you run code if the server returns any errors
});

}



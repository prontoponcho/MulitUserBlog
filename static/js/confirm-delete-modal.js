// Get the modal
var modal = document.getElementById('myModal');

// Get the button that opens the modal
var yes_button = document.getElementById("yes-button");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When page loads, open the modal 
window.onload = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// When the user clicks "yes" button, show redirecting
yes_button.onclick = function() {
	var message_div = document.getElementById("message");
	message_div.innerHTML = "Content deleted. Redirecting to front page...";
}
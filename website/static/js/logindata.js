if (!("librarian" in localStorage)) {
		localStorage["librarian"] = "Junior";
}
document.getElementById("librarian").value = localStorage["librarian"];

function update_librarian(event) {
	console.log(event);
	console.log(this);
}
// takes data from server via socketio, to display events of in order of decreasing importance
sio.on("events", data => {
	console.log(data);
	//data = [{"text": "foo bar", "impact": "high", "library": "jnr"}, {"text": "baz", "impact": "low", "library": "snr"}]
	var ul = document.getElementById("list");
	ul.innerHTML = ""; // clear the current events, so that events are not display multiple times
	data.forEach(value => {
		var ul = document.getElementById("list");
		var li = document.createElement("li");
		li.appendChild(document.createTextNode(value["text"]));
		li.setAttribute("class", value["impact"] + "impact" + " " + value["library"] + "event");
		ul.appendChild(li);
	});
});

// set visibility of events, when a user toggles the clickbox
function toggleEvents(cb) {
	console.log(cb);
	var list = document.getElementsByClassName(cb.name);
	for (var i = 0; i < list.length; i++) {
		list[i].style.display = ["none", ""][cb.checked + 0];
	}
}

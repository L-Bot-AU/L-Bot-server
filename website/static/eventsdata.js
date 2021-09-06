sio.on("events", data => {
	console.log(data);
	//data = [{"text": "foo bar", "impact": "high", "library": "jnr"}, {"text": "baz", "impact": "low", "library": "snr"}]
	var ul = document.getElementById("list");
	ul.innerHTML = "";
	data.forEach(value => {
		var ul = document.getElementById("list");
		var li = document.createElement("li");
		li.appendChild(document.createTextNode(value["text"]));
		li.setAttribute("class", value["impact"] + "impact" + " " + value["library"] + "event");
		ul.appendChild(li);
	});
});

function toggleEvents(cb) {
	console.log(cb);
	var list = document.getElementsByClassName(cb.name);
	for (var i = 0; i < list.length; i++) {
		list[i].style.display = ["none", ""][cb.checked + 0];
	}
}
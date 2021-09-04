sio.on("events", data => {
	//data = [{"text": "foo bar", "impact": "high", "library": "jnr"}, {"text": "baz", "impact": "low", "library": "snr"}]
	var ul = document.getElementById("list");
	ul.innerHTML = "";
	data.forEach(value => {
		var ul = document.getElementById("list");
		var li = document.createElement("li");
		li.appendChild(document.createTextNode(value["text"]));
		li.setAttribute("class", value["impact"] + "impact");
		ul.appendChild(li);
	});
});
["jnr", "snr"].forEach(lib => {
	sio.on(lib + "Opening", data => {
		["monday", "tuesday", "wednesday", "thursday", "friday"].forEach(function (day) {
			document.getElementById(lib + day).innerHTML = data[day];
		});
	});
	
	sio.on(lib + "Max", data => {
		document.getElementById(lib + "max").innerHTML = data;
	});
	
	sio.on(lib + "Librarians", data => {
		data.forEach(function (librarian) {
			var ul = document.getElementById(lib + "librarians");
			var div = document.createElement("div");
			div.appendChild(document.createTextNode(librarian));
			ul.appendChild(div);
		});
	});
});
["jnr", "snr"].forEach(lib => {
	// takes data from server via socketio, to update the opening and closing times of each library
	sio.on(lib + "Opening", data => {
		["monday", "tuesday", "wednesday", "thursday", "friday"].forEach(function (day) {
			// opening and closing times are in seperate columns for spacing
			document.getElementById(lib + day + "opening").innerHTML = data[day]["opening"] + " - ";
			document.getElementById(lib + day + "closing").innerHTML = data[day]["closing"];
		});
	});
	
	// takes data from server via socketio, to update the maximum capacity of each library
	sio.on(lib + "Max", data => {
		document.getElementById(lib + "max").innerHTML = data;
	});
	
	// takes data from server via socketio, to update the names of librarians
	sio.on(lib + "Librarians", data => {
		data.forEach(function (librarian) {
			var ul = document.getElementById(lib + "librarians");
			var div = document.createElement("div");
			div.appendChild(document.createTextNode(librarian));
			ul.appendChild(div);
		});
	});
});

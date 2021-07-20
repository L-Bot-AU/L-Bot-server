["jnr", "snr"].forEach(lib => {
	sio.on(lib + "Opening", data => {
		console.log(data);
		["mon", "tue", "wed", "thu", "fri"].forEach(function (day) {
			document.getElementById(lib + day).innerHTML = data[day];
		});
	});
	
	sio.on(lib + "Max", data => {
		console.log(data);
		document.getElementById(lib + "max").innerHTML = data;
	});
	
	sio.on(lib + "Librarians", data => {
		console.log(data);
		data.forEach(function (librarian) {
			var ul = document.getElementById(lib + "librarians");
			var div = document.createElement("div");
			div.appendChild(document.createTextNode(librarian));
			ul.appendChild(div);
		});
	});
});
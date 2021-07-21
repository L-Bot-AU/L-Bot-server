var HOVERCOLOUR = [
	"rgba(255, 99, 132, 1)",
	"rgba(54, 162, 235, 1)",
	"rgba(85, 214, 64, 1)",
	"rgba(75, 192, 192, 1)",
	"rgba(153, 102, 255, 1)",
	"rgba(255, 159, 64, 1)"
];
var BACKGROUNDCOLOUR = [
	"rgba(255, 99, 132, 0.2)",
	"rgba(54, 162, 235, 0.2)",
	"rgba(85, 214, 64, 0.2)",
	"rgba(75, 192, 192, 0.2)",
	"rgba(153, 102, 255, 0.2)",
	"rgba(255, 159, 64, 0.2)"
];
var BORDERCOLOUR = [
	"rgba(255, 99, 132, 1)",
	"rgba(54, 162, 235, 1)",
	"rgba(85, 214, 64, 1)",
	"rgba(75, 192, 192, 1)",
	"rgba(153, 102, 255, 1)",
	"rgba(255, 159, 64, 1)"
];


// initialise graph
var isFirstLoad = {"jnr": true, "snr": true};
window.graphData = {};
window.predictionGraph = {};
["jnr", "snr"].forEach(function(lib) {
	var ctx = document.getElementById(lib + "Predictions").getContext("2d");
	window.predictionGraph[lib] = new Chart(ctx, {
		type: "bar",
		data: {
			labels: [],
			datasets: []
		},
		options: {
			legend: {
				display: false
			},
			scales: {
				yAxes: [{
					ticks: {
						beginAtZero: true,
						max: 100
					}
				}]
			},
			responsiveAnimationDuration: 0,
			responsive: true,
			maintainAspectRatio: false
		}
	});
});

// handle sio events
["jnr", "snr"].forEach(lib => {
	sio.on(lib + "Periods", data => {
		//console.log(data);
		
		var table = document.getElementById(lib + "Periods");
		table.innerHTML = "<tr><th>Period</th><th> Expected</th></tr>";
		data.forEach(val => {
			if (val[0].length === 1) {
				val[0] = "Period " + val[0];
			}
			var tr = document.createElement("tr");
			
			var td1 = document.createElement("td");
			td1.setAttribute("class", "periodText");
			td1.appendChild(document.createTextNode(val[0]));
			
			var td2 = document.createElement("td");
			td2.setAttribute("class", "periodFullness");
			td2.appendChild(document.createTextNode(val[1]));
			
			tr.appendChild(td1);
			tr.appendChild(td2);
			
			table.appendChild(tr);
		});
	});
	sio.on(lib + "Alert", data => {
		//console.log(data);
		if (data !== "") {
			// nonzero alert
			document.getElementById(lib + "Alert").style.display = "visible";
			document.getElementById(lib + "Alerttext").innerHTML = data;
		}
		else {
			document.getElementById(lib + "Alert").style.display = "none";
		}
	});
	
	
	sio.on(lib + "Remaining", data => {
		//console.log(data);
		document.getElementById(lib + "Remaining").innerHTML = data;
	});
	
	sio.on(lib + "Fullness", data => {
		//console.log(data);
		if (data <= 30) {
			document.getElementById(lib + "Status").innerHTML = "Not busy:";
		}
		else if (data <= 70) {
			document.getElementById(lib + "Status").innerHTML = "Busy:";
		}
		else {
			document.getElementById(lib + "Status").innerHTML = "Very busy:";
		}
		
		if (data <= 12) {
			document.getElementById(lib + "Fullness").style.paddingLeft = "20px";
		}
		else {
			document.getElementById(lib + "Fullness").style.paddingLeft = "";
		}
		
		document.getElementById(lib + "Fullness").innerHTML = data + "% full";
		document.getElementById(lib + "Fullness").parentElement.style.width = data + "%";
	});
	
	sio.on(lib + "Trends", data => {
		//console.log(data);
		
		window.predictionGraph[lib].data.labels = data["labels"];
		for (let day = 0; day < 5; day++) {
			window.graphData[day] = {
				data: data["data"][day],
				pointHitRadius: 5,
				HoverBackgroundColor: HOVERCOLOUR[day],
				backgroundColor: BACKGROUNDCOLOUR[day],
				borderColor: BORDERCOLOUR[day],
				borderWidth: 3,
			};
		}
		
		if (isFirstLoad[lib]) {
			isFirstLoad[lib] = false;
			
			var today = new Date().getDay() - 1;
			if (today === -1 || today === 6) {
				// today is sunday or saturday respectively
				// view for monday instead
				today = 0;
			}
			displayGraph(lib, today);
		}
	});

	
});


// this function is called when a user clicks on a day
// it updates the graph to display that say
function displayGraph(lib, day){
	// underline the currently clicked button, un-underline the rest of the buttons
	for (let i = 0; i < 5; i++) {
		var curr = document.getElementsByClassName(lib + "daybtn")[i];
		if (i === day) {
			curr.classList.add("selected");
		}
		else {
			curr.classList.remove("selected");
		}
	}
	
	window.predictionGraph[lib].data.datasets[0] = window.graphData[day];
	window.predictionGraph[lib].update();
}

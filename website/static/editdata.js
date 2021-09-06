var currentDay = new Date().getDay() - 1;
if (currentDay == -1 || currentDay == 5) { // If today is Saturday or Sunday, set it to show Monday
	currentDay = 0;
}

// Get the select element for the day dropdown list and set it to today's value
var selectedDay = document.getElementById("day");
selectedDay.value = [...selectedDay.options].map(option => option.value)[currentDay];
changeTimes(day);

// Loop through each event and add onclick event handlers to each option for the impact
[...document.getElementById("events").children].forEach(event => {
	event.onclick = function() {
		window.currentSelected = event;
		document.querySelectorAll(".impact-choice").forEach(choice => {
			choice.onclick = function() {setImpact(choice)};
		});
	};
});

// Loop through each alert and add onclick event handlers to each option for the importance
[...document.getElementById("alerts").children].forEach(alert => {
	alert.onclick = function() {
		window.currentSelected = alert;
		document.querySelectorAll(".impact-choice").forEach(choice => {
			choice.onclick = function() {
				choice.onclick = setImportance(choice);
			}
		});
	}
});

// Enable the popovers of all required elements
var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
	return new bootstrap.Popover(popoverTriggerEl);
});

function setFocus(newFocus, obj) {
	document.getElementsByClassName("settab")[0].classList.remove("settab");
	obj.classList.add("settab");
	switch (newFocus) {
		case "general":
			document.body.classList.remove("focuscenter");
			document.body.classList.remove("focusright");
			break;
		case "events":
			document.body.classList.remove("focusright");
			document.body.classList.add("focuscenter");
			break;
		case "alerts":
			document.body.classList.remove("focuscenter");
			document.body.classList.add("focusright");
			break;
	}
}

function changeTimes(dayElement) {
	var day = dayElement.value.toLowerCase();
	var openingTime = document.getElementById("openingTime");
	var closingTime = document.getElementById("closingTime");
	openingTime.value = opening_times[day].map(num => String(num).padStart(2, '0')).join(":");
	closingTime.value = closing_times[day].map(num => String(num).padStart(2, '0')).join(":");
}

function changeOpening(openingElement) {
	var day = document.getElementById("day").value.toLowerCase();
	opening_times[day] = openingElement.value.split(":").map(num => parseInt(num));
}

function changeClosing(closingElement) {
	var day = document.getElementById("day").value.toLowerCase();
	closing_times[day] = closingElement.value.split(":").map(num => parseInt(num));
}

function addLibrarian() {
	var librarians = document.getElementById("librarians");
	var newLib = document.createElement("li");
	newLib.classList.add("edit-list-line", "bold-this");
	var libInput = document.createElement("input");
	libInput.classList.add("form-control", "edit-list");
	libInput.setAttribute("type", "text");
	var removeButton = document.createElement("button");
	removeButton.classList.add("btn", "btn-primary", "remove-button");
	removeButton.setAttribute("onclick", "this.parentElement.remove()");
	var removeIcon = document.createElement("i");
	removeIcon.setAttribute("style", "font-family: \'Font Awesome 5 Pro\' !important; color: white;");
	removeIcon.classList.add("fas", "fa-times-circle");
	removeButton.appendChild(removeIcon);
	removeButton.appendChild(document.createTextNode(" Remove"));
	newLib.appendChild(libInput);
	newLib.appendChild(document.createTextNode(" "));
	newLib.appendChild(removeButton);
	librarians.appendChild(newLib);
}

function addEvent() {
	var events = document.getElementById("events");
	var newEvent = document.createElement("li");
	newEvent.classList.add("edit-hover", "lowimpact", "bold-this");
	newEvent.setAttribute("data-bs-toggle", "popover");
	newEvent.setAttribute("data-bs-trigger", "focus");
	newEvent.setAttribute("data-bs-placement", "left");
	newEvent.setAttribute("data-bs-html", "true");
	newEvent.setAttribute("data-bs-content", "<ul class='list'><li class='highimpact impact-choice'></li><li class='moderateimpact impact-choice'></li><li class='lowimpact impact-choice'></li></ul>");
	var eventInput = document.createElement("input");
	eventInput.classList.add("form-control", "edit-event");
	eventInput.setAttribute("type", "text");
	var removeButton = document.createElement("button");
	removeButton.classList.add("btn", "btn-primary", "remove-button");
	removeButton.setAttribute("onclick", "this.parentElement.remove()");
	var removeIcon = document.createElement("i");
	removeIcon.setAttribute("style", "font-family: \'Font Awesome 5 Pro\' !important; color: white;");
	removeIcon.classList.add("fas", "fa-times-circle");
	removeButton.appendChild(removeIcon);
	removeButton.appendChild(document.createTextNode(" Remove"));
	newEvent.appendChild(eventInput);
	newEvent.appendChild(document.createTextNode(" "));
	newEvent.appendChild(removeButton);
	events.appendChild(newEvent);
	var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
	var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
	  return new bootstrap.Popover(popoverTriggerEl);
	});
	newEvent.onclick = function() {
		window.currentSelected = newEvent;
		document.querySelectorAll(".impact-choice").forEach(choice => {
			choice.onclick = function() {setImpact(choice)};
		});
	}
}

function addAlert() {
	var alerts = document.getElementById("alerts");
	var newAlert = document.createElement("li");
	newAlert.classList.add("form-inline", "bold-this");
	newAlert.setAttribute("data-bs-toggle", "popover");
	newAlert.setAttribute("data-bs-trigger", "focus");
	newAlert.setAttribute("data-bs-placement", "left");
	newAlert.setAttribute("data-bs-html", "true");
	newAlert.setAttribute("data-bs-content", "<div class='list'><span class='impact-choice'>⚠</span><br><span class='impact-choice'>ℹ</span><br></div>");
	var alertIcon = document.createElement("div");
	alertIcon.classList.add("alert-icon");
	alertIcon.appendChild(document.createTextNode("⚠"));
	var alertText = document.createElement("textarea");
	alertText.classList.add("form-control", "alert-box");
	var removeButton = document.createElement("button");
	removeButton.classList.add("btn", "btn-primary", "remove-button");
	removeButton.setAttribute("onclick", "this.parentElement.remove()");
	var removeIcon = document.createElement("i");
	removeIcon.setAttribute("style", "font-family: \'Font Awesome 5 Pro\' !important; color: white;");
	removeIcon.classList.add("fas", "fa-times-circle");
	removeButton.appendChild(removeIcon);
	removeButton.appendChild(document.createTextNode(" Remove"));
	newAlert.appendChild(alertIcon);
	newAlert.appendChild(alertText);
	newAlert.appendChild(document.createTextNode(" "));
	newAlert.appendChild(removeButton);
	alerts.appendChild(newAlert);
	var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
	var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
	  return new bootstrap.Popover(popoverTriggerEl);
	});
	newAlert.onclick = function() {
		window.currentSelected = newAlert;
		document.querySelectorAll(".impact-choice").forEach(choice => {
			choice.onclick = function() {
				choice.onclick = setImportance(choice);
			}
		});
	}
}

function setImpact(impactType) {
	window.currentSelected.className = impactType.classList[0];
}

function setImportance(importanceType) {
	window.currentSelected.children[0].innerHTML = importanceType.innerHTML;
}

function saveGeneral() {
	/* Code for manually sending a POST request: https://stackoverflow.com/questions/6396101/pure-javascript-send-post-data-without-a-form */
	var xhr = new XMLHttpRequest();
	var librarians = [];
	var max_seats = document.getElementById("maxSeats").value;
	[...document.getElementById("librarians").children].forEach(l => {
		librarians.push(l.children[0].value);
	});
	xhr.open("POST", "", true);
	xhr.setRequestHeader("Content-Type", "application/json");
	
	xhr.onreadystatechange = function() {
		if (this.readyState === 4 && this.status === 200) {
			showNotification("Your changes have been changed!");
		}
	}
	
	xhr.send(JSON.stringify({
		tab: "general",
		opening_times: opening_times,
		closing_times: closing_times,
		max_seats: parseInt(max_seats),
		librarians: librarians
	}));
}

function saveEvents() {
	var xhr = new XMLHttpRequest();
	var events = [];
	var event;
	var impact;
	[...document.getElementById("events").children].forEach(l => {
		if (l.classList.contains("lowimpact")) {
			impact = "low";
		} else if (l.classList.contains("moderateimpact")) {
			impact = "moderate";
		} else {
			impact = "high";
		}
		event = {
			impact: impact,
			event: l.children[0].value
		};
		events.push(event);
	});
	xhr.open("POST", "", true);
	xhr.setRequestHeader("Content-Type", "application/json");
	
	xhr.onreadystatechange = function() {
		if (this.readyState === 4 && this.status === 200) {
			showNotification("Your changes have been changed!");
		}
	}
	
	xhr.send(JSON.stringify({
		tab: "events",
		events: events
	}));
}

function saveAlerts() {
	var xhr = new XMLHttpRequest();
	var alerts = [];
	var alert;
	var importance;
	[...document.getElementById("alerts").children].forEach (l => {
		if (l.children[0].innerHTML === "⚠") {
			importance = "warning";
		} else {
			importance = "information";
		}
		alert = {
			importance: importance,
			alert: l.children[1].value
		};
		alerts.push(alert);
	})
	xhr.open("POST", "", true);
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.onreadystatechange = function() {
		if (this.readyState === 4 && this.status === 200) {
			showNotification("Your changes have been changed!");
		}
	}
	
	xhr.send(JSON.stringify({
		tab: "alerts",
		alerts: alerts
	}));
}

function showNotification(message) {
	console.log("a");
	var notif = document.getElementById("notification");
	console.log(notif);
	notif.hidden = false;
	notif.innerHTML = "<i style='font-family: \"Font Awesome 5 Pro\" !important; color: white;' class=\"fas fa-check-circle\"></i> " + message;
	setTimeout(function() {
	    notif.hidden = true;
	}, 3000);
	console.log(notif);
}
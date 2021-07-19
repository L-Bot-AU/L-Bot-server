let checkBox = document.getElementById("toggle-box-checkbox");

function setTheme(themeName) {
	localStorage.setItem('theme', themeName);
    document.documentElement.className = themeName;
}

checkBox.onclick = function() {
	let imgs = document.getElementsByTagName("img");
	if (checkBox.checked) {
		console.log("dark mode");
		setTheme('theme-dark');
		// for (let i = 0; i < imgs.length; ++i) {
		//     imgs[i].style.webkitFilter = "invert(100%)";
		// }
	}
	else {
		console.log("light mode");
		setTheme('theme-light');
		// for (let i = 0; i < imgs.length; ++i) {
		//     imgs[i].style.webkitFilter = "";
		// }
	}
}

// initialise to dark mode by default
if (localStorage.getItem("theme") === null) {
	localStorage.setItem("theme", "theme-dark")
}

checkBox.checked = (localStorage.getItem("theme") === "theme-dark");
checkBox.onclick();

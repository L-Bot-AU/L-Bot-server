let checkBox = document.getElementById("toggle-box-checkbox");

function setTheme(themeName) {
	localStorage.setItem('theme', themeName);
    document.documentElement.className = themeName;
}

checkBox.onclick = function() {
	// let imgs = document.getElementsByTagName("img");
	// console.log(imgs);
	if (checkBox.checked) {
		console.log("dark mode");
		setTheme('theme-dark');
		// for (let i = 0; i < imgs.length; ++i) {
		// 	imgs[i].style.webkitFilter = "invert(100%)";
		// }
	}
	else {
		console.log("light mode");
		setTheme('theme-light');
		// for (let i = 0; i < imgs.length; ++i) {
		// 	imgs[i].style.webkitFilter = "";
		// }
	}
	// console.log(imgs);

}
// checkBox.checked = true;
if (localStorage.getItem("theme") === null) localStorage.setItem("theme", "theme-dark")
checkBox.checked = (localStorage.getItem("theme") === "theme-dark");
checkBox.onclick();

function testing(){
	n = localStorage.getItem("thing");
	if (n === null){
		console.log("null");
		n = 0;
	} else {
		console.log(n);
		n++;
	}
	localStorage.setItem("thing", n);
}
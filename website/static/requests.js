// const host = "sr8137wxs02.win.sydneyboys-h.schools.nsw.edu.au";
const host = location.hostname;
// const host = "10.219.218.62";
// const host = "192.168.137.1";
const port = 2910;

function getReq(endpoint, func) {
    p = new Promise((resolve, reject) => {
		let sock = new WebSocket(`ws://${host}:${port}/${endpoint}`);
		sock.onmessage = function (event) {
			resolve(JSON.parse(event.data));
		}
    }).then(func);
}



/*
// todo enable cross origin resource sharing (CORS)?
const socket = io("ws://localhost:5000");

socket.on("connect", () => {
  // either with send()
  socket.send("Hello!");

  // or with emit() and custom event names
  socket.emit("salutations", "Hello!", { "mr": "john" });
});

// handle the event sent with socket.send()
socket.on("message", data => {
  console.log(data);
});

// handle the event sent with socket.emit()
socket.on("greetings", (elem1, elem2, elem3) => {
  console.log(elem1, elem2, elem3);
});

// function updateAll() {
//     libs = ["snr", "jnr"];
//     todo = ["Count"];
//     for (let i = 0; i < 2 ; i++){
//         for (let j = 0; j < 1; j++) {
//             getReq(libs[i] + todo[j], "updText");
//         }
//     }
// }
*/


/*function hardCode(){
    console.log("hardcoded data");
    window.graphData = {"labels": ["morning", "break 1", "break 2"], "data": [[0, 0, 10], [1, 4, 6], [1, 7, 2], [3, 7, 8], [1, 6, 9], [2, 5, 7]]};
}*/

const host = "127.0.0.1";
// const host = "10.219.218.62";
// const host = "192.168.137.1";
const port = 2910;

// todo enable cross origin resource sharing (CORS)?
const socket = io("ws://127.0.0.1:2910");

socket.on("connect", () => {
    console.log("connecting to socket.io server...");
  // either with send()
  // socket.send("Hello!");

  // or with emit() and custom event names
  socket.emit("staticdata");//maybe use send not emit
});

//// handle the event sent with socket.send()
// socket.on("message", data => {
//   console.log(data);
// });

// handle the event sent with socket.emit()
socket.on("countUpd", (lib, cnt) => {
  console.log("count upd:", lib, cnt);
  socket.emit("prediction");
});

socket.on("prediction", (lib, predictions) => {
    console.log("pred upd:", lib, predictions);
})

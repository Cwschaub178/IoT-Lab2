document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.123.132";   // the IP address of your Raspberry PI
var command = null; // To hold the current command being sent
var controlInterval; // To store the interval ID

function client(command){
    const net = require('net');

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // Send the command
        client.write(`${command}\r\n`);
    });
    
    // Handle response from the server
    client.on('data', (data) => {
        const response = data.toString();
        document.getElementById("bluetooth").innerHTML = response;
        console.log(response);
        updateInfo(response); // update displayed info
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });
}

function updateInfo(info) {
    const lines = info.split(', ');
    lines.forEach(line => {
        const [key, value] = line.split(': ');
        switch (key.trim()) {
            case "Direction":
                document.getElementById("direction").innerText = value;
                break;
            case "Speed":
                document.getElementById("speed").innerText = value;
                break;
            case "Distance":
                document.getElementById("distance").innerText = value;
                break;
            case "Temperature":
                document.getElementById("temperature").innerText = value;
                break;
        }
    });
}

// Function to handle the submit button
function submitMessage() {
    var input = document.getElementById("message").value; // Get value from input box
    if (input) {
        client(input); // Send the message
        document.getElementById("message").value = ""; // Clear the input box
    }
}

// for detecting which key is being pressed (W, A, S, D)
function updateKey(e) {
    e = e || window.event;

    if (controlInterval) return; // Prevent starting a new interval if already running

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        command = "87";
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        command = "83";
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        command = "65";
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        command = "68";
    }

    if (command) {
        // Send the command once
        client(command);
        // Set an interval to send the command every 100 ms while the key is held down
        controlInterval = setInterval(() => client(command), 100);
    }
}


// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    // Clear the interval and stop sending commands
    clearInterval(controlInterval);
    controlInterval = null;
    client("STOP"); // Stop car when key is released

    
}

// Function to send data to RPi
function send_data(command) {
    client(command);
}

// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}

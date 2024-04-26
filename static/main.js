var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('serialstatus', function(msg) {
    document.getElementById("serialstatus").innerText = "Serial status: "+msg;
});

function sendMessage() {
    var message = document.getElementById('message').value;
    socket.emit('message', message);
    document.getElementById('message').value = '';
}

// Function to check for gamepad support
function checkGamepadSupport() {
  return 'getGamepads' in navigator;
}

// Object to store the previous state of gamepad buttons and axes
var previousState = {};

// Function to handle gamepad connected event
function handleGamepadConnected(event) {
  console.log("Gamepad connected:", event.gamepad.id);
}

// Function to handle gamepad disconnected event
function handleGamepadDisconnected(event) {
  console.log("Gamepad disconnected:", event.gamepad.id);
}

// Function to handle gamepad button state change
function handleButtonStateChange(gamepad, buttonIndex) {
  var buttonState = gamepad.buttons[buttonIndex].pressed;
  var previousButtonState = previousState[gamepad.index].buttons[buttonIndex];
  
  if (buttonState !== previousButtonState) {
    console.log("Button", buttonIndex, "state changed:", buttonState);
    socket.emit("btn",[buttonIndex,buttonState])
    previousState[gamepad.index].buttons[buttonIndex] = buttonState;
  }
}

// Function to handle gamepad axis state change
function handleAxisStateChange(gamepad, axisIndex) {
  var axisValue = gamepad.axes[axisIndex];
  var previousAxisValue = previousState[gamepad.index].axes[axisIndex];
  
  if (axisValue !== previousAxisValue) {
    console.log("Axis", axisIndex, "value changed:", axisValue);
    socket.emit("axi",[axisIndex,axisValue])
    previousState[gamepad.index].axes[axisIndex] = axisValue;
  }
}

// Check for gamepad support
if (checkGamepadSupport()) {
  window.addEventListener("gamepadconnected", function(event) {
    handleGamepadConnected(event);
    previousState[event.gamepad.index] = {
      buttons: new Array(event.gamepad.buttons.length).fill(false),
      axes: new Array(event.gamepad.axes.length).fill(0)
    };
  });
  
  window.addEventListener("gamepaddisconnected", function(event) {
    handleGamepadDisconnected(event);
    delete previousState[event.gamepad.index];
  });

  // Function to continuously poll gamepad state
  function pollGamepads() {
    var gamepads = navigator.getGamepads();

    for (var i = 0; i < gamepads.length; i++) {
      var gamepad = gamepads[i];
      if (gamepad) {
        // Check button state changes
        for (var j = 0; j < gamepad.buttons.length; j++) {
          handleButtonStateChange(gamepad, j);
        }

        // Check axis state changes
        for (var k = 0; k < gamepad.axes.length; k++) {
          handleAxisStateChange(gamepad, k);
        }
      }
    }

    requestAnimationFrame(pollGamepads);
  }

  // Start polling gamepad state
  pollGamepads();
} else {
  console.log("Gamepad not supported");
}


// Function to handle keydown event
function handleKeyDown(event) {
    var keyCode = event.keyCode;
    var keyName = event.key;
    socket.emit('key',[keyCode,true])

    // Display key info
    document.getElementById("key-info").innerHTML = "Key Down: " + keyName + " (KeyCode: " + keyCode + ")";
}

// Function to handle keyup event
function handleKeyUp(event) {
    var keyCode = event.keyCode;
    var keyName = event.key;
    socket.emit('key',[keyCode,false])

    // Display key info
    document.getElementById("key-info").innerHTML = "Key Up: " + keyName + " (KeyCode: " + keyCode + ")";
}

// Add event listeners for keydown and keyup events
window.addEventListener("keydown", handleKeyDown);
window.addEventListener("keyup", handleKeyUp);
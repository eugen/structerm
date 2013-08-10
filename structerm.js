function Structerm() {
	var commandBar = document.getElementById("commandBar");
	var outputs = document.getElementById("outputs");

	commandBar.addEventListener("keypress", function(e) {
		switch(e.charCode) {
			case 13:
			window.external.ExecuteCommand(commandBar.value);
			break;
			default:
			break;
		}
	})

	// initialize handlers
	this.commandHandlers = {};

	for(var i = 0; i < Structerm.plugins.length; i++) {
		var plugin = Structerm.plugins[i];
		var instance = new plugin();
		for(var icom = 0; icom < plugin.commandsHandled.length; icom++) {
			this.commandHandlers[plugin.commandsHandled[icom]] = instance;
		}
	}
}

Structerm.plugins = [];

Structerm.prototype.renderOutput = function(cmd, output) {
	if(this.commandHandlers[cmd]) { 
		outputs.appendChild(this.commandHandlers[cmd].render(cmd, output))
	} else {
		var elem = document.createElement("pre");
		elem.textContent = output;
		outputs.appendChild(elem)
	}
}

window.onload = function() {
	window.sre = new Structerm();
}
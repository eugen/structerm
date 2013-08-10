function ProcessHandler() {

	var psTmpl = doT.template(document.getElementById("template_ps").innerHTML);

	this.render = function(cmd, output) {
		var divs = []
		for(var i = 0; i < output.length; i++) {
			divs.push(psTmpl(output[i]));
		}
		var div = document.createElement("div");
		div.innerHTML =  divs.join("");
		return div;
	}
}

ProcessHandler.commandsHandled = ["ps"]

Structerm.plugins.push(ProcessHandler);

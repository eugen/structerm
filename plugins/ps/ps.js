function ProcessHandler() {

	var psTmpl = doT.template(document.getElementById("template_ps").innerHTML);

	this.render = function(cmd, output) {
		var divs = []
		for(var i = 0; i < output.length; i++) {
			divs.push(psTmpl(output[i]));
		}
		var div = document.createElement("div");
		div.innerHTML = divs.join("");

		div.childNodes.forEach(function(procDiv) {
			procDiv.addEventListener("click", function() {
				var pid = procDiv.querySelector("input.pid").value;
				alert("killing process " + pid);
			});
		});

		return div;
	}
}

ProcessHandler.commandsHandled = ["ps"]

Structerm.plugins.push(ProcessHandler);

// Lollms Flow
// A library for building workflows of execution
// By ParisNeo
class WorkflowNode {
    constructor(id, name, inputs, outputs, operation, x = 0, y = 0) {
        this.id = id;
        this.name = name;
        this.inputs = inputs;
        this.outputs = outputs;
        this.operation = operation;
        this.inputConnections = {};
        this.outputConnections = {};
        this.x = x;
        this.y = y;
    }

    connect(outputIndex, targetNode, inputIndex) {
        if (!this.outputConnections[outputIndex]) {
            this.outputConnections[outputIndex] = [];
        }
        this.outputConnections[outputIndex].push({ node: targetNode, input: inputIndex });
        targetNode.inputConnections[inputIndex] = { node: this, output: outputIndex };
    }

    execute(inputs) {
        return this.operation(inputs);
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            inputs: this.inputs,
            outputs: this.outputs,
            x: this.x,
            y: this.y
        };
    }

    static fromJSON(json, operation) {
        return new WorkflowNode(json.id, json.name, json.inputs, json.outputs, operation, json.x, json.y);
    }
}

class Workflow {
    constructor() {
        this.nodes = {};
        this.nodeList = [];
    }

    addNode(node) {
        this.nodes[node.id] = node;
        this.nodeList.push(node);
    }

    connectNodes(sourceId, sourceOutput, targetId, targetInput) {
        const sourceNode = this.nodes[sourceId];
        const targetNode = this.nodes[targetId];
        if (this.canConnect(sourceNode, sourceOutput, targetNode, targetInput)) {
            sourceNode.connect(sourceOutput, targetNode, targetInput);
            return true;
        }
        return false;
    }

    canConnect(sourceNode, sourceOutput, targetNode, targetInput) {
        return sourceNode.outputs[sourceOutput].type === targetNode.inputs[targetInput].type;
    }

    execute() {
        const executed = new Set();
        const results = {};

        const executeNode = (node) => {
            if (executed.has(node.id)) return results[node.id];

            const inputs = {};
            for (let i = 0; i < node.inputs.length; i++) {
                if (node.inputConnections[i]) {
                    const { node: sourceNode, output } = node.inputConnections[i];
                    inputs[node.inputs[i].name] = executeNode(sourceNode)[sourceNode.outputs[output].name];
                }
            }

            results[node.id] = node.execute(inputs);
            executed.add(node.id);
            return results[node.id];
        };

        this.nodeList.forEach(node => {
            if (Object.keys(node.inputConnections).length === 0) {
                executeNode(node);
            }
        });

        return results;
    }

    toJSON() {
        return {
            nodes: this.nodeList.map(node => node.toJSON()),
            connections: this.nodeList.flatMap(node => 
                Object.entries(node.outputConnections).flatMap(([outputIndex, connections]) =>
                    connections.map(conn => ({
                        sourceId: node.id,
                        sourceOutput: parseInt(outputIndex),
                        targetId: conn.node.id,
                        targetInput: conn.input
                    }))
                )
            )
        };
    }

    static fromJSON(json, nodeOperations) {
        const workflow = new Workflow();
        json.nodes.forEach(nodeJson => {
            const node = WorkflowNode.fromJSON(nodeJson, nodeOperations[nodeJson.name]);
            workflow.addNode(node);
        });
        json.connections.forEach(conn => {
            workflow.connectNodes(conn.sourceId, conn.sourceOutput, conn.targetId, conn.targetInput);
        });
        return workflow;
    }
}

class WorkflowVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.workflow = new Workflow();
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.container.appendChild(this.svg);
        this.nodeElements = {};
        this.connectionElements = [];
        this.draggedNode = null;
        this.offsetX = 0;
        this.offsetY = 0;

        this.svg.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.svg.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.svg.addEventListener('mouseup', this.onMouseUp.bind(this));
    }

    addNode(node) {
        this.workflow.addNode(node);
        this.drawNode(node);
    }

    connectNodes(sourceId, sourceOutput, targetId, targetInput) {
        if (this.workflow.connectNodes(sourceId, sourceOutput, targetId, targetInput)) {
            this.drawConnection(sourceId, sourceOutput, targetId, targetInput);
        } else {
            console.error("Cannot connect incompatible types");
        }
    }

    drawNode(node) {
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("transform", `translate(${node.x}, ${node.y})`);
        g.setAttribute("data-id", node.id);

        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("width", "120");
        rect.setAttribute("height", "60");
        rect.setAttribute("fill", "lightblue");
        rect.setAttribute("stroke", "black");
        g.appendChild(rect);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "60");
        text.setAttribute("y", "35");
        text.setAttribute("text-anchor", "middle");
        text.textContent = node.name;
        g.appendChild(text);

        // Draw input sockets
        node.inputs.forEach((input, index) => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", "0");
            circle.setAttribute("cy", (index + 1) * 15);
            circle.setAttribute("r", "5");
            circle.setAttribute("fill", this.getColorForType(input.type));
            g.appendChild(circle);
        });

        // Draw output sockets
        node.outputs.forEach((output, index) => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", "120");
            circle.setAttribute("cy", (index + 1) * 15);
            circle.setAttribute("r", "5");
            circle.setAttribute("fill", this.getColorForType(output.type));
            g.appendChild(circle);
        });

        this.svg.appendChild(g);
        this.nodeElements[node.id] = g;
    }

    drawConnection(sourceId, sourceOutput, targetId, targetInput) {
        const sourceNode = this.workflow.nodes[sourceId];
        const targetNode = this.workflow.nodes[targetId];
        const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const sourcePosX = sourceNode.x + 120;
        const sourcePosY = sourceNode.y + (sourceOutput + 1) * 15;
        const targetPosX = targetNode.x;
        const targetPosY = targetNode.y + (targetInput + 1) * 15;
        const midX = (sourcePosX + targetPosX) / 2;

        const d = `M ${sourcePosX} ${sourcePosY} C ${midX} ${sourcePosY}, ${midX} ${targetPosY}, ${targetPosX} ${targetPosY}`;
        line.setAttribute("d", d);
        line.setAttribute("fill", "none");
        line.setAttribute("stroke", "black");
        this.svg.appendChild(line);
        this.connectionElements.push({ line, sourceId, sourceOutput, targetId, targetInput });
    }

    updateConnections() {
        this.connectionElements.forEach(conn => {
            const sourceNode = this.workflow.nodes[conn.sourceId];
            const targetNode = this.workflow.nodes[conn.targetId];
            const sourcePosX = sourceNode.x + 120;
            const sourcePosY = sourceNode.y + (conn.sourceOutput + 1) * 15;
            const targetPosX = targetNode.x;
            const targetPosY = targetNode.y + (conn.targetInput + 1) * 15;
            const midX = (sourcePosX + targetPosX) / 2;

            const d = `M ${sourcePosX} ${sourcePosY} C ${midX} ${sourcePosY}, ${midX} ${targetPosY}, ${targetPosX} ${targetPosY}`;
            conn.line.setAttribute("d", d);
        });
    }

    getColorForType(type) {
        const colors = {
            number: "blue",
            string: "green",
            boolean: "red",
            object: "purple"
        };
        return colors[type] || "gray";
    }

    onMouseDown(event) {
        const target = event.target.closest("g");
        if (target) {
            this.draggedNode = this.workflow.nodes[target.getAttribute("data-id")];
            const rect = target.getBoundingClientRect();
            this.offsetX = event.clientX - rect.left;
            this.offsetY = event.clientY - rect.top;
        }
    }

    onMouseMove(event) {
        if (this.draggedNode) {
            const rect = this.svg.getBoundingClientRect();
            this.draggedNode.x = event.clientX - rect.left - this.offsetX;
            this.draggedNode.y = event.clientY - rect.top - this.offsetY;
            this.nodeElements[this.draggedNode.id].setAttribute("transform", `translate(${this.draggedNode.x}, ${this.draggedNode.y})`);
            this.updateConnections();
        }
    }

    onMouseUp() {
        this.draggedNode = null;
    }

    execute() {
        return this.workflow.execute();
    }

    saveToJSON() {
        return JSON.stringify(this.workflow.toJSON());
    }

    loadFromJSON(json, nodeOperations) {
        this.workflow = Workflow.fromJSON(JSON.parse(json), nodeOperations);
        this.redraw();
    }

    saveToLocalStorage(key) {
        localStorage.setItem(key, this.saveToJSON());
    }

    loadFromLocalStorage(key, nodeOperations) {
        const json = localStorage.getItem(key);
        if (json) {
            this.loadFromJSON(json, nodeOperations);
        }
    }

    redraw() {
        this.svg.innerHTML = '';
        this.nodeElements = {};
        this.connectionElements = [];
        this.workflow.nodeList.forEach(node => this.drawNode(node));
        this.workflow.nodeList.forEach(node => {
            Object.entries(node.outputConnections).forEach(([outputIndex, connections]) => {
                connections.forEach(conn => {
                    this.drawConnection(node.id, parseInt(outputIndex), conn.node.id, conn.input);
                });
            });
        });
    }
}

// Usage example
const nodeOperations = {
    "Add": (inputs) => ({ sum: inputs.a + inputs.b }),
    "Multiply": (inputs) => ({ product: inputs.x * inputs.y }),
    "Output": (inputs) => console.log("Result:", inputs.result)
};

const visualizer = new WorkflowVisualizer("workflow-container");

const addNode = new WorkflowNode(0, "Add", [
    { name: "a", type: "number" },
    { name: "b", type: "number" }
], [
    { name: "sum", type: "number" }
], nodeOperations["Add"], 50, 50);

const multiplyNode = new WorkflowNode(1, "Multiply", [
    { name: "x", type: "number" },
    { name: "y", type: "number" }
], [
    { name: "product", type: "number" }
], nodeOperations["Multiply"], 250, 50);

const outputNode = new WorkflowNode(2, "Output", [
    { name: "result", type: "number" }
], [], nodeOperations["Output"], 450, 50);

visualizer.addNode(addNode);
visualizer.addNode(multiplyNode);
visualizer.addNode(outputNode);

visualizer.connectNodes(0, 0, 1, 0);
visualizer.connectNodes(1, 0, 2, 0);

// Add save and load buttons
const saveButton = document.createElement("button");
saveButton.textContent = "Save";
saveButton.onclick = () => {
    const json = visualizer.saveToJSON();
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "workflow.json";
    a.click();
    URL.revokeObjectURL(url);
};
document.body.appendChild(saveButton);

const loadButton = document.createElement("button");
loadButton.textContent = "Load";
loadButton.onclick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json";
    input.onchange = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
            visualizer.loadFromJSON(e.target.result, nodeOperations);
        };
        reader.readAsText(file);
    };
    input.click();
};
document.body.appendChild(loadButton);

// Add save and load to/from localStorage buttons
const saveLocalButton = document.createElement("button");
saveLocalButton.textContent = "Save to LocalStorage";
saveLocalButton.onclick = () => visualizer.saveToLocalStorage("workflow");
document.body.appendChild(saveLocalButton);

const loadLocalButton = document.createElement("button");
loadLocalButton.textContent = "Load from LocalStorage";
loadLocalButton.onclick = () => visualizer.loadFromLocalStorage("workflow", nodeOperations);
document.body.appendChild(loadLocalButton);

const executeButton = document.createElement("button");
executeButton.textContent = "Execute";
executeButton.onclick = () => {
    const results = visualizer.execute();
    console.log(results);
};
document.body.appendChild(executeButton);

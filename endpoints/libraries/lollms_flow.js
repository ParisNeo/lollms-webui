// Lollms Flow
// A library for building workflows of execution
// By ParisNeo
class WorkflowNode {
    constructor(id, name, inputs, outputs, operation, options = {}, x = 0, y = 0) {
        this.id = id;
        this.name = name;
        this.inputs = inputs;
        this.outputs = outputs;
        this.operation = operation;
        this.options = options;
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
        return this.operation(inputs, this.options);
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            inputs: this.inputs,
            outputs: this.outputs,
            options: this.options,
            x: this.x,
            y: this.y
        };
    }

    static fromJSON(json, operation) {
        return new WorkflowNode(json.id, json.name, json.inputs, json.outputs, operation, json.options, json.x, json.y);
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

        this.svg.setAttribute('width', '100%');
        this.svg.setAttribute('height', '600px');

        this.tempLine = null;
        this.startSocket = null;

        this.optionsPopup = null;
        this.setupOptionsPopup();


        this.addDefs();
        this.setupEventListeners();
    }

    addDefs() {
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        
        // Node shadow filter
        const filter = document.createElementNS("http://www.w3.org/2000/svg", "filter");
        filter.setAttribute("id", "dropShadow");
        filter.innerHTML = `
            <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
            <feOffset in="blur" dx="2" dy="2" result="offsetBlur"/>
            <feMerge>
                <feMergeNode in="offsetBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        `;
        defs.appendChild(filter);

        this.svg.appendChild(defs);
    }

    setupEventListeners() {
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
        g.classList.add("node");

        const titleHeight = 30;
        const buttonHeight = 25;
        const buttonMargin = 5;
        const nodeWidth = 160;
        const nodeHeight = titleHeight + (Object.keys(node.options).length * (buttonHeight + buttonMargin)) + buttonMargin;

        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("width", nodeWidth);
        rect.setAttribute("height", nodeHeight);
        rect.setAttribute("rx", "5");
        rect.setAttribute("ry", "5");
        rect.setAttribute("fill", node.color || "#f0f0f0");
        rect.setAttribute("stroke", "#333");
        rect.setAttribute("stroke-width", "2");
        g.appendChild(rect);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", nodeWidth / 2);
        text.setAttribute("y", titleHeight / 2 + 5);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-family", "Arial, sans-serif");
        text.setAttribute("font-size", "14");
        text.setAttribute("fill", "#333");
        text.textContent = node.name;
        g.appendChild(text);

        this.drawSockets(g, node.inputs, 'input', nodeHeight);
        this.drawSockets(g, node.outputs, 'output', nodeHeight);
        this.drawOptionButtons(g, node, titleHeight, buttonHeight, buttonMargin, nodeWidth);

        g.addEventListener('mousedown', this.onNodeMouseDown.bind(this));
        this.svg.appendChild(g);
        this.nodeElements[node.id] = g;
    }

    drawOptionButtons(nodeGroup, node, titleHeight, buttonHeight, buttonMargin, nodeWidth) {
        Object.entries(node.options).forEach(([key, option], index) => {
            const button = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            button.setAttribute("x", buttonMargin);
            button.setAttribute("y", titleHeight + index * (buttonHeight + buttonMargin));
            button.setAttribute("width", nodeWidth - 2 * buttonMargin);
            button.setAttribute("height", buttonHeight);
            button.setAttribute("rx", "3");
            button.setAttribute("ry", "3");
            button.setAttribute("fill", "#ddd");
            button.setAttribute("stroke", "#333");
            button.setAttribute("stroke-width", "1");
            button.classList.add("option-button");
    
            const buttonText = document.createElementNS("http://www.w3.org/2000/svg", "text");
            buttonText.setAttribute("x", nodeWidth / 2);
            buttonText.setAttribute("y", titleHeight + index * (buttonHeight + buttonMargin) + buttonHeight / 2 + 5);
            buttonText.setAttribute("text-anchor", "middle");
            buttonText.setAttribute("font-family", "Arial, sans-serif");
            buttonText.setAttribute("font-size", "12");
            buttonText.setAttribute("fill", "#333");
            buttonText.textContent = option.name; // Use the option name (key) instead of index
    
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                this.showOptionsPopup(node, key, option.name);
            });
    
            nodeGroup.appendChild(button);
            nodeGroup.appendChild(buttonText);
        });
    }
    

    drawSockets(nodeGroup, sockets, type, nodeHeight) {
        sockets.forEach((socket, index) => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", type === 'input' ? "0" : "160");
            circle.setAttribute("cy", (index + 1) * (nodeHeight / (sockets.length + 1)));
            circle.setAttribute("r", "6");
            circle.setAttribute("fill", this.getColorForType(socket.type));
            circle.setAttribute("stroke", "#333");
            circle.setAttribute("stroke-width", "2");
            circle.classList.add("socket", `${type}-socket`);
            circle.setAttribute("data-node-id", nodeGroup.getAttribute("data-id"));
            circle.setAttribute("data-socket-index", index);
            circle.setAttribute("data-socket-type", socket.type);
            
            this.addSocketListeners(circle, type);
            nodeGroup.appendChild(circle);
        });
    }

    setupOptionsPopup() {
        this.optionsPopup = document.createElement('div');
        this.optionsPopup.style.position = 'absolute';
        this.optionsPopup.style.zIndex = '1000';
        this.optionsPopup.style.backgroundColor = 'white';
        this.optionsPopup.style.border = '1px solid #333';
        this.optionsPopup.style.borderRadius = '5px';
        this.optionsPopup.style.padding = '10px';
        this.optionsPopup.style.display = 'none';
        this.optionsPopup.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        document.body.appendChild(this.optionsPopup);

        // Close popup when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.optionsPopup.contains(event.target) && !event.target.closest('.option-button')) {
                this.optionsPopup.style.display = 'none';
            }
        });
    }

    showOptionsPopup(node, optionKey, optionName) {
        this.optionsPopup.innerHTML = '';
        
        const title = document.createElement('h3');
        title.textContent = `${node.name}: ${optionName}`;
        title.style.marginTop = '0';
        this.optionsPopup.appendChild(title);

        const option = node.options[optionKey];
        const optionContainer = document.createElement('div');
        optionContainer.style.marginBottom = '10px';

        let input;
        switch (option.type) {
            case 'checkbox':
                input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = option.value;
                break;
            case 'radio':
                option.options.forEach(optionValue => {
                    const radioInput = document.createElement('input');
                    radioInput.type = 'radio';
                    radioInput.name = optionKey;
                    radioInput.value = optionValue;
                    radioInput.checked = option.value === optionValue;
                    const radioLabel = document.createElement('label');
                    radioLabel.textContent = optionValue;
                    optionContainer.appendChild(radioInput);
                    optionContainer.appendChild(radioLabel);
                });
                break;
            case 'select':
                input = document.createElement('select');
                option.options.forEach(optionValue => {
                    const optionElement = document.createElement('option');
                    optionElement.value = optionValue;
                    optionElement.textContent = optionValue;
                    optionElement.selected = option.value === optionValue;
                    input.appendChild(optionElement);
                });
                break;
            case 'file':
                input = document.createElement('input');
                input.type = 'file';
                break;
            case 'textarea':
                input = document.createElement('textarea');
                input.value = option.value;
                input.rows = 3;
                break;
            default:
                input = document.createElement('input');
                input.type = 'text';
                input.value = option.value;
        }

        if (input) {
            input.addEventListener('change', (e) => {
                option.value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
            });
            optionContainer.appendChild(input);
        }

        this.optionsPopup.appendChild(optionContainer);

        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.marginTop = '10px';
        closeButton.addEventListener('click', () => {
            this.optionsPopup.style.display = 'none';
        });
        this.optionsPopup.appendChild(closeButton);

        const rect = this.svg.getBoundingClientRect();
        this.optionsPopup.style.left = (rect.left + node.x + 170) + 'px';
        this.optionsPopup.style.top = (rect.top + node.y) + 'px';
        this.optionsPopup.style.display = 'block';
    }

    calculateNodeHeight(node) {
        const baseHeight = 80;
        const optionsHeight = Object.keys(node.options).length * 30;
        return baseHeight + optionsHeight;
    }

    drawOptions(nodeGroup, options) {
        let yOffset = 50;
        Object.entries(options).forEach(([key, option]) => {
            const foreignObject = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
            foreignObject.setAttribute("x", "10");
            foreignObject.setAttribute("y", yOffset.toString());
            foreignObject.setAttribute("width", "120");
            foreignObject.setAttribute("height", "25");

            const div = document.createElement("div");
            div.style.display = "flex";
            div.style.alignItems = "center";

            const label = document.createElement("label");
            label.textContent = key + ": ";
            label.style.marginRight = "5px";
            div.appendChild(label);

            let input;
            switch (option.type) {
                case 'checkbox':
                    input = document.createElement("input");
                    input.type = "checkbox";
                    input.checked = option.value;
                    break;
                case 'radio':
                    option.options.forEach(optionValue => {
                        const radioInput = document.createElement("input");
                        radioInput.type = "radio";
                        radioInput.name = key;
                        radioInput.value = optionValue;
                        radioInput.checked = option.value === optionValue;
                        div.appendChild(radioInput);
                        const radioLabel = document.createElement("label");
                        radioLabel.textContent = optionValue;
                        div.appendChild(radioLabel);
                    });
                    break;
                case 'select':
                    input = document.createElement("select");
                    option.options.forEach(optionValue => {
                        const optionElement = document.createElement("option");
                        optionElement.value = optionValue;
                        optionElement.textContent = optionValue;
                        optionElement.selected = option.value === optionValue;
                        input.appendChild(optionElement);
                    });
                    break;
                case 'file':
                    input = document.createElement("input");
                    input.type = "file";
                    break;
                case 'textarea':
                    input = document.createElement("textarea");
                    input.value = option.value;
                    input.rows = 3;
                    break;
                default:
                    input = document.createElement("input");
                    input.type = "text";
                    input.value = option.value;
            }

            if (input) {
                input.addEventListener('change', (e) => {
                    option.value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
                });
                div.appendChild(input);
            }

            foreignObject.appendChild(div);
            nodeGroup.appendChild(foreignObject);

            yOffset += 30;
        });
    }

    drawSockets(nodeGroup, sockets, type) {
        sockets.forEach((socket, index) => {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", type === 'input' ? "0" : "140");
            circle.setAttribute("cy", (index + 1) * 20);
            circle.setAttribute("r", "6");
            circle.setAttribute("fill", this.getColorForType(socket.type));
            circle.setAttribute("stroke", "#333");
            circle.setAttribute("stroke-width", "2");
            circle.classList.add("socket", `${type}-socket`);
            circle.setAttribute("data-node-id", nodeGroup.getAttribute("data-id"));
            circle.setAttribute("data-socket-index", index);
            circle.setAttribute("data-socket-type", socket.type);
            
            this.addSocketListeners(circle, type);
            nodeGroup.appendChild(circle);
        });
    }

    drawConnection(sourceId, sourceOutput, targetId, targetInput) {
        const sourceNode = this.workflow.nodes[sourceId];
        const targetNode = this.workflow.nodes[targetId];
        const path = this.createConnectionPath(sourceNode, sourceOutput, targetNode, targetInput);
        this.svg.appendChild(path);
        this.connectionElements.push({ path, sourceId, sourceOutput, targetId, targetInput });
    }

    createConnectionPath(sourceNode, sourceOutput, targetNode, targetInput) {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const d = this.calculatePathD(sourceNode, sourceOutput, targetNode, targetInput);
        path.setAttribute("d", d);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#666");
        path.setAttribute("stroke-width", "2");
        return path;
    }

    calculatePathD(sourceNode, sourceOutput, targetNode, targetInput) {
        const sourcePosX = sourceNode.x + 140;
        const sourcePosY = sourceNode.y + (sourceOutput + 1) * 20;
        const targetPosX = targetNode.x;
        const targetPosY = targetNode.y + (targetInput + 1) * 20;
        const midX = (sourcePosX + targetPosX) / 2;
        return `M ${sourcePosX} ${sourcePosY} C ${midX} ${sourcePosY}, ${midX} ${targetPosY}, ${targetPosX} ${targetPosY}`;
    }

    updateConnections() {
        this.connectionElements.forEach(conn => {
            const sourceNode = this.workflow.nodes[conn.sourceId];
            const targetNode = this.workflow.nodes[conn.targetId];
            const d = this.calculatePathD(sourceNode, conn.sourceOutput, targetNode, conn.targetInput);
            conn.path.setAttribute("d", d);
        });
    }

    getColorForType(type) {
        const colors = {
            number: "#4285F4",
            string: "#34A853",
            boolean: "#EA4335",
            object: "#FBBC05"
        };
        return colors[type] || "#9E9E9E";
    }

    onNodeMouseDown(event) {
        if (event.target.classList.contains('socket')) return;
        const nodeElement = event.currentTarget;
        this.draggedNode = this.workflow.nodes[nodeElement.getAttribute("data-id")];
        const rect = nodeElement.getBoundingClientRect();
        this.offsetX = event.clientX - rect.left;
        this.offsetY = event.clientY - rect.top;
        nodeElement.setAttribute("filter", "url(#dropShadow)");
    }

    onMouseMove(event) {
        if (this.draggedNode) {
            const rect = this.svg.getBoundingClientRect();
            this.draggedNode.x = event.clientX - rect.left - this.offsetX;
            this.draggedNode.y = event.clientY - rect.top - this.offsetY;
            this.nodeElements[this.draggedNode.id].setAttribute("transform", `translate(${this.draggedNode.x}, ${this.draggedNode.y})`);
            this.updateConnections();
        }
        if (this.tempLine) {
            const rect = this.svg.getBoundingClientRect();
            this.updateTempLine(event.clientX - rect.left, event.clientY - rect.top);
        }
    }

    onMouseUp(event) {
        if (this.draggedNode) {
            this.nodeElements[this.draggedNode.id].removeAttribute("filter");
            this.draggedNode = null;
        }
        if (this.tempLine && this.startSocket) {
            const endSocket = event.target.closest('.input-socket');
            if (endSocket && this.canConnect(this.startSocket, endSocket)) {
                const sourceId = this.startSocket.getAttribute('data-node-id');
                const sourceOutput = this.startSocket.getAttribute('data-socket-index');
                const targetId = endSocket.getAttribute('data-node-id');
                const targetInput = endSocket.getAttribute('data-socket-index');
                this.connectNodes(sourceId, parseInt(sourceOutput), targetId, parseInt(targetInput));
            }
            this.svg.removeChild(this.tempLine);
            this.tempLine = null;
            this.startSocket = null;
        }
    }

    addSocketListeners(socket, type) {
        socket.addEventListener('mouseenter', () => socket.setAttribute('r', '8'));
        socket.addEventListener('mouseleave', () => socket.setAttribute('r', '6'));

        if (type === 'output') {
            socket.addEventListener('mousedown', this.onSocketMouseDown.bind(this));
        }
    }

    onSocketMouseDown(event) {
        event.stopPropagation();
        this.startSocket = event.target;
        const rect = this.svg.getBoundingClientRect();
        const startX = parseFloat(this.startSocket.getAttribute('cx')) + this.startSocket.parentElement.transform.baseVal[0].matrix.e;
        const startY = parseFloat(this.startSocket.getAttribute('cy')) + this.startSocket.parentElement.transform.baseVal[0].matrix.f;
        this.tempLine = this.createTempLine(startX, startY, event.clientX - rect.left, event.clientY - rect.top);
        this.svg.appendChild(this.tempLine);
    }

    createTempLine(startX, startY, endX, endY) {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const d = `M ${startX} ${startY} C ${(startX + endX) / 2} ${startY}, ${(startX + endX) / 2} ${endY}, ${endX} ${endY}`;
        path.setAttribute("d", d);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#666");
        path.setAttribute("stroke-width", "2");
        path.setAttribute("stroke-dasharray", "5,5");
        return path;
    }

    updateTempLine(endX, endY) {
        const startX = parseFloat(this.startSocket.getAttribute('cx')) + this.startSocket.parentElement.transform.baseVal[0].matrix.e;
        const startY = parseFloat(this.startSocket.getAttribute('cy')) + this.startSocket.parentElement.transform.baseVal[0].matrix.f;
        const d = `M ${startX} ${startY} C ${(startX + endX) / 2} ${startY}, ${(startX + endX) / 2} ${endY}, ${endX} ${endY}`;
        this.tempLine.setAttribute("d", d);
    }

    canConnect(sourceSocket, targetSocket) {
        return sourceSocket.getAttribute('data-socket-type') === targetSocket.getAttribute('data-socket-type') &&
               sourceSocket.getAttribute('data-node-id') !== targetSocket.getAttribute('data-node-id');
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
        this.addDefs();
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

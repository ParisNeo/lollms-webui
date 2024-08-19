# Lollms Flow

Lollms Flow is a powerful JavaScript library for building and visualizing workflows of execution. It provides an intuitive way to create, connect, and manage nodes in a workflow, as well as visualize and interact with the workflow through a drag-and-drop interface.

## Features

- Create custom workflow nodes with inputs and outputs
- Connect nodes to form complex workflows
- Visualize workflows with an interactive SVG-based interface
- Drag-and-drop functionality for easy node positioning
- Save and load workflows to/from JSON
- Execute workflows and obtain results
- Integration with local storage for persistent workflows
- Customizable node operations

## Installation

### For Lollms Users

If you're using Lollms with the server running, you can include Lollms Flow directly in your HTML:

```html
<script src="/lollms_assets/js/lollms_flow"></script>
```

### For Non-Lollms Users

If you're not using Lollms or need to specify the full server path:

```html
<script src="http://localhost:9600/lollms_assets/js/lollms_flow"></script>
```

Note: Make sure to activate the server of the app in Lollms, or the CORS policy may prevent access.

## Usage

1. Create a container for the workflow in your HTML:

```html
<div id="workflow-container"></div>
```

2. Initialize the WorkflowVisualizer:

```javascript
const visualizer = new WorkflowVisualizer("workflow-container");
```

3. Define node operations:

```javascript
const nodeOperations = {
    "Add": (inputs) => ({ sum: inputs.a + inputs.b }),
    "Multiply": (inputs) => ({ product: inputs.x * inputs.y }),
    "Output": (inputs) => console.log("Result:", inputs.result)
};
```

4. Create and add nodes:

```javascript
const addNode = new WorkflowNode(0, "Add", [
    { name: "a", type: "number" },
    { name: "b", type: "number" }
], [
    { name: "sum", type: "number" }
], nodeOperations["Add"], 50, 50);

visualizer.addNode(addNode);
```

5. Connect nodes:

```javascript
visualizer.connectNodes(0, 0, 1, 0);
```

6. Execute the workflow:

```javascript
const results = visualizer.execute();
console.log(results);
```

## API Reference

### WorkflowNode

Constructor: `WorkflowNode(id, name, inputs, outputs, operation, x = 0, y = 0)`

Methods:
- `connect(outputIndex, targetNode, inputIndex)`
- `execute(inputs)`
- `toJSON()`
- `static fromJSON(json, operation)`

### Workflow

Constructor: `Workflow()`

Methods:
- `addNode(node)`
- `connectNodes(sourceId, sourceOutput, targetId, targetInput)`
- `canConnect(sourceNode, sourceOutput, targetNode, targetInput)`
- `execute()`
- `toJSON()`
- `static fromJSON(json, nodeOperations)`

### WorkflowVisualizer

Constructor: `WorkflowVisualizer(containerId)`

Methods:
- `addNode(node)`
- `connectNodes(sourceId, sourceOutput, targetId, targetInput)`
- `execute()`
- `saveToJSON()`
- `loadFromJSON(json, nodeOperations)`
- `saveToLocalStorage(key)`
- `loadFromLocalStorage(key, nodeOperations)`
- `redraw()`

## Example

```javascript
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

const results = visualizer.execute();
console.log(results);
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

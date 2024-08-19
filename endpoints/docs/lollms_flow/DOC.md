# LollmsFlow Documentation

LollmsFlow is a JavaScript library for creating and visualizing workflows. It allows you to build, connect, and execute nodes in a workflow, as well as visualize the workflow in an interactive SVG-based interface.

## Key Components

1. **WorkflowNode**: Represents a single node in the workflow.
2. **Workflow**: Manages the entire workflow, including nodes and their connections.
3. **WorkflowVisualizer**: Handles the visual representation and interaction of the workflow.

## Supported Data Types

LollmsFlow supports the following data types for node inputs and outputs:

1. **number**: Represents numeric values (integers or floating-point numbers).
2. **string**: Represents text data.
3. **boolean**: Represents true/false values.
4. **object**: Represents complex data structures or custom objects.

Each data type is associated with a specific color in the workflow visualization:

- number: blue
- string: green
- boolean: red
- object: purple

Any other type not explicitly defined will be represented with a gray color.

## Basic Usage
### 0. Import the LollmsFlow Library

First, include the LollmsFlow library in your HTML file:

```html
<script src="/lollms_assets/js/lollms_flow"></script>
```


### 1. Create a Workflow Visualizer

```javascript
const visualizer = new WorkflowVisualizer("workflow-container");
```

### 2. Define Node Operations

```javascript
const nodeOperations = {
    "Add": (inputs) => ({ sum: inputs.a + inputs.b }),
    "Multiply": (inputs) => ({ product: inputs.x * inputs.y }),
    "Output": (inputs) => console.log("Result:", inputs.result)
};
```

### 3. Create and Add Nodes

```javascript
const addNode = new WorkflowNode(0, "Add", 
    [{ name: "a", type: "number" }, { name: "b", type: "number" }],
    [{ name: "sum", type: "number" }],
    nodeOperations["Add"], 50, 50
);
visualizer.addNode(addNode);
```

### 4. Connect Nodes

```javascript
visualizer.connectNodes(sourceId, sourceOutput, targetId, targetInput);
```

### 5. Execute the Workflow

```javascript
const results = visualizer.execute();
```

## Advanced Features

- **Save/Load Workflow**: Use `saveToJSON()` and `loadFromJSON()` methods.
- **Local Storage**: Save/load workflows using `saveToLocalStorage()` and `loadFromLocalStorage()`.
- **Drag and Drop**: Nodes can be moved around in the visualizer.

## Key Methods for AI Usage

1. `addNode(node)`: Add a new node to the workflow.
2. `connectNodes(sourceId, sourceOutput, targetId, targetInput)`: Connect two nodes.
3. `execute()`: Run the workflow and get results.
4. `saveToJSON()`: Convert the workflow to a JSON string.
5. `loadFromJSON(json, nodeOperations)`: Load a workflow from a JSON string.

## Tips for AI Implementation

1. Define a set of node types and their operations, using the supported data types.
2. Create nodes dynamically based on user input or predefined templates.
3. Use the visualization features to display the workflow to users, leveraging the color-coding for different data types.
4. Implement save/load functionality to persist workflows.
5. Utilize the execution feature to process data through the workflow.
6. When creating custom nodes, ensure that the input and output types match one of the supported data types for proper visualization and connection validation.

This library provides a flexible framework for creating visual, interactive workflows in web applications. It can be particularly useful for data processing, algorithm visualization, or any application requiring a flow-based interface. The support for various data types allows for diverse and complex workflows to be created and managed effectively.
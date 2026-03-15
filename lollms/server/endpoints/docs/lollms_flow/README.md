Certainly! I'll provide a comprehensive documentation for the Lollms Flow library. This library seems to be a powerful tool for building and visualizing workflows with nodes and connections. Here's the full documentation:

# Lollms Flow Library Documentation

## Overview

Lollms Flow is a JavaScript library for building, visualizing, and executing workflows. It provides a set of classes and methods to create nodes, connect them, and visualize the resulting workflow in an SVG-based interface.

## Classes

### 1. WorkflowNode

Represents a single node in the workflow.

#### Constructor

```javascript
new WorkflowNode(id, name, inputs, outputs, operation, options = {}, x = 0, y = 0)
```

- `id`: Unique identifier for the node
- `name`: Display name of the node
- `inputs`: Array of input sockets
- `outputs`: Array of output sockets
- `operation`: Function to execute when the node is processed
- `options`: Object containing node-specific options
- `x`, `y`: Initial position of the node in the visualization

#### Methods

- `connect(outputIndex, targetNode, inputIndex)`: Connect this node's output to another node's input
- `execute(inputs)`: Execute the node's operation
- `toJSON()`: Convert the node to a JSON representation
- `static fromJSON(json, operation)`: Create a node from a JSON representation

### 2. Workflow

Manages the entire workflow, including nodes and their connections.

#### Constructor

```javascript
new Workflow()
```

#### Methods

- `addNode(node)`: Add a node to the workflow
- `connectNodes(sourceId, sourceOutput, targetId, targetInput)`: Connect two nodes
- `canConnect(sourceNode, sourceOutput, targetNode, targetInput)`: Check if two nodes can be connected
- `execute()`: Execute the entire workflow
- `toJSON()`: Convert the workflow to a JSON representation
- `static fromJSON(json, nodeOperations)`: Create a workflow from a JSON representation

### 3. WorkflowVisualizer

Handles the visualization of the workflow using SVG.

#### Constructor

```javascript
new WorkflowVisualizer(containerId)
```

- `containerId`: ID of the HTML element to contain the SVG visualization

#### Methods

- `addNode(node)`: Add a node to the workflow and visualize it
- `connectNodes(sourceId, sourceOutput, targetId, targetInput)`: Connect two nodes and visualize the connection
- `execute()`: Execute the workflow
- `saveToJSON()`: Save the workflow to a JSON string
- `loadFromJSON(json, nodeOperations)`: Load a workflow from a JSON string
- `saveToLocalStorage(key)`: Save the workflow to local storage
- `loadFromLocalStorage(key, nodeOperations)`: Load a workflow from local storage
- `redraw()`: Redraw the entire workflow visualization

## Usage

1. Create a WorkflowVisualizer instance:

```javascript
const visualizer = new WorkflowVisualizer('workflow-container');
```

2. Define node operations:

```javascript
const nodeOperations = {
    'Add': (inputs) => ({ result: inputs.a + inputs.b }),
    'Multiply': (inputs) => ({ result: inputs.a * inputs.b })
};
```

3. Create and add nodes:

```javascript
const addNode = new WorkflowNode('1', 'Add', 
    [{ name: 'a', type: 'number' }, { name: 'b', type: 'number' }],
    [{ name: 'result', type: 'number' }],
    nodeOperations['Add']
);
visualizer.addNode(addNode);
```

4. Connect nodes:

```javascript
visualizer.connectNodes('1', 0, '2', 0);
```

5. Execute the workflow:

```javascript
const results = visualizer.execute();
```

6. Save and load workflows:

```javascript
const json = visualizer.saveToJSON();
visualizer.loadFromJSON(json, nodeOperations);
```
## Advanced version with options

1. First, let's define the node operation:

```javascript
const nodeOperations = {
    'TextInput': (inputs, options) => ({ text: options.inputText })
};
```

2. Now, let's create the node with the textarea option:

```javascript
const textInputNode = new WorkflowNode(
    '1',                           // id
    'Text Input',                  // name
    [],                            // inputs (empty array as we don't need input sockets)
    [{ name: 'text', type: 'string' }], // outputs
    nodeOperations['TextInput'],   // operation
    {                              // options
        inputText: {
            type: 'textarea',
            value: ''              // initial value
        }
    }
);
```

3. Add the node to the visualizer:

```javascript
visualizer.addNode(textInputNode);
```

4. The WorkflowVisualizer class already handles the creation of the textarea in the `drawOptions` method. When the user types in the textarea, it will automatically update the `options.inputText.value`.

5. To execute the node and get the output:

```javascript
const results = visualizer.execute();
console.log(results['1'].text);  // This will log the text entered in the textarea
```

Here's a complete example of how to set this up:

```javascript
// Assume we have already created the WorkflowVisualizer
const visualizer = new WorkflowVisualizer('workflow-container');

// Define the node operation
const nodeOperations = {
    'TextInput': (inputs, options) => ({ text: options.inputText.value })
};

// Create the node
const textInputNode = new WorkflowNode(
    '1',
    'Text Input',
    [],
    [{ name: 'text', type: 'string' }],
    nodeOperations['TextInput'],
    {
        inputText: {
            type: 'textarea',
            value: 'Enter your text here'
        }
    },
    50,  // x position
    50   // y position
);

// Add the node to the visualizer
visualizer.addNode(textInputNode);

// To execute and get the result:
document.getElementById('executeButton').addEventListener('click', () => {
    const results = visualizer.execute();
    console.log('Output text:', results['1'].text);
});
```

In this setup:

1. We define a 'TextInput' node operation that simply returns the text from the options.
2. We create a WorkflowNode with no inputs, one 'text' output, and an 'inputText' option of type 'textarea'.
3. We add the node to the visualizer, which will create the visual representation including the textarea.
4. When executed, the node will output whatever text is currently in the textarea.

The user can interact with the node in the visualization, typing text into the textarea. When the workflow is executed, it will output the current content of the textarea.

This approach allows for dynamic, user-input text to be part of your workflow, which can then be processed by other nodes or used as the final output of the workflow.

## Features

- Dynamic node creation and connection
- SVG-based visualization
- Drag-and-drop node positioning
- Interactive socket connections
- Node options with various input types (checkbox, radio, select, file, textarea)
- Workflow execution
- JSON serialization and deserialization
- Local storage integration

## Customization

The library allows for extensive customization:

- Node colors can be set individually
- Socket colors are determined by data type
- Node shadows and hover effects are included
- Connection paths are drawn as curved lines

## Event Handling

The library handles various mouse events for interactivity:

- Node dragging
- Socket connection creation
- Socket highlighting on hover

## Best Practices

1. Ensure unique IDs for each node
2. Define clear input and output types for proper connections
3. Implement error handling in node operations
4. Use meaningful names for nodes and sockets
5. Regularly save workflows to prevent data loss

## Limitations

- The library currently does not support undo/redo operations
- Circular dependencies in the workflow are not handled automatically

## Future Enhancements

Potential areas for improvement include:

- Implementing undo/redo functionality
- Adding support for subflows or grouped nodes
- Enhancing the UI with zoom and pan capabilities
- Implementing a node search or categorization system

This documentation provides a comprehensive overview of the Lollms Flow library, its classes, methods, and usage. It should help users understand and effectively utilize the library for building and visualizing workflows.


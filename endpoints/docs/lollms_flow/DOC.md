
# Lollms Flow Library - Quick Reference

## Core Classes

1. `WorkflowNode`: Represents a single node in the workflow.
   - Constructor: `new WorkflowNode(id, name, inputs, outputs, operation, options, x, y)`
   - Key methods: `connect()`, `execute()`, `toJSON()`, `fromJSON()`

2. `Workflow`: Manages the entire workflow.
   - Key methods: `addNode()`, `connectNodes()`, `execute()`, `toJSON()`, `fromJSON()`

3. `WorkflowVisualizer`: Handles visualization using SVG.
   - Constructor: `new WorkflowVisualizer(containerId)`
   - Key methods: `addNode()`, `connectNodes()`, `execute()`, `saveToJSON()`, `loadFromJSON()`

## Basic Usage

1. Create a visualizer:
   ```javascript
   const visualizer = new WorkflowVisualizer('container-id');
   ```

2. Define node operations:
   ```javascript
   const nodeOperations = {
     'OperationName': (inputs, options) => ({ output: result })
   };
   ```

3. Create and add nodes:
   ```javascript
   const node = new WorkflowNode(id, name, inputs, outputs, operation, options);
   visualizer.addNode(node);
   ```

4. Connect nodes:
   ```javascript
   visualizer.connectNodes(sourceId, sourceOutput, targetId, targetInput);
   ```

5. Execute workflow:
   ```javascript
   const results = visualizer.execute();
   ```

6. Save/Load workflow:
   ```javascript
   const json = visualizer.saveToJSON();
   visualizer.loadFromJSON(json, nodeOperations);
   ```

## Key Features

- SVG-based visualization with drag-and-drop
- Interactive socket connections
- Node options (checkbox, radio, select, file, textarea)
- JSON serialization and local storage integration
- Custom node and socket colors
- Event handling for interactivity

## Best Practices

- Use unique node IDs
- Define clear input/output types
- Implement error handling in operations
- Use descriptive names for nodes and sockets

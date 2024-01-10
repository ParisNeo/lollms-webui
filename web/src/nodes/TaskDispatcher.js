import {
    defineNode,
    TextInputInterface,
    NodeInterface
  } from "baklavajs";
  
  export const TaskDispatcherNode = defineNode({
    type: "Task",
    title: "Task",
    description: {

    },
    inputs: {
      description: () => new TextInputInterface("Description", ""),
    },
    outputs: {
      result: () => new NodeInterface("Result")
    },
    calculate({ description }) {
      return { result: description };
    }
  });
  
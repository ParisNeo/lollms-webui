import {
    defineNode,
    TextInputInterface,
    NodeInterface
  } from "baklavajs";
  
  export const TaskNode = defineNode({
    type: "Task",
    title: "Task",
    inputs: {
      description: () => new TextInputInterface("Task description", "").setPort(
        false
      ),
    },
    outputs: {
      prompt: () => new NodeInterface("Prompt")
    },
    calculate({ description }) {
      return { prompt: description };
    }
  });
  
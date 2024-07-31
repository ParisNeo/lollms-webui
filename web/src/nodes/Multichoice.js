import { defineNode, NodeInterface, TextInputInterface } from "baklavajs";


export const MultichoiceNode = defineNode({
    type: "MultichoiceNode",
    title: "Multichoice",
    inputs: {
      question: () => new NodeInterface("Question", ""),
      outputs: () =>
      new TextInputInterface("choices, one per line", "", "").setPort(
        false
      ),
    },
    outputs: {
      response: () => new NodeInterface("Response", "")
    },

});
  

import { defineNode, NodeInterface, TextInterface, SelectInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const LLMNode = defineNode({
  type: "LLMNode",
  title: "LLM",
  inputs: {
    input: () => new NodeInterface("Input", ""),
    question: () => new NodeInterface("Question", "").setPort(
      false
    ),
  },
  outputs: {
    yes: () => new NodeInterface("Yes", ""),
    no: () => new NodeInterface("No", "")
  },
  async calculate({ request }) {
    console.log(store.state.config.personalities)
    let response = '';
    try {
      const result = await axios.get('/yes_no', { params: { text: request } });
      response = result.data;
    } catch (error) {
      console.error(error);
    }
    return {
      display: response,
      response: response
    };
  }
});

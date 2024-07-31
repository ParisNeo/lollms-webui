import { defineNode, NodeInterface, TextInterface, SelectInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const LLMNode = defineNode({
  type: "LLMNode",
  title: "LLM",
  inputs: {
    request: () => new NodeInterface("Request", ""),
  },
  outputs: {
    response: () => new NodeInterface("Response", "")
  },
  async calculate({ request }) {
    console.log(store.state.config.personalities)
    let response = '';
    try {
      const result = await axios.post('/generate', { params: { text: request } });
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

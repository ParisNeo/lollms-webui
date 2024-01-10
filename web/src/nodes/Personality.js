import { defineNode, NodeInterface, TextInterface, SelectInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const AgentNode = defineNode({
  type: "PersonalityNode",
  title: "Personality",
  inputs: {
    request: () => new NodeInterface("Request", ""),
    agent_name: () =>
    new SelectInterface("Personality", "", store.state.config.personalities).setPort(
      false
    ),
  },
  outputs: {
    display: () => new TextInterface("Output", ""),
    response: () => new NodeInterface("Response", "")
  },
  async calculate({ request }) {
    console.log(store.state.config.personalities)
    let response = '';
    try {
      const result = await axios.get('/generate', { params: { text: request } });
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

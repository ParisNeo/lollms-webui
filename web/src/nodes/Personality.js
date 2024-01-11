import { defineNode, NodeInterface, TextInterface, SelectInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const PersonalityNode = defineNode({
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

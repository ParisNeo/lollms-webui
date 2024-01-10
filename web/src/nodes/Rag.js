import { defineNode, NodeInterface, TextInputInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const RAGNode = defineNode({
  type: "RAGNode",
  title: "RAG",
  inputs: {
    request: () => new NodeInterface("Prompt", ""),
    document_path: () => new TextInputInterface("Document path", "").setPort(
      false
    ),
  },
  outputs: {
    prompt: () => new NodeInterface("Prompt with Data", "")
  },
  async calculate({ request, document_path }) {
    let response = '';
    try {
      const result = await axios.get('/rag', { params: { text: request, doc_path:document_path } });
      response = result.data;
    } catch (error) {
      console.error(error);
    }
    return {
      response: response
    };
  }
});

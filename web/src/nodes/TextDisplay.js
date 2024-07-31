import { defineNode, NodeInterface, TextInterface, SelectInterface } from "baklavajs";
import axios from 'axios';
import { store } from '../main'

export const TextDisplayNode = defineNode({
  type: "TextDisplayNode",
  title: "TextDisplay",
  inputs: {
    text2display: () => new NodeInterface("Input", ""),
  },
  outputs: {
    response: () => new TextInterface("Text", "")
  },
  async calculate({ request }) {
  }
});

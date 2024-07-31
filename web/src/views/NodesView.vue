<template>
    <div style="width: 100vw; height: 100vh">
      <baklava-editor :view-model="baklava" />
      <button @click="saveGraph">Save Graph</button>
      <button @click="loadGraph">Load Graph</button>
    </div>
  </template>
  
  <script>
  import { defineComponent } from "vue";
  import {
    EditorComponent,
    useBaklava,
    DependencyEngine,
    applyResult
  } from "baklavajs";
  //import "../css/classic.css";
  import "@baklavajs/themes/dist/syrup-dark.css";
  
  import { PersonalityNode } from "../nodes/Personality";
  import { RAGNode } from "../nodes/Rag";
  import { TaskNode } from "../nodes/Task";
  import { TextDisplayNode } from "../nodes/TextDisplay";
  import { LLMNode } from "../nodes/LLM";
  import { MultichoiceNode } from "../nodes/Multichoice"
  
  export default defineComponent({
    components: {
      "baklava-editor": EditorComponent
    },
    setup() {
      const baklava = useBaklava();
      const engine = new DependencyEngine(baklava.editor);
  

      baklava.editor.registerNodeType(PersonalityNode);
      baklava.editor.registerNodeType(TaskNode);
      baklava.editor.registerNodeType(RAGNode);
      baklava.editor.registerNodeType(TextDisplayNode);
      baklava.editor.registerNodeType(LLMNode);
      baklava.editor.registerNodeType(MultichoiceNode);
      
      
      
  
      const token = Symbol();
      engine.events.afterRun.subscribe(token, (result) => {
        engine.pause();
        applyResult(result, baklava.editor);
        engine.resume();
      });
  
      engine.start();
  
      function addNodeWithCoordinates(nodeType, x, y) {
        const n = new nodeType();
        baklava.displayedGraph.addNode(n);
        n.position.x = x;
        n.position.y = y;
        return n;
      }
      const node1 = addNodeWithCoordinates(TaskNode, 300, 140);
      const node2 = addNodeWithCoordinates(LLMNode, 550, 140);
      const node3 = addNodeWithCoordinates(TextDisplayNode, 850, 140);
      baklava.displayedGraph.addConnection(
        node1.outputs.prompt,
        node2.inputs.request
      );
      baklava.displayedGraph.addConnection(
        node2.outputs.response,
        node3.inputs.text2display
      );
      return { 
        baklava,
        saveGraph: () => {
          const exportedGraph = engine.export();
          localStorage.setItem('myGraph', JSON.stringify(exportedGraph));
        },
        loadGraph: () => {
          const savedGraph = JSON.parse(localStorage.getItem('myGraph'));
          engine.import(savedGraph);
        }
      };
    }
  });
  </script>
  
  
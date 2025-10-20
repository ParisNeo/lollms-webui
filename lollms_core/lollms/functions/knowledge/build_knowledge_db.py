from pathlib import Path
from lollms.personality import APScript
from safe_store import SafeStore
import json
import re
def remove_indexing_from_markdown(markdown_text):
    # Define a regular expression pattern to match numbered and hyphenated lists at the beginning of the line
    pattern = r'^(?:\d+\.\s+|\d+-\s+)'
    
    # Use the sub() method to replace the matched pattern with an empty string
    clean_text = re.sub(pattern, '', markdown_text.strip())
    
    return clean_text


def find_last_file(folder_path):
    i = 0
    while True:
        file_name = f"database_{i}.json"
        file_path = Path(folder_path) / file_name
        if not file_path.exists():
            return str(f"database_{i-1}.json")
        i += 1


def find_available_file(folder_path):
    i = 0
    while True:
        file_name = f"database_{i}.json"
        file_path = Path(folder_path) / file_name
        if not file_path.exists():
            return str(file_path)
        i += 1


def buildKnowledgeDB(llm:APScript, data_store:SafeStore, data_folder_path:str, output_folder:str, questions_gen_size:int, answer_gen_size:int):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    # Verify if the data_folder_path exists
    data_folder_path=Path(data_folder_path)
    if not Path(data_folder_path).exists():
        llm.warning("The specified data_folder_path does not exist.")
    document_files = [v for v in data_folder_path.iterdir()]
    llm.step_start(f"Loading files")
    for file_path in document_files:
        if file_path.suffix in ['.pdf',".txt",".c",".cpp",".h",".py",".msg",".docx",".pptx",".md"]:
            print(file_path)
            data_store.add_document(file_path)
    llm.step_end(f"Loading files")
    # Index the vector store
    llm.step_start(f"Indexing files")
    data_store.build_index()
    llm.step_end(f"Indexing files")
    
    db_name = find_available_file(output_folder)
    output = "### Building questions:\n"
    llm.set_message_content(output)
    # Iterate over all documents in data_folder_path
    processed_chunks = 0
    # Iterate over all chunks and extract text
    questions_vector = []
    chunks = data_store.get_all_chunks()
    total_chunks = len(chunks)
    for chunk in chunks:
        chunk_text = chunk.text
        processed_chunks += 1
        llm.step_start(f"Processing chunk {chunk.chunk_id}: {processed_chunks}/{total_chunks}")
        # Build the prompt text with placeholders
        prompt_text = f"{llm.config.start_header_id_template}instruction: Generate questions or tasks that delve into the specific details and information presented in the text chunks. Please do not ask questions about the form of the text, and do not mention the text itllm in your questions. Make sure you format the output using Markdown with each question or task placed in a separate paragraph starting with __P__.\n{llm.config.separator_template}{llm.config.start_header_id_template}chunk {{chunk_name}}: {{chunk}}{llm.config.separator_template}{llm.config.start_header_id_template}Here are some questions and tasks to further explore the contents of the given text chunks:\n__P__"
        # Ask AI to generate questions
        generated_text = "__P__"+llm.fast_gen(prompt_text, max_generation_size=questions_gen_size, placeholders={"chunk": chunk_text, "chunk_name":chunk_name}, debug=True)
        # Split the generated text into lines and accumulate into questions_vector
        generated_lines = generated_text.strip().split("__P__")
        generated_lines = [q.replace("__P__","") for q in generated_lines]
        generated_lines = [remove_indexing_from_markdown(q) for q in generated_lines]
        questions_vector.extend(generated_lines)
        llm.step_end(f"Processing chunk {chunk.chunk_id}: {processed_chunks}/{total_chunks}")
        output += "\n".join(generated_lines) + "\n"
        llm.set_message_content(output)
    
    llm.step_start(f"Saving questions for future use")
    with open(output_folder/f"{db_name.split('.')[0]}_q.json", 'w') as file:
        json.dump(questions_vector, file)
    llm.step_end(f"Saving questions for future use")
    
    output += "### Building answers:\n"
    llm.set_message_content(output)
    qna_list=[]
    # Perform further processing with questions_vector
    for index, question in enumerate(questions_vector):
        docs, sorted_similarities, document_ids = data_store.search(question, n_results=int(llm.personality_config.rag_n_chunks)) 
        if llm.personality_config.use_enhanced_mode:
            llm.step_start(f"Verifying RAG data_{index}")
            prompt_text = """{llm.config.start_header_id_template}chunk: {{chunk}}
{llm.config.start_header_id_template}instruction: Is the information provided in the above chunk sufficient to answer the following question?
Valid answers:
- Yes
- No
{llm.config.start_header_id_template}question: {{question}}
{llm.config.start_header_id_template}answer: """
            if "yes" not in prompt_text.lower():
                llm.step_end(f"Verifying RAG data_{index}", False)
                continue
            llm.step_end(f"Verifying RAG data_{index}")

        llm.step_start(f"Asking question {index}/{len(questions_vector)}")
        prompt_text = """{llm.config.start_header_id_template}chunk: {{chunk}}
{llm.config.start_header_id_template}instructions{llm.config.end_header_id_template}
Interpret the textual data contained within the chunk thoroughly to answer the corresponding instruction/task presented alongside it.
If the information stored in this chunk does not suffice to provide categorically accurate answers, please answer exactly __UNSUFFICIENT_INFORMATION__.
All statements must be generated solely based on the available input data, discarding any assumptions beyond what has been explicitly stated.
Do not mention the chunks, assume you are generating training data for an AI to learn from without data.
It is crucial to maintain strict adherence to the content delineated in each instance of interaction.
Be precise and helpful.
{llm.config.start_header_id_template}question: {{question}}
{llm.config.start_header_id_template}answer: """
        # {llm.config.start_header_id_template}chunk: {{chunk}}{llm.config.separator_template}{llm.config.start_header_id_template}instruction: Please use the text chunks to answer the following question:\n{llm.config.separator_template}{llm.config.start_header_id_template}question: {{question}}\n{llm.config.separator_template}{llm.config.start_header_id_template}answer: "
        # Ask AI to generate an answer
        answer = llm.fast_gen(prompt_text, max_generation_size=answer_gen_size, placeholders={"chunk": "\nchunk: ".join(docs), "question": question})
        if "UNSUFFICIENT_INFORMATION" in answer:
            continue
        qna_list.append({
            "conditionning":"Act as LoLLMs expert and answer the following questions.",
            "question":question,
            "answer":answer,
            "id":0
        })
        output += f"q:{question}\na:{answer}\n"
        llm.set_message_content(output)
        llm.step_end(f"Asking question {index}/{len(questions_vector)}")
        with open(output_folder/db_name, 'w') as file:
            json.dump(qna_list, file)
    print("Dictionary saved as JSON successfully!")
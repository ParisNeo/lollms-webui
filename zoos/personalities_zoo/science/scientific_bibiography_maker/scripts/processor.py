import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.functions.bibliography import arxiv_pdf_search
from lollms.prompting import LollmsContextDetails

from lollmsvectordb import TextDocumentsLoader
import requests
import json
from lollmsvectordb import VectorDatabase
import requests 
from typing import Callable, Any
if not PackageManager.check_package_installed("arxiv"):
    PackageManager.install_package("arxiv")

def query_server(base_url, query_params):
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])
    response = requests.get(url)
    json_data = response.json()
    return json_data

def classify_reports(reports):
    sorted_reports = sorted(reports, key=lambda x: x['relevance_score'], reverse=True)
    return sorted_reports

class Processor(APScript):
    """
    A class that processes model inputs and outputs.

    Inherits from APScript.
    """


    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback = None,
                ) -> None:
        self.word_callback = None
        self.arxiv = None
        self.ieeexplore = None
        # C:\Program Files\MiKTeX\miktex\bin\x64
        # https://developer.ieee.org/Python3_Software_Development_Kit#fullTextExample
        personality_config_template = ConfigTemplate(
            [
                {"name":"research_subject","type":"str","value":"", "min":1, "help":"The subject of your research. This is useful to help the AI identify the relevance of the documents for your research subject"},
                {"name":"pdf_latex_path","type":"str","value":"", "min":1, "help":"path to the pdflatex file pdf compiler used to compile pdf files"},
                {"name":"ieee_explore_key","type":"str","value":"", "min":1, "help":"The key to use for accessing ieeexplore api"},                
                {"name":"nb_arxiv_results","type":"int","value":10, "min":1, "help":"number of results to recover for ARXIV"},                
                {"name":"sort_by","type":"str","value":"relevance", "options":["relevance"], "help":"Sorting parameter"},                
                {"name":"start_date","type":"str","value":"", "help":"Start date"},                
                {"name":"end_date","type":"str","value":"","help":"End date"},                
                {"name":"author","type":"str","value":"","help":"Search for a specific author"},                
                
                {"name":"nb_ieee_explore_results","type":"int","value":0, "min":1, "help":"number of results to recover for IEEE explore"},                
                {"name":"nb_hal_results","type":"int","value":0, "min":1, "help":"number of results to recover for HAL (French portal)"},                
                {"name":"output_file_name","type":"str","value":"summary_latex", "min":1, "help":"Name of the pdf file to generate"},
                {"name":"Formulate_search_query","type":"bool","value":True, "help":"Before doing the search the AI creates a keywords list that gets sent to the arxiv search engine."},
                {"name":"make_survey","type":"bool","value":True, "min":1, "help":"build a survey report"},
                {"name":"read_the_whole_article","type":"bool","value":False, "help":"With this, the AI readsthe whole article, summarizes it before doing the classification. This is resource intensive as it requires the AI to dive deep into the article and if you have multiple articles with multiple pages, this may slow down the generation."},
                {"name":"read_content","type":"bool","value":True, "help":"With this, the AI reads the whole document and judges if it is related to the work or not and filter out unrelated papers"},
                {"name":"read_only_first_chunk","type":"bool","value":True, "help":"To reduce processing time, you can just read the first chunks which in general contains the title, the authors and the abstracts"},
                {"name":"max_generation_prompt_size","type":"int","value":2048, "min":10, "max":personality.config["ctx_size"], "help":"Crop the maximum generation prompt size"},
                {"name":"relevance_check_severity","type":"int","value":4, "min":0, "max":10, "help":"The severity of the selection is the threshold under which the AI considers the article as irrelevant"},
                {"name":"chunk_size","type":"int","value":512, "help":"The size of chunks when using document summary"},
            ]
            )
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )
        super().__init__(
                            personality,
                            personality_config,
                            [
                                {
                                    "name": "idle",
                                    "commands": { # list of commands
                                        "help":self.help,
                                        "analyze_articles":self.analyze_articles,
                                        "search_analyze_organize_summarize":self.search_analyze_organize_summarize
                                    },
                                    "default": None
                                },                           
                            ],
                            callback=callback
                        )
        self.previous_versions = []
        self.code=[]
        
        from lollmsvectordb.lollms_tokenizers.tiktoken_tokenizer import TikTokenTokenizer

        if self.config.rag_vectorizer == "semantic":
            from lollmsvectordb.lollms_vectorizers.semantic_vectorizer import SemanticVectorizer
            v = SemanticVectorizer(self.config.rag_vectorizer_model, self.config.rag_vectorizer_execute_remote_code)
        elif self.config.rag_vectorizer == "tfidf":
            from lollmsvectordb.lollms_vectorizers.tfidf_vectorizer import TFIDFVectorizer
            v = TFIDFVectorizer()
        elif self.config.rag_vectorizer == "openai":
            from lollmsvectordb.lollms_vectorizers.openai_vectorizer import OpenAIVectorizer
            v = OpenAIVectorizer(self.config.rag_vectorizer_openai_key)        
        elif self.personality.config.rag_vectorizer == "ollama":
            from lollmsvectordb.lollms_vectorizers.ollama_vectorizer import OllamaVectorizer
            v = OllamaVectorizer(self.personality.config.rag_vectorizer_model, self.personality.config.rag_service_url)
            
        self.persona_data_vectorizer = VectorDatabase("", v, TikTokenTokenizer(), self.config.rag_chunk_size, self.config.rag_overlap)
        self.set_message_content_documents_vectorizer = VectorDatabase("", v, TikTokenTokenizer(), self.config.rag_chunk_size, self.config.rag_overlap)
        self.abstract_vectorizer = VectorDatabase("", v, TikTokenTokenizer(), self.config.rag_chunk_size, self.config.rag_overlap)

    def settings_updated(self):
        """
        Updated
        """
        if self.personality_config.ieee_explore_key!="" and self.personality_config.nb_ieee_explore_results>0:
            if not PackageManager.check_package_installed("xploreapi"):
                PackageManager.install_package("xploreapi")

            from xploreapi import XPLORE

        
    def install(self):
        super().install()
        # Get the current directory
        root_dir = self.personality.lollms_paths.personal_path
        # We put this in the shared folder in order as this can be used by other personalities.
        shared_folder = root_dir/"shared"

        requirements_file = self.personality.personality_package_path / "requirements.txt"
        # Step 2: Install dependencies using pip from requirements.txt
        subprocess.run(["pip", "install", "--upgrade", "-r", str(requirements_file)])            
        ASCIIColors.success("Installed successfully")

    
    def prepare(self):
        if self.arxiv is None:
            import arxiv
            self.arxiv = arxiv
        if self.arxiv is None:
            import arxiv
            self.arxiv = arxiv

    def help(self, prompt="", full_context=""):
        self.personality.InfoMessage(self.personality.help)

    def search_analyze_organize_summarize(self, prompt="", full_context="", callback=None, context_state=None, client:Client=None):
        self.prepare()

        download_folder = self.personality.lollms_paths.personal_outputs_path/"research_articles"
        self.warning(f"You did not specify an analysis folder path to put the output into, please do that in the personality settings page.\nUsing default path {download_folder}")
        if self.personality_config.research_subject=="":
            self.personality.InfoMessage("Please set the research subject entry in the personality settings")
            return
        self.new_message("")
        self.search_organize_and_summarize(full_context, self.personality_config.research_subject, context_state, client)


    def analyze_articles(self, prompt="", full_context="", client = None):
        download_folder = self.personality.lollms_paths.personal_outputs_path/"research_articles"
        self.warning(f"You did not specify an analysis folder path to put the output into, please do that in the personality settings page.\nUsing default path {download_folder}")
        
        if len(self.personality.text_files)==0:
            self.personality.InfoMessage("Please upload articles to analyze then trigger this command")
            return
        if self.personality_config.research_subject=="":
            self.personality.InfoMessage("Please set the research subject entry in the personality settings")
            return
        self.new_message("")
        report = []
        articles_checking_text=[]
        self.new_message("")
        for pdf in self.personality.text_files:
            text = TextDocumentsLoader.read_file(pdf)
            tk = self.personality.model.tokenize(text)
            cropped = self.personality.model.detokenize(tk[:self.personality_config.chunk_size])
            title = self.fast_gen(f"{self.start_header_id_template}request: Extract the title of this document from the chunk.\nAnswer directly by the title without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}document title:", callback=self.sink)
            authors = self.fast_gen(f"{self.start_header_id_template}request: Extract the abstract of this document from the chunk.\nAnswer directly by the list of authors without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}authors list:", callback=self.sink)
            if self.personality_config.read_only_first_chunk:
                abstract = self.fast_gen(f"{self.start_header_id_template}request: Extract the abstract of this document from the chunk.\nAnswer directly by the abstract without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}abstract:", callback=self.sink)
            else:
                abstract = self.summarize_text(text,f"{self.start_header_id_template}request: summarize this document chunk.\nAnswer directly by the summary without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}sumary:", callback=self.sink)
            self.analyze_pdf(
                self.personality_config.research_subject,
                "",
                "",
                "",
                "",
                "",
                title,
                authors,
                abstract,
                pdf,
                pdf.name,
                articles_checking_text,
                report,
                client
            )
        report = classify_reports(report)
        self.json("Report",report)
        try:
            self.display_report(report, "Organized bibliography report", client)
        except Exception as ex:
            ASCIIColors.error(ex)

        self.summarize_report(report, download_folder, client)


    def analyze_pdf(
                        self,
                        research_subject, 
                        pdf_url, 
                        doi,
                        journal_ref,
                        publication_date,
                        last_update_date,
                        title, 
                        authors, 
                        abstract,
                        file_name, 
                        document_file_name, 
                        articles_checking_text, 
                        report,
                        client):
        fn = str(file_name).replace('\\','/')
        if self.personality_config.read_the_whole_article:
            text = TextDocumentsLoader.read_file(file_name)
            tk = self.personality.model.tokenize(text)
            cropped = self.personality.model.detokenize(tk[:self.personality_config.chunk_size])            
            if self.personality_config.read_only_first_chunk:
                abstract = self.fast_gen(f"{self.start_header_id_template}request: Extract the abstract of this document from the chunk.\nAnswer directly by the abstract without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}abstract:")
            else:
                abstract = self.summarize_text(text,f"{self.start_header_id_template}request: summarize this document chunk.\nAnswer directly by the summary without any extra comments.{self.separator_template}{self.start_header_id_template} Document chunk:\n{cropped}{self.separator_template}{self.start_header_id_template}sumary:", callback=self.sink)

        relevance_score = self.fast_gen("\n".join([
            f"{self.start_header_id_template}{self.system_message_template}:",
            "Assess the relevance of a document in relation to a user's subject proposal. Provide a relevance score out of 10, with a score of 10 indicating that the document is a precise match with the proposed subject. Carefully examine the document's content and ensure it directly addresses the subject requested, without straying off-topic or loosely linking unrelated concepts through the use of similar terms. Thoroughly understand the user's prompt to accurately determine if the document is indeed pertinent to the requested subject.",
            "Answer with an integer from 0 to 10 that reflects the relevance of the document for the subject.",
            "Do not answer with text, just a single integer value without explanation.",
            f"{self.start_header_id_template}document:",
            f"title: {title}",
            f"content: {abstract}",
            f"{self.start_header_id_template}subject:{research_subject}",
            f"{self.start_header_id_template}relevance_value:"]), 10,
            debug=self.personality.config.debug, 
            callback=self.sink)
        relevance_score = self.find_numeric_value(relevance_score)
        if relevance_score is None:
            relevance="unknown"
            relevance_explanation = ""
            report_entry={
                "title":title,
                "authors":authors,
                "abstract":abstract,
                "relevance":relevance,
                "relevance_score":0,
                "explanation":relevance_explanation,
                "url":pdf_url,
                "file_path":str(file_name)
            }
            relevance = f'<p style="color: red;">{relevance}</p>'
            articles_checking_text.append(self.build_a_document_block(f"{title}","",f"<b>Authors</b>: {authors}\n<br><b>File</b>:{self.build_a_file_link(fn, client,document_file_name)}<br><b>Relevance:</b>\n{relevance}<br>"))
            report.append(report_entry)
            self.set_message_content("\n".join(articles_checking_text))
            self.warning("The AI agent didn't respond to the relevance question correctly")
            return False
        if relevance_score>=float(self.personality_config.relevance_check_severity):
            self.abstract_vectorizer.add_document(f"title:{title}\nauthors:{authors}\nabstract:{abstract}",pdf_url.split('/')[-1])
            relevance = f"relevance score {relevance_score}/10"
            relevance_explanation = self.fast_gen("\n".join([
                    f"{self.start_header_id_template}{self.system_message_template}:",
                    "Explain why you think this document is relevant to the subject by summerizing the abstract and hilighting interesting information that can serve the subject."
                    f"{self.start_header_id_template}document:",
                    f"title: {title}",
                    f"authors: {authors}",
                    f"content: {abstract}",
                    f"{self.start_header_id_template}subject: {research_subject}",
                    f"{self.start_header_id_template}Explanation: "                    
                    ]), self.personality_config.max_generation_prompt_size,
                debug=self.personality.config.debug,
                callback=self.sink)
        else:
            relevance = "irrelevant"
            relevance_explanation = ""

        report_entry={
            "title":title,
            "authors":authors,
            "abstract":abstract,
            "relevance":relevance,
            "relevance_score":relevance_score,
            "explanation":relevance_explanation,
            "url":pdf_url,
            "doi":doi,
            "journal_ref":journal_ref,
            "publication_date":publication_date,            
            "last_update_date":last_update_date,
            "file_path":str(file_name),
            "fn":fn,
            "document_file_name":document_file_name
        }
        relevance = f'<p style="color: red;">{relevance}</p>' if relevance=="irrelevant" else f'<p style="color: green;">{relevance}</p>\n<b>Explanation</b><br>{relevance_explanation}'  if relevance_score>float(self.personality_config.relevance_check_severity) else f'<p style="color: gray;">{relevance}</p>' 
        
        articles_checking_text.append(self.build_a_document_block(f"{title}","","\n".join([
            f"<b>Authors</b>: {authors}<br>",
            f"<b>File</b>:{self.build_a_file_link(fn,document_file_name)}<br>",
            f"<b>doi:</b>\n{doi}<br>"
            f"<b>journal_ref:</b>\n{journal_ref}<br>"
            f"<b>publication_date:</b>\n{publication_date}<br>"
            f"<b>last_update_date:</b>\n{last_update_date}<br>"
            f"<b>Relevance:</b>\n{relevance}<br>"
            ]))
            )
        self.set_message_content("\n".join(articles_checking_text))
        report.append(report_entry)
        return True
    
    def display_report(self, report, title="Report", client:Client=None):
        text = "<h2> "+title+"</h2>\n"
        for entry in report:
            if entry['relevance']=="irrelevant" or entry['relevance'] is None or entry['relevance']=="unknown":
                continue 
            relevance = f'<p style="color: green;">{entry["relevance"]}</p>\n<b>Explanation</b><br>{entry["explanation"]}' 
            text+=self.build_a_document_block(f"{entry['title']}","","\n".join([
                f"<b>Authors</b>: {entry['authors']}<br>",
                f"<b>File</b>:{self.build_a_file_link(entry['fn'],client,entry['document_file_name'])}<br>",
                f"<b>doi:</b>\n{report['doi']}<br>",
                f"<b>journal_ref:</b>\n{report['journal_ref']}<br>",
                f"<b>publication_date:</b>\n{report['publication_date']}<br>",
                f"<b>last_update_date:</b>\n{report['last_update_date']}<br>",
                relevance
                ])
                )
        self.new_message("")
        self.set_message_content(text)
        
        output_file = client.discussion_path/"organized_search_results.html" if client is not None else None
        if output_file:
            with open(output_file,"w",encoding="utf-8") as f:
                f.write("\n".join([
                    "<html>",
                    "<head>",
                    "</head>",
                    "<body>",
                    text,
                    "</body>",
                    "</html>",
                ])
                )
            text += "\n" + self.build_a_file_link(output_file, client,"Click here to vew the generated html file")
            self.set_message_content(text)

        return text
    def build_query(self, prompt,  context_details, previous_keywords=""):
            self.step_start("Building query...")
            self.set_message_content("")
            keywords = self.fast_gen(f"{self.start_header_id_template}".join([
                f"{self.start_header_id_template}{self.system_message_template}:",
                "Act as arxiv search specialist.",
                "You are very fluent at crafting search queries related to the subject",
                "you master search query formulas and can craft them efficiently to answer the user request",
                "Your job is to reformulate the user requestion into a search query.",
                "Answer with only the keywords (do not use multiple keywords, just three at maximum)",
                "We will do multiple passes of search so be very specific and do consize",
                self.system_custom_header('context discussion'),
                context_details.discussion_messages,
                self.system_custom_header("user prompt") + prompt,
                previous_keywords,
                self.ai_custom_header("keywords")
            ]),
            self.personality_config.max_generation_prompt_size,
            debug=self.personality.config.debug,
            callback=self.sink)
            self.step_end("Building query...")
            self.set_message_content(keywords)
            if keywords=="":
                ASCIIColors.error("The AI failed to build a keywords list. Using the prompt as keywords")
                keywords=prompt 
            return keywords       
    def search(self, previous_discussion_text, prompt, context_details:LollmsContextDetails=None, client:Client=None):


        #Prepare full report
        report = []

        # Define your search query
        query = prompt

        # output
        articles_checking_text = []


        # Specify the folder where you want to save the articles
        download_folder = self.personality.lollms_paths.personal_outputs_path/"research_articles"

        # Create the download folder if it doesn't exist
        download_folder.mkdir(parents=True, exist_ok=True)
        nb_found=0
        previous_keywords = ""
        query = ""
        while nb_found<self.personality_config.nb_arxiv_results:
            if self.personality_config.Formulate_search_query:
                previous_keywords += self.system_custom_header("previous keywords") + query +"\n"+ self.system_custom_header("found articles") + nb_found if query else ""
                keywords = self.build_query(prompt, context_details, previous_keywords)
            else:
                keywords=query
            articles_checking_text.append(self.build_a_document_block("Keywords","",keywords))
            self.set_message_content("\n".join(articles_checking_text))
            
            self.step_end(f"Searching and processing {self.personality_config.nb_arxiv_results+self.personality_config.nb_hal_results} documents")
            
            # Search for articles
       
            self.step_start(f"Searching articles on arxiv")
            # "title": title,
            # "authors": authors,
            # "affiliations": affiliations,
            # "abstract": abstract,
            # "published_date": published_date,
            # "journal_ref": journal_ref,
            # "pdf_url": pdf_url,
            # "local_url": local_url
            html_output, pdf_info = arxiv_pdf_search(
                                keywords, 
                                self.personality_config.nb_arxiv_results, sort_by=self.personality_config.sort_by,
                                start_date=self.personality_config.start_date if self.personality_config.start_date!="" else None,
                                end_date=self.personality_config.end_date if self.personality_config.end_date!="" else None,
                                author=self.personality_config.author if self.personality_config.author!="" else None,
                                client=client)
            # search_results_ = self.arxiv.Search(query=query, max_results=self.personality_config.nb_arxiv_results).results()
            self.step_end(f"Searching articles on arxiv")
            nb_found += self.personality_config.nb_arxiv_results
            articles_checking_text.append(self.build_a_document_block(f"Searching on arxiv {self.personality_config.nb_arxiv_results} articles.","",f"Found : {len(pdf_info)} articles on the subject"))
            self.set_message_content("\n".join(articles_checking_text))
            
            # Download and save articles
            for i,(key, val)  in enumerate(pdf_info.items()):
                pdf_url = val["pdf_url"]
                doi = ""
                journal_ref = val["journal_ref"]
                authors = val["authors"]
                local_url = val["local_url"]
                title = val["title"]
                abstract = val["abstract"]
                document_file_name = local_url.split('/')[-1]
                try:
                    try:
                        publication_date = val["published_date"]
                    except Exception as ex:
                        publication_date = "Unknown"
                    
                    if pdf_url:
                        self.step_start(f"Processing document {i+1}/{self.personality_config.nb_arxiv_results}: {document_file_name}")
                        # Get the PDF content
                        if self.analyze_pdf(
                                            query, 
                                            pdf_url, 
                                            doi,
                                            journal_ref,
                                            publication_date,
                                            "",
                                            title, 
                                            authors, 
                                            abstract, 
                                            local_url, 
                                            document_file_name, 
                                            articles_checking_text, 
                                            report,
                                            client
                                        ):
                            self.step_end(f"Processing document {i+1}/{self.personality_config.nb_arxiv_results}: {document_file_name}")
                        else:
                            self.step_end(f"Processing document {i+1}/{self.personality_config.nb_arxiv_results}: {document_file_name}", False)
                except Exception as ex:
                    ASCIIColors.error(ex)
                    self.step_end(f"Processing document {i+1}/{self.personality_config.nb_arxiv_results}: {document_file_name}", False)

        # ----------------------------------- HAL ----------------------------------

        
        return report, articles_checking_text, download_folder

    def summarize_report(self, report, download_folder, client:Client=None):
        self.new_message("")
        if len(report)>0:
            text_to_summarize = ""
            for entry in report:
                if entry["relevance"]!="irrelevant" and entry["relevance"]!="unchecked":
                    text_to_summarize +=f"{entry['title']}\nauthors: {entry['authors']}\nAbstract: {entry['abstract']}\n"

            self.step_start(f"Summerizing content")
            summary = self.summarize_text(text_to_summarize,"Create a comprehensive scientific bibliography report using markdown format. Include a title and one or more paragraphs summarizing each source's content. Make sure to only list the references cited within the document. Exclude any references not explicitly present in the text.", callback=self.sink)
            self.set_message_content(summary)
            self.step_end(f"Summerizing content")           

            self.step_start(f"Building answer")
            with open(download_folder/"report.json","w") as f:
                json.dump(report, f)

            summary_text=f"\n<b>Summary</b>:\n{summary}"
            with open(download_folder/"summary.md","w",encoding="utf-8") as f:
                f.write(summary_text)
                        
            self.set_message_content(summary_text)
            self.new_message("")
            if self.personality_config.make_survey:
                summary_latex = "```latex\n"+self.fast_gen(
                    self.build_prompt([
                    f"{self.start_header_id_template}instruction: Write a survey article out of the summary.",
                    f"Use academic style and cite the contributions.",
                    f"The author of this survey is Scientific Bibliography Maker AI",
                    f"summary:",
                    f"{summary}",
                    "Output format : a complete latex document that should compile without errors and should contain inline bibliography.",
                    f"{self.start_header_id_template}Output:",
                    "```latex\n"]), 
                    callback=self.sink
                    )
                code_blocks = self.extract_code_blocks(summary_latex)
                if len(code_blocks)>0:
                    for code_block in code_blocks[:1]:
                        self.set_message_content(
                            "\n".join([
                                "```latex",
                                f"{code_block['content']}",
                                "```"
                            ])
                        )
                        with open(download_folder/f"{self.personality_config.output_file_name}.tex","w",encoding="utf-8") as f:
                            f.write(code_block["content"])
                    if self.personality_config.pdf_latex_path!="":
                        output_file = download_folder/f"{self.personality_config.output_file_name}.tex"
                        self.compile_latex(output_file,self.personality_config.pdf_latex_path)
                        self.set_message_content(
                            "\n".join([
                                "```latex",
                                f"{code_block['content']}",
                                "```",
                                self.build_a_file_link(str(output_file).replace(".tex",".pdf"),client,"Click here to vew the generated PDF file")
                            ])
                        )

        else:
            self.personality.error("No article found about this subject!")
            self.set_message_content("No article found about this subject!\nLet me try another query!")


    def search_organize_and_summarize(self, previous_discussion_text, prompt, context_details:LollmsContextDetails=None, client:Client=None):
        report, articles_checking_text, download_folder = self.search(previous_discussion_text, prompt, context_details=context_details, client=client)
        report = classify_reports(report)
        self.json("Report",report)
        try:
            self.display_report(report, "Organized bibliography report", client)
        except Exception as ex:
            ASCIIColors.error(ex)

        self.summarize_report(report, download_folder, client)


    def run_workflow(self,  context_details:LollmsContextDetails=None, client:Client=None,  callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None):
        """
        This function generates code based on the given parameters.

        Args:
            full_prompt (str): The full prompt for code generation.
            prompt (str): The prompt for code generation.
            context_details (dict): A dictionary containing the following context details for code generation:
                - conditionning (str): The conditioning information.
                - documentation (str): The documentation information.
                - knowledge (str): The knowledge information.
                - user_description (str): The user description information.
                - discussion_messages (str): The discussion messages information.
                - positive_boost (str): The positive boost information.
                - negative_boost (str): The negative boost information.
                - current_language (str): The force language information.
                - fun_mode (str): The fun mode conditionning text
                - ai_prefix (str): The AI prefix information.
            n_predict (int): The number of predictions to generate.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.
            client: The current client information

        Returns:
            None
        """
        prompt = context_details.prompt
        previous_discussion_text = context_details.discussion_messages
        self.callback = callback
        self.prepare()

        self.search_organize_and_summarize(previous_discussion_text, prompt, context_details, client)

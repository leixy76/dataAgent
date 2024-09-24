##解析抽取手册数据，进行chunk后 对chunk数据进行QA抽取
from pathlib import Path
import re
import threading
import uuid

import loguru

from entities.dataset_sft_entity import DatasetsTextSFTFormat
from entities.document import Document
from llm import LLMApi
from parser.cleaner.clean_processor import CleanProcessor
from parser.extract_processor import EtlType, ExtractProcessor
from parser.markdown_extractor import MarkdownExtractor
from parser.pdf_extractor import PdfExtractor
from parser.splitter.fixed_text_splitter import FixedRecursiveCharacterTextSplitter
from prompt import GENERATOR_QA_PROMPT_EN, GENERATOR_QA_PROMPT_ZH, GENERATOR_QA_PROMPT_ZH_1, GENERATOR_QA_PROMPT_ZH_2
from utils.helper import generate_text_hash, write_json_file_line


class TextSFTDatasets():
    def __init__(self, file_path):
        self.file_path = file_path
        
    def extract_text(self):
        return ExtractProcessor.extract(self.file_path)
    
    def chunk_text_to_qa_unstructured(self, documents: list[Document], **kwargs) -> list[Document]:
        all_qa_documents = []
        total_tokens_num = []
        for document in documents:
            threads = []
            document_format_thread = threading.Thread(
                        target=self._format_qa_document,
                        kwargs={
                            "document_node": document,
                            "all_qa_documents": all_qa_documents,
                            "total_tokens_num":total_tokens_num,
                            "document_language": kwargs.get("doc_language", "Chinese"),

                        },
            )
            threads.append(document_format_thread)
            document_format_thread.start()
            for thread in threads:
                thread.join()
        loguru.logger.info(f"total_tokens_num:{sum(total_tokens_num)}")
        return all_qa_documents

    def chunk_text_to_qa(self, documents: list[Document], **kwargs) -> list[Document]:
        splitter = self._get_splitter()
        all_documents = []
        all_qa_documents = []
        for document in documents:
            # document clean
            document_text = CleanProcessor.clean(document.page_content, True)
            document.page_content = document_text
            # parse document to nodes
            document_nodes = splitter.split_documents([document])
            split_documents = []
            for document_node in document_nodes:
                if document_node.page_content.strip():
                    doc_id = str(uuid.uuid4())
                    hash = generate_text_hash(document_node.page_content)
                    document_node.metadata["doc_id"] = doc_id
                    document_node.metadata["doc_hash"] = hash
                    # delete Splitter character
                    page_content = document_node.page_content
                    if page_content.startswith(".") or page_content.startswith("。"):
                        page_content = page_content[1:]
                    else:
                        page_content = page_content
                    document_node.page_content = page_content
                    split_documents.append(document_node)
            all_documents.extend(split_documents)
            for i in range(0, len(all_documents), 10):
                threads = []
                sub_documents = all_documents[i: i + 10]
                for doc in sub_documents:
                    document_format_thread = threading.Thread(
                        target=self._format_qa_document,
                        kwargs={
                            "document_node": doc,
                            "all_qa_documents": all_qa_documents,
                            "document_language": kwargs.get("doc_language", "Chinese"),
                        },
                    )
                    threads.append(document_format_thread)
                    document_format_thread.start()
                for thread in threads:
                    thread.join()
        return all_documents

    def _get_splitter(self):
        separator = "\n"
        character_splitter = FixedRecursiveCharacterTextSplitter.from_encoder(
            chunk_size=100,
            chunk_overlap=10,
            fixed_separator=separator,
            separators=["\n\n", "。", ". ", " ", ""],
            embedding_model_instance=None,
        )
        return character_splitter

    def _llm_generate_qa_document(self, query, document_language: str):
        ##TODO 这里prompt要更改一下
        prompt = GENERATOR_QA_PROMPT_ZH.format(language=document_language)
        # prompt = GENERATOR_QA_PROMPT_ZH_2.replace("{{document}}",query)
        prompt = LLMApi.build_prompt(query,prompt)
        response = LLMApi.call_llm(prompt)
        answer = response["content"]
        return answer.strip(),response['total_tokens']

    def _format_qa_document(self, document_node, all_qa_documents, total_tokens_num,document_language):
        format_documents = []
        if document_node.page_content is None or not document_node.page_content.strip():
            return
        try:
            # qa model document
            response,total_tokens = self._llm_generate_qa_document(document_node.page_content, document_language)
            total_tokens_num.append(total_tokens)
            document_qa_list = self._format_split_text(response)
            loguru.logger.info(f"document_qa_list:{document_qa_list}")
            qa_documents = []
            for result in document_qa_list:
                qa_document = Document(page_content=result["question"], metadata=document_node.metadata.copy())
                doc_id = str(uuid.uuid4())
                hash = generate_text_hash(result["question"])
                qa_document.metadata["answer"] = result["answer"]
                qa_document.metadata['context']=document_node.page_content
                qa_document.metadata["doc_id"] = doc_id
                qa_document.metadata["doc_hash"] = hash
                qa_documents.append(qa_document)
            format_documents.extend(qa_documents)
        except Exception as e:
            loguru.logger.exception(e)

        all_qa_documents.extend(format_documents)

    def _format_split_text(self, text):
        regex = r"Q\d+:\s*(.*?)\s*A\d+:\s*([\s\S]*?)(?=Q\d+:|$)"
        matches = re.findall(regex, text, re.UNICODE)

        return [{"question": q, "answer": re.sub(r"\n\s*", "\n", a.strip())} for q, a in matches if q and a]

    def build_sft_format(self,all_qa_documents):
        sft_data_list = []
        for document in all_qa_documents:
            data = DatasetsTextSFTFormat(
                instruction="",
                input=document.page_content,
                output=document.metadata["answer"]
            )
            sft_data_list.append(data.to_dict())
        if sft_data_list:
            write_json_file_line(sft_data_list,"data\\handbook_dataset_sft.json")


def test_text_sft_dataset():
    file_path = "data\\《中华人民共和国安全生产法》（2021 年修订版）.pdf"
    file_path_md = "data\\test_readme.md"
    file_path_md = "data\\handbook_test.md"
    file_path_tex = "data\\test.tex"
    ##有问题
    file_path_doc = "data\\《起重设备安装工程施工及验收标准》（征求意见稿）.doc"
    text_sft_dataset = TextSFTDatasets(file_path_tex)
    all_docs = text_sft_dataset.extract_text()
    loguru.logger.info(f"text {len(all_docs)}")
    all_qa_documents = text_sft_dataset.chunk_text_to_qa_unstructured(all_docs)
    text_sft_dataset.build_sft_format(all_qa_documents)


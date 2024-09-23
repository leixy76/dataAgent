##解析抽取手册数据，进行chunk后 对chunk数据进行QA抽取
import re
import threading
import uuid

import loguru

from entities.document import Document
from llm import LLMApi
from parser.cleaner.clean_processor import CleanProcessor
from parser.pdf_extractor import PdfExtractor
from parser.splitter.fixed_text_splitter import FixedRecursiveCharacterTextSplitter
from prompt import GENERATOR_QA_PROMPT
from utils.helper import generate_text_hash


class TextSFTDatasets():
    def __init__(self, file_path):
        self.file_path = file_path
        self.parser = PdfExtractor(self.file_path)

    def extract_text(self):
        return self.parser.extract()

    def chuck_text_to_qa(self, documents: list[Document], **kwargs) -> list[Document]:
        splitter = self._get_splitter()
        all_documents = []
        all_qa_documents = []
        for document in documents:
            # document clean
            document_text = CleanProcessor.clean(document.page_content, kwargs.get("process_rule"))
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
                            "flask_app": "hello world",
                            "tenant_id": kwargs.get("tenant_id"),
                            "document_node": doc,
                            "all_qa_documents": all_qa_documents,
                            "document_language": kwargs.get("doc_language", "English"),
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
            chunk_size=512,
            chunk_overlap=100,
            fixed_separator=separator,
            separators=["\n\n", "。", ". ", " ", ""],
            embedding_model_instance=None,
        )
        return character_splitter

    def _llm_generate_qa_document(self, query, document_language: str):
        ##TODO 这里prompt要更改一下
        prompt = GENERATOR_QA_PROMPT.format(language=document_language)
        prompt = LLMApi.build_prompt(query, prompt)
        response = LLMApi.call_llm(prompt)
        answer = response.message.content
        return answer.strip()

    def _format_qa_document(self, document_node, all_qa_documents, document_language):
        format_documents = []
        if document_node.page_content is None or not document_node.page_content.strip():
            return
        try:
            # qa model document
            response = self._llm_generate_qa_document(document_node.page_content, document_language)
            document_qa_list = self._format_split_text(response)
            qa_documents = []
            for result in document_qa_list:
                qa_document = Document(page_content=result["question"], metadata=document_node.metadata.copy())
                doc_id = str(uuid.uuid4())
                hash = generate_text_hash(result["question"])
                qa_document.metadata["answer"] = result["answer"]
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


def test_text_sft_dataset():
    file_path = "data\\《中华人民共和国安全生产法》（2021 年修订版）.pdf"
    text_sft_dataset = TextSFTDatasets(file_path)
    all_docs = text_sft_dataset.extract_text()
    loguru.logger.info(f"text {len(all_docs)}")
    text_sft_dataset.chuck_text_to_qa(all_docs)


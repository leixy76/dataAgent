from enum import Enum


class RetrievalMethod(Enum):
    SEMANTIC_SEARCH = "semantic_search"
    FULL_TEXT_SEARCH = "full_text_search"
    HYBRID_SEARCH = "hybrid_search"

    @staticmethod
    def is_support_semantic_search(retrieval_method: str) -> bool:
        return retrieval_method in {RetrievalMethod.SEMANTIC_SEARCH.value, RetrievalMethod.HYBRID_SEARCH.value}

    @staticmethod
    def is_support_fulltext_search(retrieval_method: str) -> bool:
        return retrieval_method in {RetrievalMethod.FULL_TEXT_SEARCH.value, RetrievalMethod.HYBRID_SEARCH.value}
    
class EmbeddingInferenceType(Enum):
    SENTENCE_TRANSFORMER = "sentence_transformer"
    FLAG_EMBEDDING = "flagembedding"
    FAST_EMBED = "fastembed"
    TGI_EMBEDDING_API = "tig_embedding_api"
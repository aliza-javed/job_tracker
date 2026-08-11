"""
rag_engine.py
-------------
Retrieval-Augmented Generation engine.
Ranks documents by keyword overlap, builds context for LLM.
"""

import re
from models import RAGDocument, RAGQuery
from utils import clean_text, truncate_text


class RAGEngine:
    """Simple keyword-overlap RAG system (no vector DB needed)."""
    
    def __init__(self):
        self.documents = []
    
    def add_document(self, content, metadata=None):
        """Add a document to the knowledge base."""
        doc = RAGDocument(content=clean_text(content), metadata=metadata or {})
        self.documents.append(doc)
    
    def add_documents(self, doc_list):
        """Add multiple documents."""
        for item in doc_list:
            if isinstance(item, dict):
                self.add_document(item.get("content", ""), item.get("metadata", {}))
            else:
                self.add_document(str(item))
    
    def query(self, user_query, job_description="", top_k=3):
        """
        Retrieve relevant documents, build context.
        
        Pipeline:
        User Query + Job Description
               ↓
        Keyword Extraction
               ↓
        Document Scoring (overlap)
               ↓
        Ranking (top-k)
               ↓
        Context Assembly
               ↓
        LLM Prompt
        """
        rag_query = RAGQuery(user_query, job_description)
        
        # Combine query + job description for retrieval
        combined_query = f"{user_query} {job_description}"
        
        # Extract keywords
        query_keywords = self._extract_keywords(combined_query)
        
        # Score all documents
        scored_docs = []
        for doc in self.documents:
            score = self._score_document(doc, query_keywords)
            doc.score = score
            if score > 0:
                scored_docs.append(doc)
        
        # Rank by score
        scored_docs.sort(key=lambda d: d.score, reverse=True)
        
        # Take top-k
        top_docs = scored_docs[:top_k]
        rag_query.retrieved_docs = top_docs
        
        # Build context string
        context_parts = []
        for i, doc in enumerate(top_docs, 1):
            text = truncate_text(doc.content, 400)
            source = doc.metadata.get("source", f"Document {i}")
            context_parts.append(f"[Source: {source}]\n{text}")
        
        rag_query.context = "\n\n".join(context_parts)
        
        return rag_query
    
    def _extract_keywords(self, text):
        """Extract meaningful words from text."""
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'shall',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'and', 'but', 'or', 'nor', 'not', 'so',
            'yet', 'both', 'either', 'neither', 'each', 'every', 'all',
            'any', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'only', 'own', 'same', 'than', 'too', 'very', 'just', 'because',
            'if', 'when', 'where', 'how', 'what', 'which', 'who', 'whom',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we', 'our',
            'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its',
            'they', 'them', 'their', 'us', 'about', 'up', 'out', 'then'
        }
        
        words = re.findall(r'[a-zA-Z]+', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also extract technical terms (preserve casing)
        tech_terms = re.findall(r'\b(?:python|java|javascript|react|django|flask|aws|docker|sql|mongodb|azure|gcp|node|angular|vue|typescript|postgresql|mysql|redis|kubernetes|terraform|git|ci/cd|linux|rest graphql|microservices|machine learning|deep learning|ai|pandas|numpy|tensorflow|pytorch)\b', text, re.IGNORECASE)
        
        return list(set(keywords + [t.lower() for t in tech_terms]))
    
    def _score_document(self, doc, query_keywords):
        """Score document relevance against keywords."""
        if not query_keywords:
            return 0
        
        doc_keywords = self._extract_keywords(doc.content)
        
        if not doc_keywords:
            return 0
        
        # Count matches
        matches = sum(1 for kw in query_keywords if kw in doc_keywords)
        
        # Normalize by query length and doc length
        score = matches / len(query_keywords)
        
        # Bonus for tech term overlap (weighted higher)
        tech_bonus = 0
        doc_text_lower = doc.content.lower()
        for tech in ['python', 'django', 'react', 'aws', 'docker', 'sql', 'java', 'javascript']:
            if tech in query_keywords and tech in doc_text_lower:
                tech_bonus += 0.1
        
        score = min(score + tech_bonus, 1.0)
        
        # Scale to 0-100 for readability
        return round(score * 100, 2)
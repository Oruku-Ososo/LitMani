import httpx
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from app.config import settings


class OllamaService:
    """Service for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client with proper configuration"""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout, connect=10.0)
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send chat messages to Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to configured model)
            stream: Whether to stream response
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dict with 'message', 'model', 'usage', etc.
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        async with await self._get_client() as client:
            if stream:
                # For streaming, we'll handle it differently
                response = await client.post("/api/chat", json=payload)
                response.raise_for_status()
                return {"stream": True, "data": response.text}
            else:
                response = await client.post("/api/chat", json=payload)
                response.raise_for_status()
                return response.json()
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from Ollama
        
        Yields:
            Chunks of the response text
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        async with await self._get_client() as client:
            async with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Generate text completion using Ollama
        
        Args:
            prompt: Input prompt
            model: Model to use
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Response dict with 'response', 'model', etc.
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with await self._get_client() as client:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json()
    
    async def summarize_text(
        self,
        text: str,
        length: str = "medium",
        style: str = "academic",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Summarize text using Ollama
        
        Args:
            text: Text to summarize
            length: Summary length (short, medium, long)
            style: Summary style (academic, casual, bullet points)
            model: Model to use
            
        Returns:
            Dict with summary and key points
        """
        length_instructions = {
            "short": "Provide a brief 2-3 sentence summary.",
            "medium": "Provide a concise paragraph summary (5-7 sentences).",
            "long": "Provide a detailed summary (2-3 paragraphs).",
        }
        
        style_instructions = {
            "academic": "Use formal academic language.",
            "casual": "Use simple, accessible language.",
            "bullet points": "Present key points as bullet points.",
        }
        
        system_prompt = f"""You are an expert research assistant. Your task is to summarize academic texts.
{length_instructions.get(length, length_instructions['medium'])}
{style_instructions.get(style, style_instructions['academic'])}

Also extract 3-5 key points from the text."""
        
        prompt = f"""Please summarize the following text:

{text}

Provide:
1. A clear summary
2. Key points (as a numbered list)"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.5,  # Lower temperature for more focused summaries
            max_tokens=1500,
        )
        
        # Parse the response to extract summary and key points
        result = response.get("response", "")
        
        return {
            "summary": result,
            "key_points": [],  # Would need better parsing
            "model_used": model or self.default_model,
        }
    
    async def suggest_tags(
        self,
        text: str,
        max_tags: int = 10,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Suggest tags for a document
        
        Args:
            text: Document text
            max_tags: Maximum number of tags to suggest
            model: Model to use
            
        Returns:
            Dict with tags and confidence scores
        """
        prompt = f"""Analyze the following text and suggest {max_tags} relevant tags/keywords.
Return only the tags as a JSON array of strings, nothing else.

Text:
{text}

Tags:"""
        
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=200,
        )
        
        import json
        try:
            tags = json.loads(response.get("response", "[]"))
            if not isinstance(tags, list):
                tags = [tags]
        except:
            tags = [response.get("response", "").strip()]
        
        return {
            "tags": tags[:max_tags],
            "confidence_scores": [1.0] * len(tags[:max_tags]),  # Placeholder
            "model_used": model or self.default_model,
        }
    
    async def generate_citation(
        self,
        paper_data: Dict[str, Any],
        style: str = "apa",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate citation in specified format
        
        Args:
            paper_data: Paper metadata
            style: Citation style (apa, mla, chicago, ieee, harvard)
            model: Model to use
            
        Returns:
            Dict with formatted citation and bibtex
        """
        prompt = f"""Generate a {style.upper()} style citation for the following paper:

Title: {paper_data.get('title', 'N/A')}
Authors: {', '.join(paper_data.get('authors', [])) if isinstance(paper_data.get('authors'), list) else paper_data.get('authors', 'N/A')}
Journal: {paper_data.get('journal', 'N/A')}
Year: {paper_data.get('publication_date', 'N/A')}
DOI: {paper_data.get('doi', 'N/A')}

Provide:
1. The formatted citation
2. BibTeX entry

Format your response as JSON with keys 'citation' and 'bibtex'."""
        
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=0.3,
            max_tokens=500,
        )
        
        import json
        try:
            result = json.loads(response.get("response", "{}"))
        except:
            result = {
                "citation": response.get("response", ""),
                "bibtex": "",
            }
        
        return {
            "citation": result.get("citation", ""),
            "bibtex": result.get("bibtex", ""),
            "style": style,
        }
    
    async def find_related_papers(
        self,
        query_paper: Dict[str, Any],
        library_papers: List[Dict[str, Any]],
        limit: int = 10,
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find papers related to a given paper
        
        Args:
            query_paper: The paper to find related work for
            library_papers: List of papers in the library
            limit: Maximum number of related papers
            model: Model to use
            
        Returns:
            List of related papers with similarity scores
        """
        # This would be better done with embeddings, but we can use LLM for semantic matching
        prompt = f"""Given the following paper:

Title: {query_paper.get('title', 'N/A')}
Abstract: {query_paper.get('abstract', 'N/A')[:500]}

And these candidate papers from the library:
"""
        
        for i, paper in enumerate(library_papers[:20]):  # Limit candidates for context
            prompt += f"\n{i+1}. Title: {paper.get('title', 'N/A')}, Abstract: {paper.get('abstract', 'N/A')[:200]}"
        
        prompt += f"\n\nSelect the top {limit} most related papers based on topic, methodology, and domain. Return their indices (1-based) and a brief reason for each."
        
        response = await self.generate(
            prompt=prompt,
            model=model,
            temperature=0.5,
            max_tokens=1000,
        )
        
        # Parse response to get related papers
        # This is a simplified version - would need better parsing
        return {
            "related_papers": [],
            "reasons": [],
        }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama"""
        async with await self._get_client() as client:
            response = await client.get("/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
    
    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama registry"""
        async with await self._get_client() as client:
            payload = {"name": model_name}
            response = await client.post("/api/pull", json=payload)
            response.raise_for_status()
            return response.json()


# Singleton instance
ollama_service = OllamaService()

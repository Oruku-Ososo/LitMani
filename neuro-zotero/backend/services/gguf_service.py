from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from app.config import settings


class GGUFService:
    """
    Service for loading and running GGUF models directly using llama-cpp-python
    
    This allows running LLMs locally without Ollama, with fine-grained control
    over model parameters and execution.
    """
    
    def __init__(self):
        self.model_path = settings.GGUF_MODEL_PATH
        self.default_model = settings.GGUF_DEFAULT_MODEL
        self.n_ctx = settings.GGUF_N_CTX
        self.n_gpu_layers = settings.GGUF_N_GPU_LAYERS
        self.n_threads = settings.GGUF_N_THREADS
        
        # Cache for loaded models
        self._loaded_models: Dict[str, Any] = {}
    
    def _get_model_path(self, model_name: str) -> Path:
        """Get full path to model file"""
        model_path = Path(self.model_path) / model_name
        if not model_path.exists():
            # Try without .gguf extension
            model_path = Path(self.model_path) / f"{model_name}.gguf"
        return model_path
    
    def load_model(
        self,
        model_name: Optional[str] = None,
        n_ctx: Optional[int] = None,
        n_gpu_layers: Optional[int] = None,
        n_threads: Optional[int] = None,
    ) -> Any:
        """
        Load a GGUF model using llama-cpp-python
        
        Args:
            model_name: Name of the model file (default: configured default model)
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU
            n_threads: Number of CPU threads
            
        Returns:
            Llama model instance
        """
        model_name = model_name or self.default_model
        n_ctx = n_ctx or self.n_ctx
        n_gpu_layers = n_gpu_layers or self.n_gpu_layers
        n_threads = n_threads or self.n_threads
        
        # Check if already loaded
        cache_key = f"{model_name}_{n_ctx}_{n_gpu_layers}"
        if cache_key in self._loaded_models:
            return self._loaded_models[cache_key]
        
        model_path = self._get_model_path(model_name)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}. "
                f"Please download a GGUF model to {self.model_path}"
            )
        
        try:
            from llama_cpp import Llama
            
            model = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                verbose=settings.DEBUG,
            )
            
            self._loaded_models[cache_key] = model
            return model
            
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with: pip install llama-cpp-python"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text using a loaded GGUF model
        
        Args:
            prompt: Input prompt
            model_name: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: Stop sequences
            stream: Whether to stream output
            
        Returns:
            Generation result with text and metadata
        """
        model = self.load_model(model_name)
        
        try:
            output = model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                stream=stream,
            )
            
            if stream:
                # For streaming, we'll collect all chunks
                full_response = ""
                for chunk in output:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("text", "")
                        full_response += delta
                
                return {
                    "response": full_response,
                    "model_used": model_name or self.default_model,
                    "usage": {
                        "prompt_tokens": 0,  # Would need to track separately
                        "completion_tokens": 0,
                    },
                }
            else:
                return {
                    "response": output["choices"][0]["text"],
                    "model_used": model_name or self.default_model,
                    "usage": {
                        "prompt_tokens": output.get("usage", {}).get("prompt_tokens", 0),
                        "completion_tokens": output.get("usage", {}).get("completion_tokens", 0),
                    },
                }
                
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")
    
    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Create chat completion using a GGUF model
        
        Args:
            messages: List of chat messages with role and content
            model_name: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            stream: Whether to stream
            
        Returns:
            Chat completion response
        """
        model = self.load_model(model_name)
        
        # Format messages for chat
        try:
            # llama-cpp-python has built-in chat template support
            output = model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
            )
            
            if stream:
                full_response = ""
                for chunk in output:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        full_response += delta
                
                return {
                    "message": {"role": "assistant", "content": full_response},
                    "model": model_name or self.default_model,
                }
            else:
                return {
                    "message": output["choices"][0]["message"],
                    "model": model_name or self.default_model,
                    "usage": output.get("usage", {}),
                }
                
        except Exception as e:
            # Fallback: format as prompt manually
            prompt = self._format_chat_as_prompt(messages)
            return self.generate(
                prompt=prompt,
                model_name=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
            )
    
    def _format_chat_as_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages as a single prompt (fallback method)"""
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant: ")
        return "".join(prompt_parts)
    
    def get_embedding(
        self,
        text: str,
        model_name: Optional[str] = None,
    ) -> List[float]:
        """
        Get embedding vector for text
        
        Note: Not all GGUF models support embeddings.
        This works best with specialized embedding models.
        
        Args:
            text: Text to embed
            model_name: Embedding model to use
            
        Returns:
            Embedding vector as list of floats
        """
        model = self.load_model(model_name)
        
        try:
            embedding = model.embed(text)
            return embedding
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all GGUF models available in the model directory"""
        model_dir = Path(self.model_path)
        
        if not model_dir.exists():
            return []
        
        models = []
        for file in model_dir.glob("*.gguf"):
            models.append({
                "name": file.name,
                "path": str(file),
                "size_bytes": file.stat().st_size,
                "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
            })
        
        return models
    
    def unload_model(self, model_name: Optional[str] = None):
        """Unload a model from memory"""
        if model_name is None:
            # Unload all models
            self._loaded_models.clear()
        else:
            # Find and remove matching models
            keys_to_remove = [
                key for key in self._loaded_models.keys() 
                if key.startswith(model_name)
            ]
            for key in keys_to_remove:
                del self._loaded_models[key]
    
    def summarize_text(
        self,
        text: str,
        length: str = "medium",
        style: str = "academic",
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Summarize text using GGUF model"""
        length_instructions = {
            "short": "Provide a brief 2-3 sentence summary.",
            "medium": "Provide a concise paragraph summary (5-7 sentences).",
            "long": "Provide a detailed summary (2-3 paragraphs).",
        }
        
        system_prompt = f"""You are an expert research assistant specializing in summarizing academic papers.
{length_instructions.get(length, length_instructions['medium'])}
Use {style} language.

Extract 3-5 key points after the summary."""
        
        prompt = f"""{system_prompt}

Text to summarize:
{text}

Summary:"""
        
        result = self.generate(
            prompt=prompt,
            model_name=model_name,
            max_tokens=1500,
            temperature=0.5,
        )
        
        return {
            "summary": result["response"],
            "key_points": [],  # Would need parsing
            "model_used": model_name or self.default_model,
        }
    
    def suggest_tags(
        self,
        text: str,
        max_tags: int = 10,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest tags for a document"""
        prompt = f"""Analyze this text and suggest {max_tags} relevant keywords/tags.
Return ONLY a JSON array of strings.

Text:
{text[:2000]}  # Limit context

Tags:"""
        
        result = self.generate(
            prompt=prompt,
            model_name=model_name,
            max_tokens=300,
            temperature=0.3,
        )
        
        # Parse JSON response
        import json
        try:
            tags = json.loads(result["response"].strip())
            if not isinstance(tags, list):
                tags = [result["response"].strip()]
        except:
            tags = [result["response"].strip()]
        
        return {
            "tags": tags[:max_tags],
            "confidence_scores": [1.0] * len(tags[:max_tags]),
            "model_used": model_name or self.default_model,
        }


# Singleton instance
gguf_service = GGUFService()

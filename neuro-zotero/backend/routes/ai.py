from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from models.paper import Paper, User, AITask
from models.schemas import (
    ChatRequest, ChatResponse, SummarizeRequest, SummarizeResponse,
    TagSuggestionRequest, TagSuggestionResponse, CitationGenerateRequest,
    CitationGenerateResponse, RelatedPapersRequest, RelatedPapersResponse,
    AITaskResponse
)
from services.ollama_service import ollama_service
from services.gguf_service import gguf_service
from app.config import settings
import json

router = APIRouter(prefix="/ai", tags=["AI/LLM"])


def get_ai_service(use_gguf: bool = False):
    """Get appropriate AI service based on configuration"""
    if use_gguf:
        return gguf_service
    return ollama_service


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Chat with AI assistant about your research library
    
    Can include context from specific papers in your library.
    """
    try:
        # Determine which service to use
        use_gguf = request.model and ".gguf" in request.model.lower()
        ai_service = get_ai_service(use_gguf)
        
        # Add context from papers if specified
        messages = request.messages.copy()
        
        if request.context_paper_ids:
            # Fetch papers and add their content as context
            papers = db.query(Paper).filter(
                Paper.id.in_(request.context_paper_ids)
            ).all()
            
            context = "Here are some relevant papers from my library:\n\n"
            for paper in papers:
                context += f"Title: {paper.title}\n"
                context += f"Authors: {paper.authors}\n"
                if paper.abstract:
                    context += f"Abstract: {paper.abstract[:500]}...\n"
                context += "\n"
            
            # Add context to system message or create one
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful research assistant. "
                    "Help the user understand and work with their research papers. "
                    "Provide accurate, scholarly information.\n\n" + context
                )
            }
            
            # Insert system message at the beginning
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\n" + context
            else:
                messages.insert(0, system_message)
        
        # Get response from AI
        if use_gguf:
            response = await ai_service.create_chat_completion(
                messages=messages,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream,
            )
            
            return ChatResponse(
                response=response["message"]["content"],
                model=response["model"],
                usage=response.get("usage"),
            )
        else:
            response = await ai_service.chat(
                messages=messages,
                model=request.model,
                stream=request.stream,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            return ChatResponse(
                response=response["message"]["content"],
                model=response["model"],
                usage=response.get("usage"),
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_paper(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
):
    """
    Generate an AI summary of a paper
    """
    try:
        # Fetch paper
        paper = db.query(Paper).filter(Paper.id == request.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get text to summarize
        text_to_summarize = ""
        if paper.abstract:
            text_to_summarize = paper.abstract
        else:
            # Would need to extract text from PDF
            # For now, use title and notes
            text_to_summarize = f"{paper.title}\n{paper.notes or ''}"
        
        if not text_to_summarize.strip():
            raise HTTPException(
                status_code=400, 
                detail="No content available to summarize"
            )
        
        # Determine which service to use
        use_gguf = request.model and ".gguf" in request.model.lower()
        ai_service = get_ai_service(use_gguf)
        
        # Generate summary
        if use_gguf:
            result = ai_service.summarize_text(
                text=text_to_summarize,
                length=request.length,
                style=request.style,
                model_name=request.model,
            )
        else:
            result = await ai_service.summarize_text(
                text=text_to_summarize,
                length=request.length,
                style=request.style,
                model=request.model,
            )
        
        # Create task record
        task = AITask(
            paper_id=paper.id,
            task_type="summarize",
            status="completed",
            input_data=json.dumps({"text_length": len(text_to_summarize)}),
            output_data=json.dumps(result),
            model_used=result["model_used"],
        )
        db.add(task)
        db.commit()
        
        return SummarizeResponse(
            summary=result["summary"],
            key_points=result.get("key_points", []),
            model_used=result["model_used"],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/suggest-tags", response_model=TagSuggestionResponse)
async def suggest_tags(
    request: TagSuggestionRequest,
    db: Session = Depends(get_db),
):
    """
    Get AI-suggested tags for a paper or text
    """
    try:
        # Get text to analyze
        text = request.text
        
        if request.paper_id:
            paper = db.query(Paper).filter(Paper.id == request.paper_id).first()
            if not paper:
                raise HTTPException(status_code=404, detail="Paper not found")
            
            # Combine abstract, title, and notes
            text = f"{paper.title}\n{paper.abstract or ''}\n{paper.notes or ''}"
        
        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text available for tag suggestion"
            )
        
        # Determine which service to use
        use_gguf = False  # Could add model parameter
        ai_service = get_ai_service(use_gguf)
        
        # Generate tags
        if use_gguf:
            result = gguf_service.suggest_tags(
                text=text,
                max_tags=request.max_tags,
            )
        else:
            result = await ollama_service.suggest_tags(
                text=text,
                max_tags=request.max_tags,
            )
        
        return TagSuggestionResponse(
            tags=result["tags"],
            confidence_scores=result.get("confidence_scores", []),
            model_used=result["model_used"],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tag suggestion failed: {str(e)}")


@router.post("/generate-citation", response_model=CitationGenerateResponse)
async def generate_citation(
    request: CitationGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Generate citation in specified format
    """
    try:
        # Fetch paper
        paper = db.query(Paper).filter(Paper.id == request.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Prepare paper data
        paper_data = {
            "title": paper.title,
            "authors": paper.authors,
            "journal": paper.journal,
            "publication_date": str(paper.publication_date) if paper.publication_date else None,
            "doi": paper.doi,
            "publisher": paper.publisher,
            "url": paper.url if request.include_url else None,
        }
        
        # Determine which service to use
        # Citations work better with Ollama typically
        ai_service = ollama_service
        
        # Generate citation
        result = await ai_service.generate_citation(
            paper_data=paper_data,
            style=request.style,
        )
        
        return CitationGenerateResponse(
            citation=result["citation"],
            style=result["style"],
            bibtex=result.get("bibtex"),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation generation failed: {str(e)}")


@router.post("/find-related", response_model=RelatedPapersResponse)
async def find_related_papers(
    request: RelatedPapersRequest,
    db: Session = Depends(get_db),
):
    """
    Find papers related to a given paper using AI
    """
    try:
        # Fetch query paper
        query_paper = db.query(Paper).filter(Paper.id == request.paper_id).first()
        if not query_paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Fetch all other papers (could be optimized with filters)
        all_papers = db.query(Paper).filter(Paper.id != request.paper_id).all()
        
        # Limit to reasonable number for AI processing
        candidate_papers = all_papers[:50]
        
        # Prepare paper data
        query_data = {
            "title": query_paper.title,
            "abstract": query_paper.abstract,
            "tags": query_paper.tags,
        }
        
        candidates_data = [
            {
                "id": p.id,
                "title": p.title,
                "abstract": p.abstract,
                "tags": p.tags,
            }
            for p in candidate_papers
        ]
        
        # Use AI to find related papers
        # Note: This is a simplified approach - embeddings would be better
        ai_service = ollama_service
        
        result = await ai_service.find_related_papers(
            query_paper=query_data,
            library_papers=candidates_data,
            limit=request.limit,
        )
        
        # Convert to response format
        related_papers = []
        similarity_scores = []
        
        # For now, return empty - would need proper implementation
        # In production, use embedding similarity
        
        return RelatedPapersResponse(
            related_papers=[],
            similarity_scores=[],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finding related papers failed: {str(e)}")


@router.get("/models")
async def list_models():
    """List available AI models"""
    try:
        # Get Ollama models
        ollama_models = await ollama_service.list_models()
        
        # Get GGUF models
        gguf_models = gguf_service.list_available_models()
        
        return {
            "ollama_models": ollama_models,
            "gguf_models": gguf_models,
            "default_model": settings.OLLAMA_MODEL,
            "default_gguf_model": settings.GGUF_DEFAULT_MODEL,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/tasks", response_model=List[AITaskResponse])
async def list_ai_tasks(
    paper_id: Optional[int] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List AI tasks with optional filtering"""
    try:
        query = db.query(AITask)
        
        if paper_id:
            query = query.filter(AITask.paper_id == paper_id)
        
        if task_type:
            query = query.filter(AITask.task_type == task_type)
        
        tasks = query.order_by(AITask.created_at.desc()).limit(50).all()
        
        return tasks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")

import os
import json
import requests

RAG_HOST = os.getenv("RAG_HOST", "api-knowledgebase.mlp.ap-southeast-1.bytepluses.com")
RAG_API_KEY = os.getenv("RAG_API_KEY", "")
RAG_SERVICE_RESOURCE_ID = os.getenv("RAG_SERVICE_RESOURCE_ID", "")


def _call_api(method: str, path: str, data: dict = None) -> dict:
    """Call RAG Knowledge Base API with Bearer API Key authentication."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": RAG_HOST,
        "Authorization": f"Bearer {RAG_API_KEY}",
    }
    body = json.dumps(data) if data is not None else None
    url = f"http://{RAG_HOST}{path}"
    resp = requests.request(method, url, headers=headers, data=body, timeout=30)
    resp.encoding = "utf-8"
    return resp.json()


def knowledge_service_chat(query: str, stream: bool = False) -> dict:
    """
    Query the knowledge base using the service chat endpoint.
    Uses the deployed knowledge service with RAG retrieval + LLM generation.
    """
    body = {
        "service_resource_id": RAG_SERVICE_RESOURCE_ID,
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ],
        "stream": stream,
    }
    return _call_api("POST", "/api/knowledge/service/chat", body)


def search_knowledge(collection_name: str, query: str, limit: int = 10,
                     resource_id: str = None, project: str = "default") -> dict:
    """
    Search knowledge base for relevant claim information using semantic retrieval.
    Uses search_knowledge endpoint for pure retrieval (no LLM generation).
    """
    body = {
        "query": query,
        "limit": limit,
        "post_processing": {
            "rerank_switch": True,
            "rerank_model": "base-multilingual-rerank",
            "retrieve_count": 25,
            "chunk_group": True,
        },
    }

    if resource_id:
        body["resource_id"] = resource_id
    elif collection_name:
        body["name"] = collection_name

    if project:
        body["project"] = project

    return _call_api("POST", "/api/knowledge/collection/search_knowledge", body)

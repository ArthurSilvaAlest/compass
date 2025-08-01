from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from api.models.agent_manager import AgentManager

app = FastAPI(title="Compass API")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para a API
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
    tools: Optional[List[Dict[str, Any]]] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

# Instância global do AgentManager
agent_manager = AgentManager()

async def verify_api_key(authorization: str = Header(...)):
    api_key = authorization.replace("Bearer ", "")
    if api_key != "nossa-chave-secreta":  # Em produção, usar env vars e hash seguro
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Cria uma nova tarefa de completion usando o Agent Zero.
    """
    try:
        # Converte as mensagens para o formato esperado
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "name": msg.name
            } for msg in request.messages
        ]
        
        # Cria a tarefa usando o AgentManager
        result = await agent_manager.create_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature or 1.0,
            stream=request.stream or False
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/chat/status/{task_id}")
async def get_chat_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Obtém o status de uma tarefa de chat.
    """
    try:
        result = await agent_manager.get_task_status(task_id)
        
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Task not found")
            
        if result["status"] == "completed":
            # Limpa os recursos da tarefa após retornar o resultado
            agent_manager.cleanup_task(task_id)
            
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
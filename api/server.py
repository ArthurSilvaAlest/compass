from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from datetime import datetime

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

# Armazenamento de tarefas em memória
tasks: Dict[str, Any] = {}

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
    # Gerar ID único para a tarefa
    task_id = str(uuid.uuid4())
    
    # Por enquanto apenas retorna um mock
    # TODO: Integrar com Agent Zero
    return {
        "task_id": task_id,
        "status": "running",
        "created": int(datetime.now().timestamp())
    }

@app.get("/v1/chat/status/{task_id}")
async def get_chat_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Por enquanto apenas retorna um mock
    # TODO: Implementar verificação real do status
    return {
        "status": "running",
        "created": int(datetime.now().timestamp())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
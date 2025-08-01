from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import sys
import os

# Adiciona o diretório do Agent Zero ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../agent'))

from agent import AgentContext, UserMessage, AgentConfig
from initialize import initialize_agent

class AgentManager:
    """
    Gerencia a integração entre o servidor FastAPI e o Agent Zero.
    Mantém o estado dos agentes e suas tarefas.
    """
    
    def __init__(self):
        self.contexts: Dict[str, AgentContext] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        
    async def create_completion(
        self,
        messages: list,
        model: str,
        temperature: float = 1.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Cria uma nova tarefa de completion usando o Agent Zero.
        
        Args:
            messages: Lista de mensagens do chat
            model: Nome do modelo a ser usado
            temperature: Temperatura para geração (0-1)
            stream: Se deve usar streaming de resposta
            
        Returns:
            Dict contendo task_id e status inicial
        """
        # Inicializa configuração do agente
        config = initialize_agent()
        
        # Configura o modelo e temperatura
        config.chat_model.name = model
        config.chat_model.temperature = temperature
        
        # Cria novo contexto
        context = AgentContext(config=config)
        
        # Extrai a última mensagem
        last_message = messages[-1]["content"]
        
        # Cria mensagem para o agente
        user_message = UserMessage(message=last_message)
        
        # Inicia a tarefa em background
        task = asyncio.create_task(context.communicate(user_message))
        
        # Gera ID único para a tarefa
        from uuid import uuid4
        task_id = str(uuid4())
        
        # Armazena contexto e tarefa
        self.contexts[task_id] = context
        self.tasks[task_id] = {
            "task": task,
            "status": "running",
            "created": datetime.now(),
            "stream": stream
        }
        
        return {
            "task_id": task_id,
            "status": "running",
            "created": int(self.tasks[task_id]["created"].timestamp())
        }
        
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Obtém o status de uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dict contendo status e resultado (se disponível)
        """
        if task_id not in self.tasks:
            return {
                "status": "not_found",
                "error": "Task not found"
            }
            
        task_info = self.tasks[task_id]
        task = task_info["task"]
        
        if task.done():
            try:
                result = await task.result()
                return {
                    "status": "completed",
                    "result": result,
                    "created": int(task_info["created"].timestamp())
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "created": int(task_info["created"].timestamp())
                }
                
        return {
            "status": "running",
            "created": int(task_info["created"].timestamp())
        }
        
    def cleanup_task(self, task_id: str):
        """
        Limpa os recursos de uma tarefa completada.
        
        Args:
            task_id: ID da tarefa
        """
        if task_id in self.contexts:
            del self.contexts[task_id]
        if task_id in self.tasks:
            del self.tasks[task_id]
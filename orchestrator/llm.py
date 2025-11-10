"""Custom LLM implementation for LangChain."""
from typing import Any, List, Optional, Dict, Tuple
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
import requests

class GroqLLM(BaseChatModel):
    api_url: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096

    @property
    def _llm_type(self) -> str:
        return "groq"
        
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "api_url": self.api_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call Groq API asynchronously."""
        return self._generate(messages, stop, run_manager, **kwargs)
        
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call the Groq API and return the response."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Convert BaseMessage objects to API format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                role = "assistant"
            elif msg.type == "human":
                role = "user"
            elif msg.type == "system":
                role = "system"
            else:
                role = "user"  # Default to user for unknown types
                
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
        
        data = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if stop:
            data["stop"] = stop

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            completion = response.json()
            
            # Create ChatGeneration with the response
            message_content = completion["choices"][0]["message"]["content"]
            chat_generation = ChatGeneration(
                message=AIMessage(content=message_content),
                text=message_content,
                generation_info={"finish_reason": completion["choices"][0].get("finish_reason")}
            )
            
            # Create ChatResult with the generation
            chat_result = ChatResult(
                generations=[chat_generation],
                llm_output={
                    "token_usage": completion.get("usage", {}),
                    "model_name": self.model,
                }
            )
            return chat_result
        except Exception as e:
            print(f"\nError in LLM call: {str(e)}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")
            raise
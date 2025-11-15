"""
LLM API integration module for calling LLM models via Ollama or API.
"""
import random
import json
import requests
from typing import Dict, Any, Optional, List
import config


def get_available_models() -> List[str]:
    """Get list of available model identifiers."""
    return list(config.LLM_MODELS.keys())


def random_model_choice() -> str:
    """Randomly select a model from available options."""
    return random.choice(get_available_models())


def call_ollama(prompt: str, model_name: str, temperature: float = config.TEMPERATURE,
                system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Call Ollama API with the given prompt.
    
    Args:
        prompt: User prompt
        model_name: Ollama model name (e.g., "llama3.1:8b")
        temperature: Temperature setting
        system_prompt: Optional system prompt
        
    Returns:
        Dictionary with 'content' and 'metadata'
    """
    try:
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=300  # 5 minute timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "content": result.get("response", ""),
            "metadata": {
                "model": model_name,
                "tokens_used": result.get("eval_count", 0) + result.get("prompt_eval_count", 0),
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0)
            }
        }
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama API call failed: {e}")


def call_llm(prompt: str, model_name: Optional[str] = None, 
             temperature: float = config.TEMPERATURE,
             system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Call LLM API with the given prompt. Uses Ollama if available, otherwise falls back to API.
    
    Args:
        prompt: User prompt
        model_name: Model identifier, None for random
        temperature: Temperature setting (default from config)
        system_prompt: Optional system prompt
        
    Returns:
        Dictionary with 'content' (response text) and 'metadata' (token usage, etc.)
    """
    if model_name is None:
        model_name = random_model_choice()
    
    if model_name not in config.LLM_MODELS:
        raise ValueError(f"Unknown model: {model_name}. Available: {get_available_models()}")
    
    actual_model = config.LLM_MODELS[model_name]
    
    # Try Ollama first if configured
    if config.USE_OLLAMA:
        try:
            return call_ollama(prompt, actual_model, temperature, system_prompt)
        except Exception as e:
            print(f"Warning: Ollama call failed ({e}). Trying API fallback...")
            # Fall through to API call
    
    # Fallback to API call
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=config.OPENAI_API_KEY or config.HUGGINGFACE_API_KEY,
            base_url="https://api-inference.huggingface.co/v1" if config.HUGGINGFACE_API_KEY else None
        )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=actual_model,
            messages=messages,
            temperature=temperature
        )
        
        return {
            "content": response.choices[0].message.content,
            "metadata": {
                "model": model_name,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None
            }
        }
    except Exception as e:
        # Last resort: return a mock response for development/testing
        print(f"Warning: All LLM calls failed ({e}). Using mock response.")
        return {
            "content": f"[Mock LLM Response for {model_name}]\n{prompt[:100]}...",
            "metadata": {
                "model": model_name,
                "tokens_used": len(prompt.split()) * 1.3,  # Rough estimate
                "error": str(e)
            }
        }


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON response from LLM, handling cases where JSON is embedded in text.
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        Parsed JSON dictionary
    """
    # Try to extract JSON from the response
    response_text = response_text.strip()
    
    # Look for JSON code blocks
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    
    # Try to find JSON object boundaries
    if "{" in response_text and "}" in response_text:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        response_text = response_text[start:end]
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If parsing fails, return a wrapper with the raw text
        return {"raw_response": response_text, "parse_error": True}


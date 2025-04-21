from openai import OpenAI
from typing import List, Dict, Optional, Union
import click
from termcolor import colored
import os

class LLMApiCaller:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Union[str, List[str]]] = None,
        n: int = 1,
        stream: bool = False,
        logprobs: Optional[int] = None,
        seed: Optional[int] = None,
        response_format: Optional[Dict] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        top_k: Optional[int] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.n = n
        self.stream = stream
        self.logprobs = logprobs
        self.seed = seed
        self.response_format = response_format
        self.logit_bias = logit_bias
        self.top_k = top_k
        
        # Check if we're using DeepInfra or OpenAI
        if "DEEPINFRA_API_TOKEN" in os.environ:
            self.client = OpenAI(
                base_url="https://api.deepinfra.com/v1/openai",
                api_key=self.api_key
            )
            # Print debugging info in verbose mode
            if os.environ.get("VERBOSE", "0") == "1":
                click.secho(f"Using DeepInfra with model: {self.model}", fg='cyan')
        else:
            self.client = OpenAI(api_key=self.api_key)
            if os.environ.get("VERBOSE", "0") == "1":
                click.secho(f"Using OpenAI with model: {self.model}", fg='cyan')

    def _get_api_params(self, messages: List[Dict], stream: bool = False) -> Dict:
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "n": self.n,
            "stream": stream
        }

        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
        if self.stop:
            params["stop"] = self.stop
        if self.logprobs:
            params["logprobs"] = self.logprobs
        if self.seed:
            params["seed"] = self.seed
        if self.response_format:
            params["response_format"] = self.response_format
        if self.logit_bias:
            params["logit_bias"] = self.logit_bias
        if self.top_k:
            params["top_k"] = self.top_k

        return params

    def stream_response(self, messages: List[Dict]) -> None:
        try:
            stream = self.client.chat.completions.create(
                **self._get_api_params(messages, stream=True)
            )
            
            for chunk in stream:
                if chunk.choices[0].finish_reason:
                    pass
                else:
                    content = chunk.choices[0].delta.content
                    if content:
                        print(colored(content, "green"), end='', flush=True)
            
            print()
            
        except Exception as e:
            raise

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            # Print debugging info in verbose mode
            if os.environ.get("VERBOSE", "0") == "1":
                click.secho(f"Sending request to model: {self.model}", fg='cyan')
                click.secho(f"API Key (first 4 chars): {self.api_key[:4]}...", fg='cyan')
            
            response = self.client.chat.completions.create(
                **self._get_api_params(messages, stream=False)
            )
            return response.choices[0].message.content
        except Exception as e:
            click.secho(f"API Error: {str(e)}", fg='red')
            raise RuntimeError(f"API call failed: {str(e)}")

    def interactive_session(self) -> None:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        while True:
            try:
                question = click.prompt("\nType your question (or '.' to quit)")
                
                if question.lower() == '.':
                    break
                    
                messages.append({"role": "user", "content": question})
                
                self.stream_response(messages)
                
                response = self.get_response(messages)
                messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                click.secho(f"\nAn error occurred: {e}", fg='red')
                break
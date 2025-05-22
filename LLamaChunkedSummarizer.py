import os
from llama_cpp import Llama

class LLamaChunkedSummarizer:
    def __init__(self, model_path: str, n_ctx: int = 2048, max_output_tokens: int = 500, chat_format: str = "mistral-instruct"):
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            chat_format=chat_format,
            n_threads=os.cpu_count(),
            verbose=False
        )
        self.n_ctx = n_ctx
        self.max_output_tokens = max_output_tokens

    def _build_prompt(self, content: str, section_title: str, section_instruction: str) -> str:
        return f"""You are a helpful assistant writing a simple strategy report.

TASK:
Write the "{section_title}" section of the client strategy report.

Instructions:
{section_instruction}

Source Text:
{content}

---

Write your response below:
{section_title}
"""

    def summarize(self, document_text: str, section_title: str, section_instruction: str) -> str:
        full_prompt = self._build_prompt(document_text, section_title, section_instruction)
        prompt_tokens = self.model.tokenize(full_prompt.encode("utf-8"))
        max_input_tokens = self.n_ctx - self.max_output_tokens

        chunks = [
            prompt_tokens[i:i + max_input_tokens]
            for i in range(0, len(prompt_tokens), max_input_tokens)
        ]

        full_response = ""

        for i, chunk in enumerate(chunks):
            try:
                prompt_chunk = self.model.detokenize(chunk).decode("utf-8", errors="ignore")
                messages = [{"role": "user", "content": prompt_chunk}]
                response = self.model.create_chat_completion(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=self.max_output_tokens,
                )
                chunk_response = response["choices"][0]["message"]["content"]
                full_response += chunk_response.strip() + "\n"
            except Exception as e:
                print(f"[Chunk {i}] Error during inference: {e}")
                continue

        return full_response.strip()

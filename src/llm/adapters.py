"""LLM-03 — per-model adapters.

Two concrete adapters:

  - GroqLlama70B   primary; Llama 3.3 70B served via Groq free tier
  - LocalGemma2B   fallback; Gemma 2-2B-it served on Colab GPU (CPU
                   on dev hardware is slow but functional)

Each implements `_complete(prompt) -> str` only — task methods are
inherited from BaseLLMClient. Adapters propagate rate-limit / network
exceptions in their original form so `RoutingClient` (LLM-05) can
catch them by type.

Reference: compliance-gap-analysis-spec.md § LLM-03.
"""

from __future__ import annotations

import os

from src.llm.base import BaseLLMClient
from src.llm.cache import DiskCache


class GroqLlama70B(BaseLLMClient):
    """Llama 3.3 70B Versatile via the Groq free tier.

    Free-tier limits (verified 2026-05-04 against console.groq.com docs):
      RPM 30, TPM 12K, RPD 1K, TPD 100K, context 128K.
    """

    @property
    def model_family(self) -> str:
        return "llama"

    @property
    def model_id(self) -> str:
        return "llama-3.3-70b-versatile"

    @property
    def max_context(self) -> int:
        return 128_000

    def __init__(
        self,
        *,
        api_key: str | None = None,
        cache: DiskCache | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4_000,
    ) -> None:
        super().__init__(cache=cache)
        from groq import Groq
        self._client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        self._temperature = temperature
        # 4K out leaves ~8K for input under the free-tier 12K TPM ceiling;
        # synthesise step's per-obligation JSON objects need the headroom.
        self._max_tokens = max_tokens

    def _complete(self, prompt: str) -> str:
        # `groq.RateLimitError`, `groq.APIConnectionError`, and
        # `groq.APITimeoutError` propagate unchanged for RoutingClient.
        resp = self._client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return resp.choices[0].message.content or ""


class LocalGemma2B(BaseLLMClient):
    """Gemma 2-2B-it via Hugging Face Transformers.

    Targeted at Colab GPU — `device_map="auto"` picks GPU if available
    else falls back to CPU (slow but functional). Lazy-load: instantiation
    is cheap; the ~5 GB weight load only happens on first `_complete()`.
    """

    @property
    def model_family(self) -> str:
        return "gemma"

    @property
    def model_id(self) -> str:
        return "google/gemma-2-2b-it"

    @property
    def max_context(self) -> int:
        return 8_192

    def __init__(
        self,
        *,
        cache: DiskCache | None = None,
        temperature: float = 0.0,
        max_new_tokens: int = 1_500,
    ) -> None:
        super().__init__(cache=cache)
        self._tokenizer = None
        self._model = None
        self._temperature = temperature
        self._max_new_tokens = max_new_tokens

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    def _complete(self, prompt: str) -> str:
        self._ensure_loaded()
        inputs = self._tokenizer(prompt, return_tensors="pt").to(
            self._model.device
        )
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=self._max_new_tokens,
            do_sample=self._temperature > 0,
            temperature=(
                self._temperature if self._temperature > 0 else None
            ),
        )
        # Strip the input prompt; return only the generated continuation.
        gen_ids = outputs[0][inputs["input_ids"].shape[1]:]
        return self._tokenizer.decode(gen_ids, skip_special_tokens=True)

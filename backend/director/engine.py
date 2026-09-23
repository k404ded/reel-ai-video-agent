"""
engine.py
The core AI Educational Video Director Engine.
Orchestrates:
1. Content-Type Classification & Domain Rule Injection
2. Exemplar Retrieval from the Training Dataset
3. Educational Production Grammar Prompting
4. Video-Model Aware Storyboard Generation
5. Quality Control Metaphor Validation & Auto-Correction
6. Seamless Fallback Execution
"""

import os
import json
import re
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from .storyboard import EducationalStoryboard, StoryboardScene, ContentType
from .router import ContentTypeRouter
from .grammar import EDUCATIONAL_DIRECTOR_SYSTEM_PROMPT, build_director_prompt
from .validator import QualityControlValidator
from .fallback import SpecializedFallbackPlanner

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TUNED_PLANNER_MODEL = os.getenv("TUNED_PLANNER_MODEL")  # Optional fine-tuned model checkpoint

if not GEMINI_API_KEY and ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.startswith("AQ."):
    GEMINI_API_KEY = ANTHROPIC_API_KEY
    ANTHROPIC_API_KEY = None


class EducationalDirectorEngine:
    """Specialized Educational Video Director that produces validated instructional video plans."""

    def __init__(self):
        self._training_exemplars: List[Dict[str, Any]] = self._load_exemplars()
        has_gemini = bool(self._get_gemini_key())
        has_anthropic = bool(self._get_anthropic_key())
        self.using_fallback = not (has_gemini or has_anthropic)

    @staticmethod
    def _get_gemini_key() -> Optional[str]:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"])
            except Exception:
                pass
        anthropic = os.getenv("ANTHROPIC_API_KEY", "")
        if not key and anthropic.startswith("AQ."):
            key = anthropic
        return key

    @staticmethod
    def _get_anthropic_key() -> Optional[str]:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "ANTHROPIC_API_KEY" in st.secrets:
                    key = str(st.secrets["ANTHROPIC_API_KEY"])
            except Exception:
                pass
        if key and key.startswith("AQ."):
            return None
        return key

    def _load_exemplars(self) -> List[Dict[str, Any]]:
        dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "training", "educational_video_plans.jsonl")
        exemplars = []
        if os.path.exists(dataset_path):
            try:
                with open(dataset_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            exemplars.append(json.loads(line))
            except Exception as exc:
                print(f"[EducationalDirectorEngine] Could not load training exemplars: {exc}")
        return exemplars

    def _get_best_exemplar(self, content_type: str, prompt: str) -> Optional[Dict[str, Any]]:
        matches = [e for e in self._training_exemplars if e.get("content_type") == content_type]
        if matches:
            prompt_words = set(re.findall(r"\w+", prompt.lower()))
            best_match = None
            best_overlap = -1
            for m in matches:
                ex_words = set(re.findall(r"\w+", m.get("user_prompt", "").lower()))
                overlap = len(prompt_words.intersection(ex_words))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = m
            return best_match
        return None

    async def plan_educational_video(self, user_prompt: str) -> EducationalStoryboard:
        """
        Main pipeline: Classify -> Retrieve Exemplar -> Build Prompt -> LLM Execution -> Validation & Auto-Correction.
        """
        return await self._plan_pipeline(user_prompt)

    async def plan_video(self, user_prompt: str) -> EducationalStoryboard:
        """Alias for plan_educational_video for full provider backward compatibility."""
        return await self._plan_pipeline(user_prompt)

    async def _plan_pipeline(self, user_prompt: str) -> EducationalStoryboard:
        # Step 1: Ontology & Content Routing
        content_type = ContentTypeRouter.classify(user_prompt)
        rules = ContentTypeRouter.get_rules(content_type)
        exemplar = self._get_best_exemplar(content_type, user_prompt)

        # Step 2: Build Structured Prompt with Production Grammar
        director_user_prompt = build_director_prompt(
            user_prompt=user_prompt,
            content_type=content_type,
            rules=rules,
            exemplar=exemplar
        )

        raw_storyboard_data: Optional[Dict[str, Any]] = None
        gemini_key = self._get_gemini_key()
        anthropic_key = self._get_anthropic_key()

        # Step 3: Call configured model (tuned checkpoint or foundation model)
        if gemini_key:
            try:
                raw_storyboard_data = await self._plan_with_gemini(director_user_prompt, gemini_key)
                self.using_fallback = False
            except Exception as exc:
                print(f"[EducationalDirectorEngine] Gemini planning failed ({exc}); trying fallback.")

        if not raw_storyboard_data and anthropic_key:
            try:
                raw_storyboard_data = await self._plan_with_anthropic(director_user_prompt, anthropic_key)
                self.using_fallback = False
            except Exception as exc:
                print(f"[EducationalDirectorEngine] Anthropic planning failed ({exc}); trying fallback.")

        # Step 4: Local Specialized Fallback if LLM unavailable
        if not raw_storyboard_data:
            self.using_fallback = True
            storyboard = SpecializedFallbackPlanner.plan(user_prompt)
            return QualityControlValidator.validate_and_correct(storyboard)

        # Step 5: Parse into EducationalStoryboard
        storyboard = EducationalStoryboard.from_dict(raw_storyboard_data)
        storyboard.content_type = content_type

        # Step 6: Quality Control Validation & Metaphor Auto-Correction Layer
        validated_storyboard = QualityControlValidator.validate_and_correct(storyboard)
        return validated_storyboard

    async def _plan_with_gemini(self, prompt_text: str, api_key: str) -> Dict[str, Any]:
        models_to_try = []
        tuned_model = os.getenv("TUNED_PLANNER_MODEL")
        if tuned_model:
            models_to_try.append(tuned_model)
        models_to_try.extend(["gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest"])

        full_prompt = f"{EDUCATIONAL_DIRECTOR_SYSTEM_PROMPT}\n\n{prompt_text}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}

        async with httpx.AsyncClient(timeout=60) as client:
            last_err = None
            for model in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
                    return json.loads(text)
                except Exception as exc:
                    last_err = exc
                    continue
            raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")

    async def _plan_with_anthropic(self, prompt_text: str, api_key: str) -> Dict[str, Any]:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "system": EDUCATIONAL_DIRECTOR_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt_text}],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            )
            text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
            return json.loads(text)

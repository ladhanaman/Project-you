from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Optional, Tuple
import logging
import os
import json

from .prompts import (
    REFLECTION_SESSION_SYSTEM_ROLE,
    REFLECTION_SESSION_HUMAN_PROMPT
)

logger = logging.getLogger(__name__)


class ReflectionSessionGenerator:
    """
    Generate personalized 7-day reflection sessions based on PRI analysis.
    
    Logic:
    - Identifies lowest PRI score → Primary Theme (Days 1-4)
    - Identifies second-lowest → Secondary Theme (Days 5-6)
    - Day 7: Integration of all three dimensions
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.4
    ):
        """
        Initialize Reflection Session Generator with fallback support.
        
        Args:
            api_key: OpenAI API key
            gemini_api_key: Google Gemini API key
            model: Model name (default: gpt-4o-mini)
            temperature: Generation temperature (0.4 for creativity in questions)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.temperature = temperature
        
        self.llms = []
        
        # Initialize OpenAI (Primary)
        if self.api_key:
            try:
                openai_llm = ChatOpenAI(
                    api_key=self.api_key,
                    model=self.model,
                    temperature=self.temperature,
                    max_retries=1
                )
                self.llms.append(openai_llm)
                logger.info(f"Initialized OpenAI model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")

        # Initialize Gemini (Secondary/Fallback)
        if self.gemini_api_key:
            try:
                gemini_llm = ChatGoogleGenerativeAI(
                    google_api_key=self.gemini_api_key,
                    model="gemini-2.0-flash",
                    temperature=self.temperature,
                    max_retries=1
                )
                self.llms.append(gemini_llm)
                logger.info("Initialized Gemini model")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        if not self.llms:
            logger.warning("No LLMs initialized. System will use fallback templates only.")
    
    def generate_session(
        self,
        user_profile: Dict,
        pri_data: Dict,
        archetype_data: Dict,
        signals: Dict
    ) -> Dict:
        """
        Generate a 7-day reflection session.
        """
        try:
            # Determine themes based on lowest PRI scores
            primary_dim, secondary_dim, pri_sorted = self._determine_themes(pri_data)
            
            # Build the prompt
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(REFLECTION_SESSION_SYSTEM_ROLE),
                HumanMessagePromptTemplate.from_template(REFLECTION_SESSION_HUMAN_PROMPT)
            ])
            
            # Format inputs
            input_data = {
                "name": user_profile.get("name", "User"),
                "age": user_profile.get("age", "N/A"),
                "occupation": user_profile.get("occupation", "Professional"),
                "final_archetype": archetype_data["final_archetype"],
                "pri_scores_sorted": pri_sorted,
                "primary_dimension": primary_dim,
                "secondary_dimension": secondary_dim,
                "negative_tags": ", ".join(signals.get("negative_tags", [])),
                "positive_tags": ", ".join(signals.get("positive_tags", []))
            }
            
            # Create chain with JSON parser
            parser = JsonOutputParser()
            
            errors = []
            
            # Try each initialized model
            for i, llm in enumerate(self.llms):
                try:
                    logger.info(f"Attempting session generation with model {i+1}/{len(self.llms)}...")
                    chain = prompt | llm | parser
                    
                    # Invoke and parse
                    session_data = chain.invoke(input_data)
                    
                    logger.info(f"Successfully generated reflection session for {user_profile.get('name')}")
                    return session_data
                    
                except Exception as e:
                    logger.error(f"Model {i+1} failed: {str(e)}")
                    errors.append(str(e))
                    continue
            
            # If all fail
            logger.error(f"All AI models failed. Errors: {errors}")
            raise Exception("All models exhausted")
            
        except Exception as e:
            logger.error(f"Error generating reflection session chain: {str(e)}")
            # Return fallback session
            # We need to ensure themes are determined even if AI fails
            if 'primary_dim' not in locals():
                primary_dim, secondary_dim, _ = self._determine_themes(pri_data)
                
            return self._generate_fallback_session(
                user_profile,
                archetype_data,
                primary_dim,
                secondary_dim
            )
    
    def _determine_themes(self, pri_data: Dict) -> Tuple[str, str, str]:
        """
        Determine primary and secondary themes based on PRI scores.
        
        Returns:
            (primary_dimension, secondary_dimension, sorted_scores_str)
        """
        scores = [
            ("P", pri_data["purpose_score"]),
            ("R", pri_data["relevance_score"]),
            ("I", pri_data["identity_score"])
        ]
        
        # Sort by score (ascending - lowest first)
        sorted_scores = sorted(scores, key=lambda x: x[1])
        
        primary_dim = sorted_scores[0][0]  # Lowest score
        secondary_dim = sorted_scores[1][0]  # Second-lowest
        
        # Create formatted string
        sorted_str = ", ".join([f"{dim}: {score:.2f}" for dim, score in sorted_scores])
        
        return primary_dim, secondary_dim, sorted_str
    
    def _generate_fallback_session(
        self,
        user_profile: Dict,
        archetype_data: Dict,
        primary_dim: str,
        secondary_dim: str
    ) -> Dict:
        """Generate a basic fallback session when AI fails."""
        
        dimension_themes = {
            "P": "finding meaning and direction",
            "R": "building visibility and usefulness",
            "I": "aligning authenticity with action"
        }
        
        primary_theme = dimension_themes.get(primary_dim, "self-discovery")
        secondary_theme = dimension_themes.get(secondary_dim, "growth")
        
        name = user_profile.get("name", "User")
        
        return {
            "reflection_session_title": f"7-Day Journey: {primary_theme.title()}",
            "final_archetype": archetype_data["final_archetype"],
            "primary_theme": {
                "dimension": primary_dim,
                "reason": f"Your {primary_dim} score is lowest and needs attention"
            },
            "secondary_theme": {
                "dimension": secondary_dim,
                "reason": f"Your {secondary_dim} score is second-lowest"
            },
            "unlock_default_time_local": "09:00",
            "days": [
                {
                    "day": i,
                    "content_id": f"REFLECT_D{i}",
                    "title": f"Day {i}: {primary_theme if i <= 4 else secondary_theme if i <= 6 else 'Integration'}",
                    "unlock_day": i,
                    "unlock_time_local": "09:00",
                    "questions": [
                        f"What did you notice today about {primary_theme}?",
                        f"How did this show up in your work?",
                        "What one thing could you try differently?"
                    ],
                    "micro_action": f"Practice one small step toward {primary_theme}",
                    "notice_cue": f"Pay attention to moments of {primary_theme}",
                    "completion_check": "You'll feel a small shift in awareness"
                }
                for i in range(1, 8)
            ]
        }

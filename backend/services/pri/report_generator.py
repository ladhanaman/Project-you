from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Dict, Optional
import logging
import os

from .prompts import (
    PRI_REPORT_SYSTEM_ROLE,
    PRI_REPORT_HUMAN_PROMPT
)

logger = logging.getLogger(__name__)


class PRIReportGenerator:
    """
    Generate personalized "Meet Yourself" PRI reports using AI.
    
    Creates 7-section markdown reports based on:
    - User profile (name, age, occupation, etc.)
    - PRI scores and levels
    - Archetype classification
    - Positive/negative signals
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        model: str = "gpt-5.2",
        temperature: float = 0.3
    ):
        """
        Initialize PRI Report Generator with fallback support.
        
        Args:
            api_key: OpenAI API key
            gemini_api_key: Google Gemini API key
            model: Model name (default: gpt-5.2)
            temperature: Generation temperature (0.3 for balanced creativity)
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
                logger.info("Initialized Gemini model (Fallback)")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        if not self.llms:
            logger.warning("No LLMs initialized. System will use fallback templates only.")
    
    def generate_report(
        self,
        user_profile: Dict,
        pri_data: Dict,
        archetype_data: Dict,
        signals: Dict
    ) -> str:
        """
        Generate a personalized PRI "Meet Yourself" report.
        """
        # Build the prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(PRI_REPORT_SYSTEM_ROLE),
            HumanMessagePromptTemplate.from_template(PRI_REPORT_HUMAN_PROMPT)
        ])
        
        # Format inputs
        input_data = {
            "name": user_profile.get("name", "User"),
            "age": user_profile.get("age", "N/A"),
            "city": user_profile.get("city", "Unknown"),
            "occupation": user_profile.get("occupation", "Professional"),
            "education": user_profile.get("education", "N/A"),
            "industry": user_profile.get("industry", "N/A"),
            "hobbies": user_profile.get("hobbies", "N/A"),
            "purpose_score": pri_data["purpose_score"],
            "relevance_score": pri_data["relevance_score"],
            "identity_score": pri_data["identity_score"],
            "purpose_level": pri_data["purpose_level"],
            "relevance_level": pri_data["relevance_level"],
            "identity_level": pri_data["identity_level"],
            "final_archetype": archetype_data["final_archetype"],
            "display_archetype": archetype_data["display_archetype"],
            "positive_tags": ", ".join(signals.get("positive_tags", [])),
            "negative_tags": ", ".join(signals.get("negative_tags", [])),
            "notable_flags": ", ".join(signals.get("notable_flags", [])) if signals.get("notable_flags") else "None"
        }
        
        errors = []
        
        # Try each initialized LLM
        for i, llm in enumerate(self.llms):
            try:
                # Determine which provider is being used
                model_name = ""
                if hasattr(llm, 'model_name'):
                    model_name = f" ({llm.model_name})"
                elif hasattr(llm, 'model'):
                    model_name = f" ({llm.model})"
                
                provider = "OpenAI" if i == 0 and self.api_key else "Gemini"
                logger.info(f"Attempting generation with {provider}{model_name}...")
                
                # Create chain and invoke
                chain = prompt | llm
                response = chain.invoke(input_data)
                
                # Extract content
                if hasattr(response, 'content'):
                    report_md = response.content
                else:
                    report_md = str(response)
                
                logger.info(f"Successfully generated PRI report for {user_profile.get('name')} using {provider}{model_name}")
                return report_md
                
            except Exception as e:
                provider = "OpenAI" if i == 0 and self.api_key else "Gemini"
                logger.error(f"{provider} generation failed: {str(e)}")
                errors.append(str(e))
                continue
        
        # If all models fail
        logger.error(f"All AI models failed. Errors: {errors}")
        return self._generate_fallback_report(user_profile, pri_data, archetype_data)
    
    def _generate_fallback_report(
        self,
        user_profile: Dict,
        pri_data: Dict,
        archetype_data: Dict
    ) -> str:
        """Generate a basic fallback report when AI fails."""
        name = user_profile.get("name", "User")
        archetype = archetype_data.get("final_archetype", "Explorer")
        
        return f"""## 1. Your Archetype

{name}, your pattern is **{archetype}**.

## 2. Your PRI Snapshot

- Purpose: {pri_data['purpose_score']} ({pri_data['purpose_level']})
- Relevance: {pri_data['relevance_score']} ({pri_data['relevance_level']})
- Identity: {pri_data['identity_score']} ({pri_data['identity_level']})

## 3. What Your Scores Mean (Science View)

Your scores reflect your current prioritization of meaning, connection, and self.

## 4. Your Core Tension (The Main Story)

The interaction between your highest and lowest scores creates your unique drive.

## 5. Evidence From Your Signals

Your choices align with this pattern.

## 6. How You Tend to Operate

You likely lead with your strongest dimension.

## 7. What’s Going Well

Leveraging your high scores brings flow.

## 8. What’s Not Working

Neglecting your low scores creates friction.

## 9. Hidden Strength in Your Lowest Score

There is untapped potential in your underused dimension.

## 10. Shadow Risks of Your Highest Score(s)

Watch out for overusing your strengths.

## 11. Next Step Unlocked

Your 7-day reflection journey is ready."""

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
                logger.info("Initialized Gemini model (Fallback)")
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
            output_parser = JsonOutputParser()
            
            errors = []
            
            # Try each initialized LLM
            for i, llm in enumerate(self.llms):
                try:
                    # Determine which provider is being used
                    model_name_str = ""
                    if hasattr(llm, 'model_name'):
                        model_name_str = f" ({llm.model_name})"
                    elif hasattr(llm, 'model'):
                        model_name_str = f" ({llm.model})"
                    
                    provider = "OpenAI" if isinstance(llm, ChatOpenAI) else "Gemini"
                    logger.info(f"Attempting session generation with {provider}{model_name_str}...")
                    
                    # Create chain with JSON output parser
                    chain = prompt | llm | output_parser
                    session_data = chain.invoke(input_data)
                    
                    logger.info(f"Successfully generated reflection session for {user_profile.get('name')} using {provider}{model_name_str}")
                    return session_data
                    
                except Exception as e:
                    provider = "OpenAI" if isinstance(llm, ChatOpenAI) else "Gemini"
                    logger.error(f"{provider} reflection generation failed: {str(e)}")
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
        """Generate a basic fallback session with varied questions when AI fails."""
        
        # Question Banks per Dimension
        question_bank = {
            "P": [
                # Set 1 (Day 1)
                [
                    {"question": "What activity today gave you the strongest sense of 'why'?", "timing_hint": "End of day", "hint": "Look for moments you felt connected to a bigger picture."},
                    {"question": "Where did you feel your energy drain the fastest?", "timing_hint": "After work", "hint": "Low purpose often shows up as inexplicable fatigue."},
                    {"question": "If you could skip one task tomorrow, what would it be?", "timing_hint": "Before sleep", "hint": "Identify what feels meaningless to you."}
                ],
                # Set 2 (Day 2)
                [
                    {"question": "Who did you help today, and how did it feel?", "timing_hint": "After interactions", "hint": "Contribution is a key driver of Purpose."},
                    {"question": "What is one thing you did just because you 'had to'?", "timing_hint": "Mid-day check-in", "hint": "Notice where obligation replaces intention."},
                    {"question": "What would you do tomorrow if no one was watching?", "timing_hint": "Morning planning", "hint": "Imagine acting purely from your own drive."}
                ],
                # Set 3 (Day 3)
                [
                    {"question": "When did you feel most 'in flow' today?", "timing_hint": "End of day", "hint": "Flow states often indicate alignment with purpose."},
                    {"question": "What problem did you enjoy solving?", "timing_hint": "After a challenge", "hint": "Purpose often hides in the problems we like to fix."},
                    {"question": "What is one small value you honored today?", "timing_hint": "Evening reflection", "hint": "Did you choose honesty? Quality? Kindness?"}
                ],
                 # Set 4 (Day 4)
                [
                    {"question": "What are you looking forward to tomorrow?", "timing_hint": "Before sleep", "hint": "Anticipation is a sign of purpose."},
                    {"question": "What felt like a waste of time today?", "timing_hint": "After work", "hint": "Contrast this with what felt valuable."},
                    {"question": "How did your work connect to a real person today?", "timing_hint": "End of day", "hint": "Purpose is often about impact on others."}
                ]
            ],
            "R": [
                # Set 1
                [
                    {"question": "When did you feel most 'seen' or understood today?", "timing_hint": "End of day", "hint": "Relevance is about connection and visibility."},
                    {"question": "Where did you feel invisible or overlooked?", "timing_hint": "After a meeting", "hint": "Note the specific context or people involved."},
                    {"question": "Who is one person you genuinely connected with?", "timing_hint": "Lunch or break", "hint": "It doesn't have to be a deep conversation."}
                ],
                # Set 2
                [
                    {"question": "What skill did you use that felt valuable?", "timing_hint": "After a task", "hint": "Competence builds clear Relevance."},
                    {"question": "Did you ask for feedback today? If not, why?", "timing_hint": "End of work day", "hint": "Feedback loops are essential for high Relevance."},
                    {"question": "Where could you have been more visible?", "timing_hint": "Morning planning", "hint": "Is there an idea you held back?"}
                ],
                # Set 3
                [
                    {"question": "Who relied on you today?", "timing_hint": "Evening reflection", "hint": "Being needed supports your sense of place."},
                    {"question": "What community or group felt supportive?", "timing_hint": "After social time", "hint": "Or where did you feel like an outsider?"},
                    {"question": "How did you express your unique perspective?", "timing_hint": "End of day", "hint": "Relevance requires showing up as yourself."}
                ],
                 # Set 4
                [
                    {"question": "What impact did you have on your team today?", "timing_hint": "End of day", "hint": "Even small contributions count."},
                    {"question": "Did you hide any of your opinions today?", "timing_hint": "After a discussion", "hint": "Self-silencing lowers Relevance."},
                    {"question": "Who could you support or mentor tomorrow?", "timing_hint": "Before sleep", "hint": "Building others' relevance builds your own."}
                ]
            ],
            "I": [
                 # Set 1
                [
                    {"question": "When did you feel like you were 'acting' a role?", "timing_hint": "Mid-day check", "hint": "Identity gaps feel like performance."},
                    {"question": "What choice was 100% yours today?", "timing_hint": "End of day", "hint": "Autonomy helps rebuild Identity."},
                    {"question": "What physical signal (tension, relief) did you ignore?", "timing_hint": "During stress", "hint": "The body often knows your truth before you do."}
                ],
                # Set 2
                [
                    {"question": "What boundary did you set or fail to set?", "timing_hint": "After a request", "hint": "Boundaries define where you begin and end."},
                    {"question": "What did you say 'yes' to but meant 'no'?", "timing_hint": "End of day", "hint": "People-pleasing erodes Identity."},
                    {"question": "What is one thing you did just for yourself?", "timing_hint": "Evening", "hint": "Not for work, not for family - for you."}
                ],
                # Set 3
                [
                    {"question": "When did you feel most authentic today?", "timing_hint": "End of day", "hint": "When were you not filtering yourself?"},
                    {"question": "What drained you because it felt 'fake'?", "timing_hint": "After interactions", "hint": "Note who you were with."},
                    {"question": "What personal standard did you uphold?", "timing_hint": "Morning reflection", "hint": "Identity is built on self-trust."}
                ],
                 # Set 4
                [
                    {"question": "Who makes you feel most like yourself?", "timing_hint": "After social time", "hint": "Spend more time with mirrors of your true self."},
                    {"question": "What old story about yourself challenged you today?", "timing_hint": "During doubt", "hint": "Is it still true?"},
                    {"question": "What do you need to forgive yourself for?", "timing_hint": "Before sleep", "hint": "Self-compassion strengthens Identity."}
                ]
            ]
        }
        
        integration_day = [
            {"question": "Looking back, which dimension (P, R, I) improved most?", "timing_hint": "Weekly review", "hint": "Celebrate the small shift."},
            {"question": "What is one micro-change you will keep doing?", "timing_hint": "Planning next week", "hint": "Sustainability matters more than intensity."},
            {"question": "How do you see your Archetype differently now?", "timing_hint": "Final reflection", "hint": "You are not fixed; you are growing."}
        ]

        dimension_themes = {
            "P": "finding meaning",
            "R": "building connection",
            "I": "trusting yourself"
        }
        
        primary_theme_name = dimension_themes.get(primary_dim, "primary focus")
        secondary_theme_name = dimension_themes.get(secondary_dim, "secondary focus")
        
        days_content = []
        
        for i in range(1, 8):
            day_data = {"day": i, "content_id": f"REFLECT_D{i}", "unlock_day": i, "unlock_time_local": "09:00"}
            
            if i <= 4:
                # Primary Theme
                questions = question_bank.get(primary_dim, question_bank["P"])[i-1] # Use sets 0, 1, 2, 3
                day_data["title"] = f"Day {i}: Focus on {primary_theme_name}"
                day_data["questions"] = questions
                day_data["micro_action"] = f"Take one small action for {primary_theme_name}"
                day_data["notice_cue"] = f"Notice moments of {primary_theme_name}"
                day_data["completion_check"] = "You paused to reflect"
            elif i <= 6:
                # Secondary Theme
                questions = question_bank.get(secondary_dim, question_bank["R"])[i-5] # Use sets 0, 1
                day_data["title"] = f"Day {i}: Focus on {secondary_theme_name}"
                day_data["questions"] = questions
                day_data["micro_action"] = f"Take one small action for {secondary_theme_name}"
                day_data["notice_cue"] = f"Notice moments of {secondary_theme_name}"
                day_data["completion_check"] = "You tried something new"
            else:
                # Integration Day 7
                day_data["title"] = "Day 7: Integration"
                day_data["questions"] = integration_day
                day_data["micro_action"] = "Plan your next week"
                day_data["notice_cue"] = "Notice how the three dimensions connect"
                day_data["completion_check"] = "You completed the journey"
                
            days_content.append(day_data)
        
        return {
            "reflection_session_title": f"7-Day Journey: {primary_theme_name.title()}",
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
            "days": days_content
        }

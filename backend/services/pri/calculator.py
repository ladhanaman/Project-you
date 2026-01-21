from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PRICalculator:
    """
    Calculate Purpose, Relevance, Identity scores from 24-question assessment.
    
    Each question has 5 options with pre-assigned P, R, I weights.
    Formula: dimension_score = (Sum of selected weights) / 24
    """
    
    def calculate_pri_scores(
        self,
        answers: List[Dict],  # [{"question_id": 1, "selected_option": 3, "weights": {"P": 80, "R": 50, "I": 30}}, ...]
        user_age: int = None
    ) -> Dict:
        """
        Calculate PRI scores from 24 assessment answers.
        
        NOTE: Weights from database are stored as INTEGER 0-100.
        This method converts them to 0.0-1.0 scale by dividing by 100.
        
        Args:
            answers: List of answer dicts with selected weights (INTEGER 0-100)
            user_age: User's age for determining archetype prefix
        
        Returns:
            {
                "purpose_score": 0.0-1.0,
                "relevance_score": 0.0-1.0,
                "identity_score": 0.0-1.0,
                "purpose_level": "HIGH|MEDIUM|LOW",
                "relevance_level": "HIGH|MEDIUM|LOW",
                "identity_level": "HIGH|MEDIUM|LOW",
                "age_category": "explorer|builder|integrator"
            }
        """
        
        if len(answers) != 24:
            logger.warning(f"Expected 24 answers, got {len(answers)}")
        
        # Enhanced logging for transparency and auditing
        logger.info(f"====== PRI CALCULATION AUDIT ======")
        logger.info(f"Total questions received: {len(answers)}")
        
        for idx, answer in enumerate(answers, 1):
            weights = answer.get('weights', {})
            question_id = answer.get('question_id', 'unknown')
            selected_option = answer.get('selected_option', 'unknown')
            
            # Show weights in both raw (0-100) and normalized (0-1) format
            p_raw = weights.get('P', 0)
            r_raw = weights.get('R', 0)
            i_raw = weights.get('I', 0)
            
            logger.info(
                f"Q{idx} (ID:{question_id}): Option='{selected_option}' | "
                f"Normalized[P={p_raw/100:.2f}, R={r_raw/100:.2f}, I={i_raw/100:.2f}]"
            )
        
        # Convert INTEGER weights (0-100) to FLOAT (0.0-1.0) and sum
        total_p = sum(answer['weights']['P'] / 100.0 for answer in answers)
        total_r = sum(answer['weights']['R'] / 100.0 for answer in answers)
        total_i = sum(answer['weights']['I'] / 100.0 for answer in answers)
        
        logger.info(f"\n=== Aggregated Totals ===")
        logger.info(f"Total P (sum of normalized): {total_p:.4f}")
        logger.info(f"Total R (sum of normalized): {total_r:.4f}")
        logger.info(f"Total I (sum of normalized): {total_i:.4f}")
        
        # Calculate scores: (Sum of normalized weights) / 24
        num_questions = len(answers) if answers else 1  # Avoid division by zero
        p_score = total_p / num_questions
        r_score = total_r / num_questions
        i_score = total_i / num_questions
        
        # Classify each dimension
        p_level = self._classify_dimension(p_score)
        r_level = self._classify_dimension(r_score)
        i_level = self._classify_dimension(i_score)
        
        # Determine age category
        age_category = self._get_age_category(user_age) if user_age else "explorer"
        
        logger.info(
            f"PRI Calculation: P={p_score:.2f}({p_level}), "
            f"R={r_score:.2f}({r_level}), I={i_score:.2f}({i_level}), Age={age_category}"
        )
        
        return {
            "purpose_score": round(p_score, 3),
            "relevance_score": round(r_score, 3),
            "identity_score": round(i_score, 3),
            "purpose_level": p_level,
            "relevance_level": r_level,
            "identity_level": i_level,
            "age_category": age_category
        }
    
    def _classify_dimension(self, score: float) -> str:
        """
        Classify dimension score as HIGH/MEDIUM/LOW.
        
        Rules:
        - HIGH: score >= 0.7
        - MEDIUM: 0.4 <= score < 0.7
        - LOW: score < 0.4
        """
        if score >= 0.7:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_age_category(self, age: int) -> str:
        """
        Determine age-based archetype prefix.
        
        Rules:
        - Explorer: Age < 25 (early career, exploration phase)
        - Builder: 25 <= Age < 45 (building career, establishing identity)
        - Integrator: Age >= 45 (integration, wisdom phase)
        """
        if age < 25:
            return "explorer"
        elif age < 45:
            return "builder"
        else:
            return "integrator"

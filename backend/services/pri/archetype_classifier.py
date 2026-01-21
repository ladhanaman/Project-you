from typing import Dict


class ArchetypeClassifier:
    """
    Classify user into archetype based on PRI pattern.
    
    Uses the complete archetype table with age-based variants:
    - Explorer (young, early career)
    - Builder (mid-career, establishing)
    - Integrator (mature, integrating)
    """
    
    # Complete archetype mapping table (27 combinations: 3^3)
    ARCHETYPE_TABLE = {
        ("HIGH", "HIGH", "HIGH"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("HIGH", "HIGH", "MEDIUM"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("HIGH", "HIGH", "LOW"): {
            "internal_base": "Meaningful Performer",
            "display": "Role-Driven Achiever",
            "explorer": "Explorer: Role-Driven Achiever",
            "builder": "Builder: Role-Driven Achiever",
            "integrator": "Integrator: Role-Driven Achiever"
        },
        ("HIGH", "MEDIUM", "HIGH"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("HIGH", "MEDIUM", "MEDIUM"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("HIGH", "MEDIUM", "LOW"): {
            "internal_base": "Meaningful Performer",
            "display": "Role-Driven Achiever",
            "explorer": "Explorer: Role-Driven Achiever",
            "builder": "Builder: Role-Driven Achiever",
            "integrator": "Integrator: Role-Driven Achiever"
        },
        ("HIGH", "LOW", "HIGH"): {
            "internal_base": "Purposeful Hermit",
            "display": "Quiet Missionary",
            "explorer": "Explorer: Quiet Missionary",
            "builder": "Builder: Quiet Missionary",
            "integrator": "Integrator: Quiet Missionary"
        },
        ("HIGH", "LOW", "MEDIUM"): {
            "internal_base": "Purposeful Hermit",
            "display": "Quiet Missionary",
            "explorer": "Explorer: Quiet Missionary",
            "builder": "Builder: Quiet Missionary",
            "integrator": "Integrator: Quiet Missionary"
        },
        ("HIGH", "LOW", "LOW"): {
            "internal_base": "Visionary Dreamer",
            "display": "Unfinished Visionary",
            "explorer": "Explorer: Unfinished Visionary",
            "builder": "Builder: Unfinished Visionary",
            "integrator": "Integrator: Unfinished Visionary"
        },
        ("MEDIUM", "HIGH", "HIGH"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("MEDIUM", "HIGH", "MEDIUM"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("MEDIUM", "HIGH", "LOW"): {
            "internal_base": "Meaningful Performer",
            "display": "Role-Driven Achiever",
            "explorer": "Explorer: Role-Driven Achiever",
            "builder": "Builder: Role-Driven Achiever",
            "integrator": "Integrator: Role-Driven Achiever"
        },
        ("MEDIUM", "MEDIUM", "HIGH"): {
            "internal_base": "Integrated Navigator",
            "display": "Aligned Builder",
            "explorer": "Explorer: Aligned Builder",
            "builder": "Builder: Aligned Builder",
            "integrator": "Integrator: Aligned Builder"
        },
        ("MEDIUM", "MEDIUM", "MEDIUM"): {
            "internal_base": "Transitional Seeker",
            "display": "Developing Generalist",
            "explorer": "Explorer: Developing Generalist",
            "builder": "Builder: Developing Generalist",
            "integrator": "Integrator: Developing Generalist"
        },
        ("MEDIUM", "MEDIUM", "LOW"): {
            "internal_base": "Meaningful Performer",
            "display": "Role-Driven Achiever",
            "explorer": "Explorer: Role-Driven Achiever",
            "builder": "Builder: Role-Driven Achiever",
            "integrator": "Integrator: Role-Driven Achiever"
        },
        ("MEDIUM", "LOW", "HIGH"): {
            "internal_base": "Purposeful Hermit",
            "display": "Quiet Missionary",
            "explorer": "Explorer: Quiet Missionary",
            "builder": "Builder: Quiet Missionary",
            "integrator": "Integrator: Quiet Missionary"
        },
        ("MEDIUM", "LOW", "MEDIUM"): {
            "internal_base": "Purposeful Hermit",
            "display": "Quiet Missionary",
            "explorer": "Explorer: Quiet Missionary",
            "builder": "Builder: Quiet Missionary",
            "integrator": "Integrator: Quiet Missionary"
        },
        ("MEDIUM", "LOW", "LOW"): {
            "internal_base": "Lost Wanderer",
            "display": "Reset Explorer",
            "explorer": "Explorer: Reset Explorer",
            "builder": "Builder: Reset Explorer",
            "integrator": "Integrator: Reset Explorer"
        },
        ("LOW", "HIGH", "HIGH"): {
            "internal_base": "Relevant Reactor",
            "display": "High-Impact Responder",
            "explorer": "Explorer: High-Impact Responder",
            "builder": "Builder: High-Impact Responder",
            "integrator": "Integrator: High-Impact Responder"
        },
        ("LOW", "HIGH", "MEDIUM"): {
            "internal_base": "Relevant Reactor",
            "display": "High-Impact Responder",
            "explorer": "Explorer: High-Impact Responder",
            "builder": "Builder: High-Impact Responder",
            "integrator": "Integrator: High-Impact Responder"
        },
        ("LOW", "HIGH", "LOW"): {
            "internal_base": "Utility Worker",
            "display": "Dependable Operator",
            "explorer": "Explorer: Dependable Operator",
            "builder": "Builder: Dependable Operator",
            "integrator": "Integrator: Dependable Operator"
        },
        ("LOW", "MEDIUM", "HIGH"): {
            "internal_base": "Identity Anchor",
            "display": "Self-Steady Seeker",
            "explorer": "Explorer: Self-Steady Seeker",
            "builder": "Builder: Self-Steady Seeker",
            "integrator": "Integrator: Self-Steady Seeker"
        },
        ("LOW", "MEDIUM", "MEDIUM"): {
            "internal_base": "Lost Wanderer",
            "display": "Reset Explorer",
            "explorer": "Explorer: Reset Explorer",
            "builder": "Builder: Reset Explorer",
            "integrator": "Integrator: Reset Explorer"
        },
        ("LOW", "MEDIUM", "LOW"): {
            "internal_base": "Lost Wanderer",
            "display": "Reset Explorer",
            "explorer": "Explorer: Reset Explorer",
            "builder": "Builder: Reset Explorer",
            "integrator": "Integrator: Reset Explorer"
        },
        ("LOW", "LOW", "HIGH"): {
            "internal_base": "Identity Anchor",
            "display": "Self-Steady Seeker",
            "explorer": "Explorer: Self-Steady Seeker",
            "builder": "Builder: Self-Steady Seeker",
            "integrator": "Integrator: Self-Steady Seeker"
        },
        ("LOW", "LOW", "MEDIUM"): {
            "internal_base": "Lost Wanderer",
            "display": "Reset Explorer",
            "explorer": "Explorer: Reset Explorer",
            "builder": "Builder: Reset Explorer",
            "integrator": "Integrator: Reset Explorer"
        },
        ("LOW", "LOW", "LOW"): {
            "internal_base": "Lost Wanderer",
            "display": "Reset Explorer",
            "explorer": "Explorer: Reset Explorer",
            "builder": "Builder: Reset Explorer",
            "integrator": "Integrator: Reset Explorer"
        },
    }
    
    def classify(
        self,
        purpose_level: str,
        relevance_level: str,
        identity_level: str,
        age_category: str = "explorer"
    ) -> Dict[str, str]:
        """
        Classify archetype based on PRI levels and age.
        
        Args:
            purpose_level: "HIGH", "MEDIUM", or "LOW"
            relevance_level: "HIGH", "MEDIUM", or "LOW"
            identity_level: "HIGH", "MEDIUM", or "LOW"
            age_category: "explorer", "builder", or "integrator"
        
        Returns:
            {
                "internal_base_archetype": "Integrated Navigator",
                "display_archetype": "Aligned Builder",
                "final_archetype": "Explorer: Aligned Builder"
            }
        """
        
        # Look up archetype from table
        pattern = (purpose_level, relevance_level, identity_level)
        archetype_data = self.ARCHETYPE_TABLE.get(pattern)
        
        if not archetype_data:
            # Fallback for unexpected patterns
            archetype_data = {
                "internal_base": "Transitional Seeker",
                "display": "Developing Generalist",
                "explorer": "Explorer: Developing Generalist",
                "builder": "Builder: Developing Generalist",
                "integrator": "Integrator: Developing Generalist"
            }
        
        # Get age-specific variant
        final_archetype = archetype_data.get(age_category, archetype_data["explorer"])
        
        return {
            "internal_base_archetype": archetype_data["internal_base"],
            "display_archetype": archetype_data["display"],
            "final_archetype": final_archetype
        }

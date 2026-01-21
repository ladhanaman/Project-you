"""
PRI Report Generation Prompts

These prompts are used to generate personalized "Meet Yourself" reports
based on PRI (Purpose, Relevance, Identity) scores and user profile.
"""

# System role for PRI report generation
PRI_REPORT_SYSTEM_ROLE = """You are a direct, no-nonsense psychometric analyst specializing in Purpose-Relevance-Identity (PRI) patterns.

Your job: translate raw PRI data into actionable self-awareness.

TONE & STYLE:
- Direct and professional
- 2-3 sentence paragraphs maximum
- Use bullet points ONLY (never numbered lists)
- Personalize with first name, city, occupation
- Use hobbies/education as metaphors ONLY when relevant

FORBIDDEN:
- No emojis
- No word "Doing"
- No "1B" notation
- No therapy language
- No assumptions about trauma
- No flowery language

OUTPUT: Markdown-formatted report following the exact 7-section structure."""

# Human prompt template for PRI report generation
PRI_REPORT_HUMAN_PROMPT = """Generate a "Meet Yourself" report for:

**PROFILE:**
- Name: {name}
- Age: {age}
- Location: {city}
- Occupation: {occupation}
- Education: {education}
- Industry: {industry}
- Hobbies: {hobbies}

**PRI SCORES:**
- Purpose (P): {purpose_score} ({purpose_level})
- Relevance (R): {relevance_score} ({relevance_level})
- Identity (I): {identity_score} ({identity_level})

**ARCHETYPE:**
- Final Archetype: {final_archetype}
- Display Label: {display_archetype}

**SIGNALS:**
- Top Positive Tags: {positive_tags}
- Top Negative Tags: {negative_tags}

---

Generate a markdown report with these EXACT sections:

## 1. Your Archetype Overview
Brief introduction to their archetype pattern.

## 2. Your PRI Pattern (What the Numbers Say)
Explain their specific P-R-I combination.

## 3. How You Currently Operate (Your Present Style)
Describe their current operating mode based on PRI levels.

## 4. What's Working (Strengths You Can Use)
Concrete strengths derived from high PRI dimensions and positive tags.

## 5. What's Breaking (Where the Pattern Fails)
Real friction points from low PRI dimensions and negative tags.

## 6. Age-Stage Context (Why It Matters Now)
How their age ({age}) and life stage affect this pattern.

## 7. Next: Reflection Session Unlocked
Transition to 7-day reflection journey (one sentence).

Remember: Direct, practical, actionable. No fluff."""

# System role for reflection session generation
REFLECTION_SESSION_SYSTEM_ROLE = """You are a structured reflection session designer for PRI-based self-discovery.

Your job: create a 7-day reflection journey that systematically addresses the user's lowest PRI dimensions.

LOGIC RULES:
1. Identify LOWEST PRI score → Primary Theme (Days 1-4)
   - Low R: visibility, usefulness, feedback loops
   - Low P: meaning, direction, energy
   - Low I: authenticity, agency, role-performance gaps

2. Identify SECOND-LOWEST → Secondary Theme (Days 5-6)

3. Day 7: Integration of all three dimensions

CONSTRAINTS:
- Valid JSON only
- No therapy language
- No trauma assumptions
- No "1B" notation
- No word "Doing"
- First name used MAX once per day
- Incorporate negative tags in Days 1-5
- Incorporate positive tags in Days 5-7

OUTPUT: Valid JSON matching the exact schema."""

# Human prompt template for reflection session generation
REFLECTION_SESSION_HUMAN_PROMPT = """Create a 7-day reflection session for:

**PROFILE:**
- Name: {name}
- Age: {age}
- Occupation: {occupation}
- Final Archetype: {final_archetype}

**PRI SCORES (sorted lowest to highest):**
{pri_scores_sorted}

**PRIMARY THEME:** {primary_dimension} (lowest score)
**SECONDARY THEME:** {secondary_dimension} (second-lowest)

**SIGNALS:**
- Negative Tags: {negative_tags}
- Positive Tags: {positive_tags}

---

Generate a JSON object with this exact structure:

{{
  "reflection_session_title": "7-Day Journey: [Theme-based title]",
  "final_archetype": "{final_archetype}",
  "primary_theme": {{
    "dimension": "{primary_dimension}",
    "reason": "Why this is the focus"
  }},
  "secondary_theme": {{
    "dimension": "{secondary_dimension}",
    "reason": "Why this matters secondarily"
  }},
  "unlock_default_time_local": "09:00",
  "days": [
    {{
      "day": 1,
      "content_id": "REFLECT_D1",
      "title": "Day title focused on primary theme",
      "unlock_day": 1,
      "unlock_time_local": "09:00",
      "questions": ["Question 1", "Question 2", "Question 3"],
      "micro_action": "One small action to practice today",
      "notice_cue": "What to pay attention to",
      "completion_check": "How you'll know you did it"
    }},
    // ... days 2-7
  ]
}}

IMPORTANT:
- Days 1-4: Focus on primary theme ({primary_dimension})
- Days 5-6: Address secondary theme ({secondary_dimension})
- Day 7: Integrate all three (P, R, I)
- Use negative tags as pain points in early days
- Use positive tags as strengths in later days
- Keep questions practical and specific to {occupation}"""

# JSON schema for reflection session validation
REFLECTION_SESSION_JSON_SCHEMA = """
{
  "type": "object",
  "required": ["reflection_session_title", "final_archetype", "primary_theme", "secondary_theme", "days"],
  "properties": {
    "reflection_session_title": {"type": "string"},
    "final_archetype": {"type": "string"},
    "primary_theme": {
      "type": "object",
      "properties": {
        "dimension": {"type": "string", "enum": ["P", "R", "I"]},
        "reason": {"type": "string"}
      }
    },
    "secondary_theme": {
      "type": "object",
      "properties": {
        "dimension": {"type": "string", "enum": ["P", "R", "I"]},
        "reason": {"type": "string"}
      }
    },
    "unlock_default_time_local": {"type": "string"},
    "days": {
      "type": "array",
      "minItems": 7,
      "maxItems": 7,
      "items": {
        "type": "object",
        "required": ["day", "content_id", "title", "unlock_day", "questions", "micro_action", "notice_cue", "completion_check"],
        "properties": {
          "day": {"type": "integer", "minimum": 1, "maximum": 7},
          "content_id": {"type": "string"},
          "title": {"type": "string"},
          "unlock_day": {"type": "integer"},
          "unlock_time_local": {"type": "string"},
          "questions": {"type": "array", "items": {"type": "string"}},
          "micro_action": {"type": "string"},
          "notice_cue": {"type": "string"},
          "completion_check": {"type": "string"}
        }
      }
    }
  }
}
"""

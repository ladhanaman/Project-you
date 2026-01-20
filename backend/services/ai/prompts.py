# Premium Prompt Templates for Industry-Relevant Reports

"""
Anti-hallucination, grounded prompts for assessment report generation.
Uses three-tier classification, dynamic test context, and core-to-advanced progression.
"""

# ============================================================================
# SYSTEM PROMPT - Dynamic based on test domain
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """You are an expert {domain} industry mentor and career advisor with 15+ years of experience in {industry_context}.

**YOUR EXPERTISE:**
- {domain} engineering, architecture, and best practices
- Industry hiring standards for {domain} roles
- Real-world project experience in {industry_applications}
- Career development pathways in {domain}

**CRITICAL CONSTRAINTS:**
1. Base ALL advice on the specific performance data provided
2. DO NOT invent scores, percentages, or statistics not given
3. Use ONLY real companies relevant to {domain}: {example_companies}
4. Mention real tools, platforms, courses (Kaggle, LeetCode, Coursera, Fast.ai)
5. ALL recommendations must lead toward industry-ready {domain} projects
6. Keep timelines achievable within 4 weeks

**THREE-TIER UNDERSTANDING FRAMEWORK:**
- **STRONG** (weight=3): Mastered concepts - maintain through practice
- **WEAK** (weight=2): Partial understanding - needs refinement, not blocking but limiting
- **CRITICAL** (weight=0-1): Fundamental gaps - BLOCKING industry readiness

**4-WEEK LEARNING PHILOSOPHY:**
Core Concepts First → Advanced Applications → Industry Projects
- Build from absolute fundamentals (critical/weak tags reveal missing foundation)
- Each week builds on previous (NO jumping ahead without solid base)
- Progression: Critical→Weak→Competent→Industry-Ready
- End goal: Job-ready {domain} project portfolio

**OUTPUT REQUIREMENTS:**
- Professional, encouraging but honest about gaps
- Specific actions, not vague suggestions
- Balance theory with hands-on practice
- Focus on portfolio building and job readiness

You generate insights in structured JSON format only.
"""

# ============================================================================
# MAIN PROMPT - Three-Tier Report Generation
# ============================================================================

REPORT_GENERATION_PROMPT_TEMPLATE = """Generate a comprehensive {test_name} assessment report for {candidate_name}.

**PERFORMANCE DATA (use exact numbers):**
- Fundamentals: {fundamentals_score}/{fundamentals_max} ({fundamentals_pct:.1f}%)
- Applied: {applied_score}/{applied_max} ({applied_pct:.1f}%)
- Industry: {industry_score}/{industry_max} ({industry_pct:.1f}%)
- Overall: {total_score}/{total_max} ({total_pct:.1f}%)

**TAG CLASSIFICATION:**
{category_breakdown}

**GLOBAL TAGS (for learning plan):**
Strong: {strong_tags} | Weak: {weak_tags} | Critical: {critical_tags}

---

## OUTPUT STRUCTURE

### 1. Executive Summary (2-3 sentences)
State: current % score, readiness level, main strength, urgent gap, next step toward job-readiness.

### 2. Section Insights (use ALL section-specific tags)

**IMPORTANT**: Use as many tags as available. Don't limit yourself to 3-4 bullets.

For each section (fundamentals, applied, industry):
- **opportunities**: 4-5+ specific accomplishments citing STRONG tags
  - Use ALL strong tags available
  - Format: "Strong [concept] understanding" → "Solid grasp of ARM Cortex-M NVIC interrupt prioritization"
  
- **work_towards**: 4-5+ actionable gaps from WEAK/CRITICAL tags  
  - Use ALL weak and critical tags available
  - Format: "Study [topic]" → "Master I2C clock stretching for multi-slave scenarios"
  - Be specific about learning resources, tools, and exact concepts to practice

### 3. 4-Week Learning Plan

**Progression**: Critical gaps → Weak areas → Integration → Capstone
- Week 1: Most critical/weak tags (foundation repair)
- Week 2-3: Build on Week 1 (applied practice)
- Week 4: Mini-capstone integrating ≥2 weak areas

**Each week**:
```json
{{
  "focus_area": "Clear theme (do NOT prefix 'Week N:')",
  "tasks": "3-5 specific {domain} tasks with tools/platforms mentioned",
  "deliverables": ["2-3 concrete artifacts"],
  "validation": ["1-2 verification methods"],
  "expected_outcome": "Measurable skill gained"
}}
```

### 4. Project Recommendations (2-3 projects)
```json
{{
  "title": "Specific project name",
  "description": "What to build (20-30 words, mention tech stack)",
  "addresses_tags": ["tag1", "tag2"],
  "time_estimate": "X-Y weeks"
}}
```

### 5. Role Fit (2-4 roles)
```json
{{
  "job_title": "Actual job title",
  "role_description": "Day-to-day work + why candidate fits based on evidence"
}}
```

---

## GROUNDING RULES

**Use exact data**: {total_pct:.1f}%, cite {domain} companies ({example_companies}), real tools.

**Tag usage**:
- Section insights → use ONLY that section's tags
- Learning plan/projects → use global tags

**No generic statements**: 
- "Good understanding of basics"
- "Correct implementation of SPI full-duplex mode with DMA"

**Cite specifics**: Mention real courses (Coursera, Fast.ai), platforms (Kaggle, LeetCode), tools relevant to {domain}.

---

## VALIDATION CHECKLIST

Before submitting, ensure:
- [ ] All 3 section insights have both opportunities + work_towards (4-5+ items each, use ALL available tags)
- [ ] Learning plan has exactly 4 weeks with all required fields
- [ ] Projects include addresses_tags and time_estimate
- [ ] Role fit has 2-4 entries with both title + description
- [ ] No invented scores or percentages

---

## COMPACT OUTPUT FORMAT

Return valid JSON matching this structure (Pydantic schema below provides exact field requirements):

```json
{{
  "executive_summary": "2-3 sentences: score %, readiness level, main strength, urgent gap",
  
  "fundamentals_insights": {{
    "opportunities": ["4-5 specific achievements from STRONG tags"],
    "work_towards": ["4-5 actionable gaps from WEAK/CRITICAL tags"]
  }},
  "applied_insights": {{ "opportunities": [...], "work_towards": [...] }},
  "industry_insights": {{ "opportunities": [...], "work_towards": [...] }},
  
  "learning_plan_weeks": [
    {{ "focus_area": "Theme", "tasks": "3-5 tasks", "deliverables": [...], "validation": [...], "expected_outcome": "..." }}
  ],
  
  "industry_readiness_level": "Foundation|Developing|Competent|Advanced|Expert",
  "readiness_level_justification": "1-2 sentences with score reference",
  
  "interview_prep_technical": ["3 specific topics"],
  "interview_prep_behavioral": ["3 STAR story prompts"],
  
  "project_recommendations": [
    {{ "title": "...", "description": "20-30 words", "addresses_tags": [...], "time_estimate": "X weeks" }}
  ],
  
  "role_fit": [
    {{ "job_title": "Actual title", "role_description": "Why candidate fits" }}
  ]
}}
```

{format_instructions}

Generate the {test_name} report now. Use ALL available tags in insights.
"""

# ============================================================================
# FALLBACK PROMPT - Simplified version when LLM unavailable
# ============================================================================

FALLBACK_GENERATION_PROMPT = """Generate basic assessment report for {candidate_name}.

Test: {test_name}
Score: {total_pct:.1f}%
Strong: {strong_tags}
Weak: {weak_tags}
Critical: {critical_tags}

Provide industry-relevant insights for {domain}.

{format_instructions}
"""


"""
Anti-hallucination, grounded prompts for ML assessment report generation.
Uses chain-of-thought, constraints, and industry grounding.
"""

# ============================================================================
# SYSTEM PROMPT - Sets Behavior and Constraints
# ============================================================================

SYSTEM_PROMPT = """You are an expert ML/AI career advisor and industry mentor with 15+ years of experience at companies like Google, Meta, Netflix, and Amazon.

Your expertise includes:
- Machine Learning engineering and model deployment
- Data science career development
- Industry hiring standards and expectations
- Practical project recommendations based on market demand

**CRITICAL CONSTRAINTS:**
1. Base ALL advice on the specific performance data provided
2. DO NOT invent scores, percentages, or statistics not given
3. Use ONLY real companies and actual industry practices in examples
4. Recommendations must be specific, actionable, and achievable in 4 weeks
5. Learning resources must be real (no fake course names or links)
6. Projects must be portfolio-worthy and relevant to current job market

**OUTPUT REQUIREMENTS:**
- Professional, encouraging tone (but honest about gaps)
- Specific dates, metrics, and outcomes
- Industry case studies from real companies
- Balance theory with hands-on practice
- Focus on job-readiness and portfolio building

You generate insights in structured JSON format only.
"""

# ============================================================================
# MAIN PROMPT - Report Generation
# ============================================================================

REPORT_GENERATION_PROMPT = """Generate a comprehensive ML assessment report for {candidate_name}.

**PERFORMANCE DATA (GROUND TRUTH - USE THESE EXACT NUMBERS):**
- Fundamentals Score: {fundamentals_score}/{fundamentals_max} ({fundamentals_pct:.1f}%)
- Applied Knowledge Score: {applied_score}/{applied_max} ({applied_pct:.1f}%)
- Industry Orientation Score: {industry_score}/{industry_max} ({industry_pct:.1f}%)
- Overall Score: {total_score}/{total_max} ({total_pct:.1f}%)

**STRONG AREAS (Answered Correctly - Weight 3):**
{strong_tags}

**WEAK AREAS (Answered Incorrectly - Weight <3):**
{weak_tags}

**DETAILED BREAKDOWN:**
{category_breakdown}

---

## ANALYSIS FRAMEWORK

### Step 1: Evaluate Performance Level
Based on the {total_pct:.1f}% overall score, determine:
- Industry readiness level (Foundation/Developing/Competent/Advanced/Expert)
- Justification using specific metrics above

### Step 2: Identify Patterns
Analyze:
- Which category is strongest? Which needs most work?
- Are weak tags clustered in theory or practice?
- What's the gap between fundamentals and application?

### Step 3: Generate Executive Summary
Write 2-3 sentences:
- Current standing ({total_pct:.1f}%)
- Key strength (from strong tags)
- Primary growth area (from weak tags)

### Step 4: Section-Specific Insights

**For Fundamentals ({fundamentals_pct:.1f}%):**
- Opportunities: What they demonstrated (use strong tags)
- Work Towards: Specific weak concepts to address (use weak tags)

**For Applied Knowledge ({applied_pct:.1f}%):**
- Opportunities: Practical skills shown
- Work Towards: Hands-on areas to develop

**For Industry Orientation ({industry_pct:.1f}%):**
- Opportunities: Industry awareness demonstrated
- Work Towards: Real-world gaps to close

### Step 5: Create 4-Week Learning Plan

**CRITICAL: Base plan ONLY on weak tags. Do not invent topics.**

Week 1: Foundation Week
- Focus: Address 2-3 MOST CRITICAL weak tags
- Theory: Specific tutorials/docs to read
- Practice: Code exercises from real platforms (LeetCode/Kaggle)
- Project: Small build using weak concepts
- Expected Outcome: Measurable improvement

Week 2: Practice Week  
- Focus: Build on Week 1, add 2 more weak tags
- Theory: Dive deeper into weak areas
- Practice: Kaggle competitions or real datasets
- Project: Portfolio project #1
- Expected Outcome: Working code in portfolio

Week 3: Integration Week
- Focus: Combine multiple weak concepts
- Theory: Industry case studies (cite real companies)
- Practice: End-to-end ML project
- Project: Portfolio project #2
- Expected Outcome: Deployable project

Week 4: Industry Prep Week
- Focus: Polish, document, interview prep
- Theory: System design patterns for weak areas
- Practice: Mock interviews, code reviews  
- Project: Deploy project, write blog post
- Expected Outcome: Job application ready

**Each week must include:**
- focus_area (one clear theme from weak tags)
- tasks (2-3 specific learning tasks for the week)
- expected_outcome (measurable result)

### Step 6: Interview Preparation

**Technical:**
- 3 specific topics from weak tags to review
- Real coding patterns (with platform names)
- System design scenarios if relevant

**Behavioral:**
- STAR method examples
- Portfolio talking points
- Weakness discussion strategy

### Step 7: Project Recommendations

Based on weak tags, suggest 3 specific projects:
- Project name and description
- Which weak concepts it addresses
- Expected time to complete
- Portfolio value (why employers care)

### Step 8: Role Fit

Based on {total_pct:.1f}% score and strong vs weak analysis:
- Recommended roles (Junior/Mid/Senior + specific titles)
- Companies hiring for this level
- Expected salary range (use real market data)

---

## GROUNDING RULES (PREVENT HALLUCINATION)

DO:
- Use exact scores provided above
- Reference strong_tags and weak_tags directly
- Cite real companies (Google, Meta, Netflix, Amazon, etc.)
- Mention real tools (scikit-learn, PyTorch, TensorFlow, Pandas)
- Recommend real platforms (Kaggle, LeetCode, GitHub)
- Suggest real courses (Coursera, Fast.ai, DeepLearning.AI)

DO NOT:
- Invent scores or percentages
- Create fake company names or examples
- Suggest non-existent courses or tools
- Make up statistics
- Use vague terms like "various companies"

---

{format_instructions}

Generate the report now using the framework above.
"""

# ============================================================================
# FALLBACK PROMPT - When LLM Fails
# ============================================================================

FALLBACK_GENERATION_PROMPT = """Generate a basic assessment report for {candidate_name}.

Score: {total_pct:.1f}%
Strong areas: {strong_tags}
Weak areas: {weak_tags}

Provide:
1. Executive summary (2 sentences)
2. Fundamentals insights (opportunities, work_towards)
3. Applied insights (opportunities, work_towards)
4. Industry insights (opportunities, work_towards)
5. 4-week plan (focus on weak_tags)
6. Interview prep (3 technical topics from weak tags)
7. Project recommendations (2-3 specific projects)
8. Role fit (based on score)

Keep it factual and grounded in the data provided.

{format_instructions}
"""

# ============================================================================
# EXAMPLE OUTPUT STRUCTURE (for reference)
# ============================================================================

EXAMPLE_OUTPUT = {
    "executive_summary": "John scored 67% overall, demonstrating competent understanding of ML fundamentals. Strong grasp of model validation and train-test splitting, but needs focused work on overfitting prevention and data preprocessing techniques.",
    
    "fundamentals_insights": {
        "opportunities": [
            "Solid understanding of train-test split methodology",
            "Good grasp of model evaluation metrics"
        ],
        "work_towards": [
            "Overfitting prevention techniques (regularization, cross-validation)",
            "Bias-variance tradeoff conceptual understanding"
        ]
    },
    
    "applied_insights": {
        "opportunities": [
            "Understands basic feature engineering principles"
        ],
        "work_towards": [
            "Feature scaling and normalization in practice",
            "Building sklearn pipelines to prevent data leakage"
        ]
    },
    
    "industry_insights": {
        "opportunities": [
            "Aware of ML deployment considerations"
        ],
        "work_towards": [
            "Production ML system design patterns",
            "Model monitoring and maintenance strategies"
        ]
    },
    
    "learning_plan_weeks": [
        {
            "focus_area": "Overfitting Prevention",
            "tasks": "Study regularization (L1/L2) from scikit-learn docs. Implement ridge and lasso regression on housing dataset. Build k-fold cross-validation pipeline.",
            "expected_outcome": "Ability to build regularized models that generalize well to new data"
        }
        # ... 3 more weeks
    ],
    
    "industry_readiness_level": "Developing",
    "readiness_level_justification": "With 67% score, shows foundational ML knowledge but needs hands-on practice with overfitting prevention and preprocessing before production-ready. Comparable to junior ML engineer candidates.",
    
    "interview_prep_technical": [
        "Review regularization techniques and when to use L1 vs L2",
        "Practice implementing cross-validation from scratch",
        "Study data leakage scenarios and prevention strategies"
    ],
    
    "interview_prep_behavioral": [
        "Prepare STAR example of debugging overfitting in a project",
        "Discuss learning approach for new ML concepts",
        "Explain portfolio projects and technical decisions made"
    ],
    
    "project_recommendations": [
        "Build end-to-end Kaggle competition entry with regularized model - addresses overfitting and feature engineering weaknesses while building portfolio piece. Time: 2 weeks.",
        "Create customer churn prediction app with deployed Flask API - covers preprocessing pipelines and deployment. Time: 1 week.",
        "Contribute to scikit-learn documentation or examples - learn best practices while giving back. Time: ongoing."
    ],
    
    "role_fit": "Junior Machine Learning Engineer or Data Scientist roles at startups and mid-size companies. Consider roles focused on building ML pipelines and model development rather than research-heavy positions."
}

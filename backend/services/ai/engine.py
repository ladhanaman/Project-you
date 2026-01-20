# services/ai/engine.py - AI Insight Engine
"""
Main AI Insight Engine for generating personalized insights using LLMs.
"""
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from typing import Dict, List, Optional
import logging

import schemas as app_schemas
# Prompts are imported inside methods as needed
from .utils import sanitize_input, retry_with_backoff, get_performance_level

logger = logging.getLogger(__name__)


class AIInsightEngine:
    """LangChain-powered service for generating personalized insights with enhanced reliability"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        gemini_api_key: Optional[str] = None, 
        model: str = "gpt-4o-mini", 
        temperature: float = 0.2
    ):
        """
        Initialize AI Engine with OpenAI and/or Gemini client
        
        Args:
            api_key: OpenAI API key
            gemini_api_key: Google Gemini API key
            model: Model name (default: gpt-4o-mini for cost optimization)
            temperature: Sampling temperature (0.2 for more deterministic outputs)
        """
        self.llm = None
        if api_key:
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=4000,
                timeout=60
            )
            
        self.gemini_llm = None
        if gemini_api_key:
            self.gemini_llm = ChatGoogleGenerativeAI(
                google_api_key=gemini_api_key,
                model="gemini-flash-latest",
                temperature=temperature,
                max_output_tokens=8000,  # Increased from 4000 to prevent truncation
                timeout=60
            )

        if not self.llm and not self.gemini_llm:
            logger.warning("No API keys provided for AI Engine. Insights will use fallback.")
        
        # Circuit breaker state
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_open = False
        
        self.parser = PydanticOutputParser(pydantic_object=app_schemas.InsightResponse)


    def generate_insights_simplified(
        self,
        candidate_name: str,
        test_name: str,
        scores: Dict[str, int],
        fundamentals_tags: Dict[str, List[str]],  # {strong, weak, critical}
        applied_tags: Dict[str, List[str]],
        industry_tags: Dict[str, List[str]],
        all_strong_tags: List[str],
        all_weak_tags: List[str],
        all_critical_tags: List[str]
    ) -> Dict[str, any]:
        """
        Generate insights using section-specific tag classification with dynamic test context
        
        Args:
            candidate_name: Candidate's name
            test_name: Name of the test (for industry context)
            scores: {fundamentals, applied, industry, total}
            fundamentals_tags: {strong: [], weak: [], critical: []} for fundamentals section
            applied_tags: {strong: [], weak: [], critical: []} for applied section
            industry_tags: {strong: [], weak: [], critical: []} for industry section
            all_strong_tags: Global strong tags for 4-week plan
            all_weak_tags: Global weak tags for 4-week plan
            all_critical_tags: Global critical tags for 4-week plan
        
        Returns:
            Dict with executive_summary, insights, learning_plan, etc.
        """
        from .prompts import SYSTEM_PROMPT_TEMPLATE, REPORT_GENERATION_PROMPT_TEMPLATE
        from .test_config import get_industry_context
        
        # Removed verbose log - start logged below
        
        # Check circuit breaker
        if self.circuit_breaker_open:
            logger.warning("Circuit breaker is open, using fallback insights")
            return self._generate_fallback_insights(
                candidate_name, scores, all_critical_tags + all_weak_tags, (scores['total'] / 300) * 100
            )
        
        # Fail fast if no LLM configured
        if not self.llm and not self.gemini_llm:
            logger.warning("No LLM configured, using fallback")
            return self._generate_fallback_insights(
                candidate_name, scores, all_critical_tags + all_weak_tags, (scores['total'] / 300) * 100
            )
        
        try:
            # Sanitize inputs
            candidate_name = sanitize_input(candidate_name, max_length=100)
            
            # Get industry context from test name
            industry_ctx = get_industry_context(test_name)
            
            # Calculate max scores (assuming 5 questions per category)
            max_scores = {
                'fundamentals': 100,  # 5 questions * 20 points
                'applied': 100,
                'industry': 100,
                'total': 300
            }
            
            # Calculate percentages
            fundamentals_pct = (scores['fundamentals'] / max_scores['fundamentals']) * 100
            applied_pct = (scores['applied'] / max_scores['applied']) * 100
            industry_pct = (scores['industry'] / max_scores['industry']) * 100
            total_pct = (scores['total'] / max_scores['total']) * 100
            
            # Format section-specific tags for prompt
            fundamentals_tags_str = f"""
Strong: {', '.join(fundamentals_tags.get('strong', [])) or 'None'}
Weak: {', '.join(fundamentals_tags.get('weak', [])) or 'None'}
Critical: {', '.join(fundamentals_tags.get('critical', [])) or 'None'}"""
            
            applied_tags_str = f"""
Strong: {', '.join(applied_tags.get('strong', [])) or 'None'}
Weak: {', '.join(applied_tags.get('weak', [])) or 'None'}
Critical: {', '.join(applied_tags.get('critical', [])) or 'None'}"""
            
            industry_tags_str = f"""
Strong: {', '.join(industry_tags.get('strong', [])) or 'None'}
Weak: {', '.join(industry_tags.get('weak', [])) or 'None'}
Critical: {', '.join(industry_tags.get('critical', [])) or 'None'}"""
            
            # Global tags for 4-week plan
            all_strong_str = ', '.join(all_strong_tags) if all_strong_tags else 'None'
            all_weak_str = ', '.join(all_weak_tags) if all_weak_tags else 'None'
            all_critical_str = ', '.join(all_critical_tags) if all_critical_tags else 'None'
            
            # Category breakdown with section-specific tags
            category_breakdown = f"""
FUNDAMENTALS ({scores['fundamentals']}/{max_scores['fundamentals']} = {fundamentals_pct:.1f}%):
{fundamentals_tags_str}

APPLIED KNOWLEDGE ({scores['applied']}/{max_scores['applied']} = {applied_pct:.1f}%):
{applied_tags_str}

INDUSTRY ORIENTATION ({scores['industry']}/{max_scores['industry']} = {industry_pct:.1f}%):
{industry_tags_str}

ALL TAGS (for 4-week plan and projects):
- Strong: {all_strong_str}
- Weak: {all_weak_str}
- Critical: {all_critical_str}
"""
            
            # Create dynamic prompts
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(**industry_ctx)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", REPORT_GENERATION_PROMPT_TEMPLATE)
            ])
            
            formatted = prompt.format_messages(
                candidate_name=candidate_name,
                test_name=test_name,
                domain=industry_ctx['domain'],
                industry_context=industry_ctx['industry_context'],
                industry_applications=industry_ctx['industry_applications'],
                example_companies=industry_ctx['example_companies'],
                fundamentals_score=scores['fundamentals'],
                fundamentals_max=max_scores['fundamentals'],
                fundamentals_pct=fundamentals_pct,
                applied_score=scores['applied'],
                applied_max=max_scores['applied'],
                applied_pct=applied_pct,
                industry_score=scores['industry'],
                industry_max=max_scores['industry'],
                industry_pct=industry_pct,
                total_score=scores['total'],
                total_max=max_scores['total'],
                total_pct=total_pct,
                # Section-specific tags (for per-section insights)
                fundamentals_tags=fundamentals_tags_str,
                applied_tags=applied_tags_str,
                industry_tags=industry_tags_str,
                # Global tags (for 4-week plan and projects)
                strong_tags=all_strong_str,
                weak_tags=all_weak_str,
                critical_tags=all_critical_str,
                category_breakdown=category_breakdown,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Try LLMs with fallback
            logger.info(f"Generating {test_name} insights for {candidate_name}")
            response = None
            model_used = None
            tokens_used = {"input": 0, "output": 0, "total": 0}
            
            # Try OpenAI first
            if self.llm:
                try:
                    response = self.llm.invoke(formatted)
                    model_used = "OpenAI (gpt-4o-mini)"
                    
                    # Extract token usage
                    if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
                        usage = response.response_metadata['token_usage']
                        tokens_used['input'] = usage.get('prompt_tokens', 0)
                        tokens_used['output'] = usage.get('completion_tokens', 0)
                        tokens_used['total'] = usage.get('total_tokens', 0)
                        
                except Exception as e:
                    logger.warning(f"OpenAI failed: {str(e)[:100]}")
                    response = None
            
            # Try Gemini if OpenAI failed
            if not response and self.gemini_llm:
                try:
                    response = self.gemini_llm.invoke(formatted)
                    model_used = "Gemini (gemini-flash-latest)"
                    
                    # Extract token usage for Gemini
                    if hasattr(response, 'response_metadata') and 'usage_metadata' in response.response_metadata:
                        usage = response.response_metadata['usage_metadata']
                        tokens_used['input'] = usage.get('prompt_token_count', 0)
                        tokens_used['output'] = usage.get('candidates_token_count', 0)
                        tokens_used['total'] = usage.get('total_token_count', 0)
                        
                except Exception as e:
                    logger.warning(f"Gemini failed: {str(e)[:100]}")
                    response = None
            
            if not response:
                raise Exception("All AI models failed")
            
            # Parse the response
            try:
                # Extract text content (handle different response formats)
                content_text = response.content
                if isinstance(content_text, list):
                    # Gemini returns list format, extract text from first item
                    content_text = content_text[0].get('text', '') if content_text else ''
                elif isinstance(content_text, dict):
                    content_text = content_text.get('text', '')
                
                insights = self.parser.parse(content_text)
                insights_dict = insights.model_dump()
                
                # Log success with token usage
                logger.info(
                    f"SUCCESS: Report generated via {model_used} | "
                    f"Tokens: {tokens_used['input']} in + {tokens_used['output']} out = {tokens_used['total']} total"
                )
                return insights_dict
            except OutputParserException as e:
                logger.error(f"Failed to parse LLM response: {str(e)}")
                self.circuit_breaker_failures += 1
                # Re-raise to let report_tasks.py handle with pending_ai
                raise Exception(f"LLM response parsing failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}", exc_info=True)
            self.circuit_breaker_failures += 1
            
            if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                logger.error(f"Circuit breaker opened after {self.circuit_breaker_failures} failures")
            
            # Re-raise the exception to let report_tasks.py handle it with pending_ai status
            raise
        finally:
            if self.circuit_breaker_failures > 0:
                self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)



    def identify_missed_tags(
        self,
        answered_questions: List[Dict],
        correct_answers: Dict[int, str]
    ) -> List[str]:
        """
        Identify tags from incorrectly answered questions
        
        Args:
            answered_questions: List of {id, tags, selected_answer, correct_answer, question_text}
            correct_answers: Dict mapping question_id to correct answer
        
        Returns:
            List of missed tags (from wrong answers)
        """
        missed_tags = set()
        
        for q in answered_questions:
            question_id = q.get('id')
            selected = q.get('selected_answer', '').strip()
            correct = correct_answers.get(question_id, '').strip()
            
            # If answer is wrong, collect tags
            if selected != correct and selected:
                tags = q.get('tags', [])
                missed_tags.update(tags)
        
        return list(missed_tags)

    def aggregate_metrics(
        self,
        answered_questions: List[Dict],
        correct_answers: Dict[int, str],
        scores: Dict[str, int]
    ) -> Dict[str, any]:
        """
        Aggregate performance metrics by tag and category to reduce context size
        """
        # Initialize containers
        tag_performance = {}  # tag -> {total, correct}
        category_performance = {
            'Fundamentals': {'total': 0, 'correct': 0},
            'Applied Knowledge': {'total': 0, 'correct': 0},
            'Industry Orientation': {'total': 0, 'correct': 0}
        }
        
        # Process all questions
        for q in answered_questions:
            question_id = q.get('id')
            selected = q.get('selected_answer', '').strip()
            correct = correct_answers.get(question_id, '').strip()
            category = q.get('category', '')
            tags = q.get('tags', [])
            
            is_correct = selected == correct
            
            # Update Category Metrics
            if category in category_performance:
                category_performance[category]['total'] += 1
                if is_correct:
                    category_performance[category]['correct'] += 1
            
            # Update Tag Metrics
            for tag in tags:
                if tag not in tag_performance:
                    tag_performance[tag] = {'total': 0, 'correct': 0}
                tag_performance[tag]['total'] += 1
                if is_correct:
                    tag_performance[tag]['correct'] += 1

        # Calculate Percentages and Identify Strengths/Weaknesses
        tag_metrics = []
        for tag, data in tag_performance.items():
            pct = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            tag_metrics.append({
                'tag': tag,
                'pct': pct,
                'total': data['total']
            })
        
        # Sort by percentage (descending for strengths)
        sorted_tags = sorted(tag_metrics, key=lambda x: x['pct'], reverse=True)

        strong_tags = [t['tag'] for t in sorted_tags if t['pct'] >= 70][:5]
        weak_tags = [t['tag'] for t in sorted_tags if t['pct'] <= 50][-5:]
        
        # If weak_tags are empty (student is too good), take the lowest performing ones anyway
        if not weak_tags and sorted_tags:
            weak_tags = [t['tag'] for t in sorted_tags[-3:]]

        return {
            'category_performance': category_performance,
            'strong_tags': strong_tags,
            'weak_tags': weak_tags,
            'total_questions': len(answered_questions)
        }

    @retry_with_backoff(max_retries=2, initial_delay=1.0)
    def generate_insights(
        self,
        candidate_name: str,
        scores: Dict[str, int],
        answered_questions: List[Dict],
        correct_answers: Dict[int, str]
    ) -> Dict[str, str]:
        """
        Generate AI-powered insights using LangChain with enhanced context
        
        Args:
            candidate_name: Candidate's name
            scores: {fundamentals, applied, industry, total}
            answered_questions: List of {id, tags, selected_answer, correct_answer, question_text, category}
            correct_answers: Dict mapping question_id to correct answer
        
        Returns:
            Dict with strengths, work_towards, learning_plan, role_fit
        """
        # Check circuit breaker
        if self.circuit_breaker_open:
            logger.warning("Circuit breaker is open, using fallback insights")
            return self._generate_fallback_insights(
                candidate_name, scores, [], (scores['total'] / 300) * 100
            )
        
        # Fail fast if no LLM is configured
        if not self.llm and not self.gemini_llm:
            logger.warning("No LLM configured (missing API keys), using fallback immediately")
            return self._generate_fallback_insights(
                candidate_name, scores, [], (scores['total'] / 300) * 100
            )
        
        try:
            # Sanitize user input to prevent prompt injection
            candidate_name = sanitize_input(candidate_name, max_length=100)
            
            # Calculate percentages
            fundamentals_pct = (scores['fundamentals'] / 100) * 100
            applied_pct = (scores['applied'] / 100) * 100
            industry_pct = (scores['industry'] / 100) * 100
            total_pct = (scores['total'] / 300) * 100

            # Analyze performance patterns
            metrics = self.aggregate_metrics(answered_questions, correct_answers, scores)
            
            # Identify missed tags
            missed_tags = self.identify_missed_tags(answered_questions, correct_answers)
            
            # Format tags for prompt
            strong_tags_str = ", ".join(metrics['strong_tags']) if metrics['strong_tags'] else "General Aptitude"
            weak_tags_str = ", ".join(metrics['weak_tags']) if metrics['weak_tags'] else "Specific Technical Depth"
            
            # Category-specific analysis
            category_analysis = ""
            for cat, perf in metrics['category_performance'].items():
                if perf['total'] > 0:
                    cat_pct = (perf['correct'] / perf['total']) * 100
                    category_analysis += f"\n- {cat}: {perf['correct']}/{perf['total']} correct ({cat_pct:.1f}%)"

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE),
                HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
            ])
            
            # Format prompt with parser instructions
            formatted_prompt = prompt.format_messages(
                candidate_name=candidate_name,
                fundamentals_pct=fundamentals_pct,
                applied_pct=applied_pct,
                industry_pct=industry_pct,
                total_pct=total_pct,
                fundamentals_level=get_performance_level(fundamentals_pct),
                applied_level=get_performance_level(applied_pct),
                industry_level=get_performance_level(industry_pct),
                strong_tags_str=strong_tags_str,
                weak_tags_str=weak_tags_str,
                category_analysis=category_analysis,
                total_questions=metrics['total_questions'],
                format_instructions=self.parser.get_format_instructions()
            )

            # Call LLM with retry logic
            logger.info(f"Generating detailed insights for {candidate_name}")
            response = None
            
            # Try OpenAI first
            if self.llm:
                try:
                    logger.info("Attempting generation with OpenAI")
                    response = self.llm.invoke(formatted_prompt)
                except Exception as e:
                    logger.warning(f"OpenAI generation failed: {str(e)}")
                    response = None

            # Try Gemini if OpenAI failed or not configured
            if not response and self.gemini_llm:
                try:
                    logger.info("Attempting generation with Gemini")
                    response = self.gemini_llm.invoke(formatted_prompt)
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {str(e)}")
                    response = None
            
            if not response:
                raise Exception("All AI models failed to generate response")

            # Parse response using PydanticOutputParser
            try:
                insights = self.parser.parse(response.content)
                insights_dict = insights.model_dump()
                logger.info("Successfully generated and parsed detailed insights")
                return insights_dict
                
            except OutputParserException as e:
                logger.error(f"Failed to parse LLM response: {str(e)}")
                logger.error(f"Response content: {response.content[:500]}")
                self.circuit_breaker_failures += 1
                return self._generate_fallback_insights(
                    candidate_name, scores, missed_tags, total_pct
                )
            
        except Exception as e:
            logger.error(f"Error in generate_insights: {str(e)}", exc_info=True)
            self.circuit_breaker_failures += 1
            
            # Open circuit breaker if too many failures
            if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                logger.error(f"Circuit breaker opened after {self.circuit_breaker_failures} failures")
            
            return self._generate_fallback_insights(
                candidate_name, scores, missed_tags, total_pct
            )
        finally:
            # Reset circuit breaker on success
            if self.circuit_breaker_failures > 0:
                self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)

    def _generate_fallback_insights(
        self,
        candidate_name: str,
        scores: Dict[str, int],
        missed_tags: List[str],
        total_pct: float
    ) -> Dict[str, any]:
        """Generate fallback insights matching new schema when LLM fails"""
        logger.warning("Using fallback insights due to LLM error")
        
        # Sample tags for demonstration
        sample_strong = missed_tags[:2] if len(missed_tags) >= 2 else ["Core Concepts"]
        sample_weak = missed_tags[2:5] if len(missed_tags) > 2 else ["Advanced Topics"]
        
        return {
            "executive_summary": f"Assessment completed for {candidate_name}. Overall score: {total_pct:.1f}%. Automated insights generated due to AI service unavailability.",
            
            # Per-section insights (NEW FORMAT)
            "fundamentals_insights": {
                "opportunities": [
                    f"Demonstrated understanding of {sample_strong[0] if sample_strong else 'basic concepts'}"
                ],
                "work_towards": [
                    f"Review {sample_weak[0] if sample_weak else 'foundational topics'} in detail",
                    "Practice core problem-solving techniques"
                ]
            },
            "applied_insights": {
                "opportunities": ["Completed practical assessment questions"],
                "work_towards": [
                    "Build hands-on projects to strengthen applied skills",
                    "Practice coding challenges regularly"
                ]
            },
            "industry_insights": {
                "opportunities": ["Showed interest in industry-relevant topics"],
                "work_towards": [
                    "Study industry best practices and workflows",
                    "Familiarize with professional development tools"
                ]
            },
            
            # Enhanced learning plan (NEW FORMAT with deliverables/validation)
            "learning_plan_weeks": [
                {
                    "focus_area": "Core Foundations",
                    "tasks": "Review fundamental concepts. Complete tutorial exercises. Study documentation.",
                    "deliverables": ["Study notes", "Practice exercises"],
                    "validation": ["Self-assessment quiz", "Peer review"],
                    "time_budget_hours": "10-12 hours",
                    "expected_outcome": "Solid grasp of fundamentals"
                },
                {
                    "focus_area": "Applied Practice",
                    "tasks": "Build small projects. Solve coding challenges. Debug real-world scenarios.",
                    "deliverables": ["Mini project", "Code solutions"],
                    "validation": ["Project demo", "Code review"],
                    "time_budget_hours": "12-15 hours",
                    "expected_outcome": "Ability to apply concepts practically"
                },
                {
                    "focus_area": "Advanced Topics",
                    "tasks": "Explore advanced concepts. Study case studies. Research industry patterns.",
                    "deliverables": ["Case study analysis", "Research notes"],
                    "validation": ["Presentation", "Discussion"],
                    "time_budget_hours": "10-12 hours",
                    "expected_outcome": "Understanding of advanced applications"
                },
                {
                    "focus_area": "Portfolio Building",
                    "tasks": "Complete capstone project. Document work. Prepare for interviews.",
                    "deliverables": ["Portfolio project", "Documentation"],
                    "validation": ["Project deployment", "Mock interview"],
                    "time_budget_hours": "15-20 hours",
                    "expected_outcome": "Job-ready portfolio piece"
                }
            ],
            
            "industry_readiness_level": "Foundation Level",
            "readiness_level_justification": "Based on automated scoring without detailed AI analysis. Further personalized insights require AI service availability.",
            
            # Interview prep
            "interview_prep_technical": [
                "Review core concepts from the assessment",
                "Practice explaining technical decisions",
                "Prepare code samples and examples"
            ],
            "interview_prep_behavioral": [
                "Practice STAR method responses",
                "Prepare project discussion points",
                "Research company culture and values"
            ],
            
            # Structured project recommendations (NEW FORMAT)
            "project_recommendations": [
                {
                    "title": "Portfolio Project",
                    "description": "Build an end-to-end project showcasing learned concepts",
                    "addresses_tags": missed_tags[:3] if missed_tags else ["General Skills"],
                    "time_estimate": "2-3 weeks"
                },
                {
                    "title": "Open Source Contribution",
                    "description": "Contribute to a relevant open-source project to gain real-world experience",
                    "addresses_tags": ["Collaboration", "Code Quality"],
                    "time_estimate": "1-2 weeks"
                }
            ],
            
            # Structured role fit (NEW FORMAT)
            "role_fit": [
                {
                    "job_title": "Junior Developer",
                    "role_description": "Entry-level position focusing on learning and growth under senior guidance"
                },
                {
                    "job_title": "Technical Intern",
                    "role_description": "Internship role to build practical experience and industry exposure"
                }
            ]
        }

    def generate_comprehensive_report(
        self,
        candidate_name: str,
        scores: Dict[str, int],
        answered_questions: List[Dict],
        correct_answers: Dict[int, str]
    ) -> Dict[str, any]:
        """
        Master function to generate complete insights
        """
        # Identify missed tags
        missed_tags = self.identify_missed_tags(answered_questions, correct_answers)
        
        # Generate insights
        insights = self.generate_insights(
            candidate_name=candidate_name,
            scores=scores,
            answered_questions=answered_questions,
            correct_answers=correct_answers
        )
        
        # Add missed tags to response
        insights['missed_tags'] = missed_tags
        
        return insights

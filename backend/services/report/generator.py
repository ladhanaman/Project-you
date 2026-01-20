# report_generator.py
from jinja2 import Template
from datetime import datetime
from pathlib import Path
import logging
import os
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Lazy import WeasyPrint to allow server to start without system dependencies
_weasyprint_available = None
_weasyprint_error = None

def _check_weasyprint():
    """Check if WeasyPrint is available, lazy import with MacOS fix"""
    global _weasyprint_available, _weasyprint_error
    
    if _weasyprint_available is None:
        try:
            # MacOS Fix: Explicitly add Homebrew paths for WeasyPrint dependencies
            import sys
            import os
            import ctypes.util
            
            if sys.platform == 'darwin':
                # Common Homebrew paths for Apple Silicon and Intel
                search_paths = [
                    '/opt/homebrew/lib', 
                    '/usr/local/lib',
                    '/opt/homebrew/opt/glib/lib',
                    '/opt/homebrew/opt/pango/lib',
                    '/opt/homebrew/opt/gdk-pixbuf/lib',
                    '/opt/homebrew/opt/libffi/lib'
                ]
                
                # Check which libraries are actually present
                required_libs = ['pango-1.0', 'pangocairo-1.0', 'glib-2.0', 'gobject-2.0']
                missing_libs = []
                
                for lib in required_libs:
                    if not ctypes.util.find_library(lib):
                        missing_libs.append(lib)
                
                if missing_libs:
                    logger.warning(f"Missing system libraries for WeasyPrint: {', '.join(missing_libs)}")
                    logger.warning("Install with: brew install pango gdk-pixbuf libffi gobject-introspection glib")
                
                # Check for library files and try to load them explicitly if find_library fails
                try:
                    # Try to help ctypes find the library
                    current_path = os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '')
                    new_paths = [p for p in search_paths if os.path.exists(p)]
                    
                    if new_paths:
                        # Append to fallback path
                        path_str = ':'.join(new_paths)
                        if current_path:
                            os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = f"{current_path}:{path_str}"
                        else:
                            os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = path_str
                            
                        # Path updated for WeasyPrint
                except Exception as e:
                    logger.warning(f"Could not apply WeasyPrint path fix: {e}")

            from weasyprint import HTML
            _weasyprint_available = True
            _weasyprint_error = None
            # WeasyPrint loaded
            return HTML
        except (OSError, ImportError) as e:
            _weasyprint_available = False
            _weasyprint_error = str(e)
            error_msg = str(e)
            
            # Provide specific guidance based on error type
            if "pango" in error_msg.lower():
                logger.error("WeasyPrint error: Pango library not found. Install: brew install pango")
            elif "glib" in error_msg.lower():
                logger.error("WeasyPrint error: GLib library not found. Install: brew install glib")
            elif "gobject" in error_msg.lower():
                logger.error("WeasyPrint error: GObject library not found. Install: brew install gobject-introspection")
            else:
                logger.error(f"WeasyPrint not available: {error_msg}")
            
            logger.warning(
                "PDF generation will be disabled. "
                "Install all dependencies: brew install pango gdk-pixbuf libffi gobject-introspection glib"
            )
            return None
            
    if _weasyprint_available:
        from weasyprint import HTML
        return HTML
    return None

class PDFReportGenerator:
    """Generate professional PDF reports using Jinja2 and WeasyPrint"""
    
    def __init__(self, output_dir: str = "./reports"):
        """Initialize report generator with output directory"""
        self.output_dir = Path(output_dir).resolve()  # Convert to absolute path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check WeasyPrint availability once at initialization
        self.HTML = _check_weasyprint()
        self.weasyprint_available = self.HTML is not None
        
        if not self.weasyprint_available:
            logger.error(f"WeasyPrint not available at initialization: {_weasyprint_error}")
            logger.error("PDF generation will fail. Install dependencies: brew install pango gdk-pixbuf libffi gobject-introspection glib")
        else:
            pass  # WeasyPrint initialized successfully
        
        # PDF output directory set

    def get_html_template(self) -> Template:
        """Return Jinja2 HTML template for the assessment report"""
        # Load template from external file for easier updates
        template_path = Path(__file__).parent / "templates" / "thinkbinary_report.html"
        
        if template_path.exists():
            # Template loaded
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            logger.warning(f"Template file not found at {template_path}, using fallback")
            # Fallback to basic template if file doesn't exist
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            line-height: 1.5;
            color: #1f2937;
        }
        .page {
            background: white;
            margin: 0 auto;
            padding: 40px 50px;
            max-width: 900px;
        }
        
        h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #111827;
            text-align: center;
        }
        h2 {
            font-size: 20px;
            font-weight: 700;
            color: #111827;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
        }
        h3 {
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        p {
            font-size: 13px;
            margin-bottom: 12px;
            text-align: justify;
            color: #4b5563;
        }
        .subtitle {
            font-size: 16px;
            text-align: center;
            color: #6b7280;
            margin-bottom: 30px;
        }

        ul, ol {
            margin-bottom: 15px;
            padding-left: 20px;
        }
        li {
            font-size: 13px;
            margin-bottom: 6px;
            color: #4b5563;
        }

        .section-box {
            margin-bottom: 25px;
        }

        /* Candidate Details */
        .details-box {
            background-color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            margin-bottom: 30px;
        }
        .details-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .detail-item {
            font-size: 13px;
        }
        .detail-label {
            font-weight: 600;
            color: #374151;
        }
        
        /* Scores */
        .score-list li {
            font-weight: 600;
            color: #1f2937;
        }

        /* Opportunities / Work Towards */
        .opportunities-box {
            margin-bottom: 15px;
        }
        .opportunities-title {
            color: #166534; /* Green */
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .work-towards-title {
            color: #991b1b; /* Red */
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 8px;
            margin-top: 15px;
        }

        /* Week Plan */
        .week-plan-item {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f3f4f6;
        }
        .week-title {
            font-weight: 700;
            color: #1e40af;
            font-size: 14px;
            margin-bottom: 5px;
        }

        /* Footer */
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 10px;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <div class="page">
        <!-- Title Section -->
        <h1>ThinkBinary</h1>
        <div class="subtitle">Personalized Learning and Industry Readiness Report</div>

        <!-- Candidate Details -->
        <h2>Candidate Details</h2>
        <div class="details-box">
            <div class="details-grid">
                <div class="detail-item"><span class="detail-label">Full Name:</span> {{ candidate_name }}</div>
                <div class="detail-item"><span class="detail-label">Email Add:</span> {{ candidate_email }}</div>
                <div class="detail-item"><span class="detail-label">WhatsApp:</span> {{ candidate_whatsapp }}</div>
                <div class="detail-item"><span class="detail-label">Phone Nu:</span> {{ candidate_whatsapp }}</div>
                <div class="detail-item"><span class="detail-label">Education:</span> {{ candidate_education }}</div>
                <div class="detail-item"><span class="detail-label">College /:</span> {{ candidate_college }}</div>
            </div>
        </div>

        <!-- Introduction -->
        <h2>Introduction</h2>
        <p>ThinkBinary was founded to help aspiring engineers bridge the academic-industry divide. The next two years (2025-2027) will be transformative for industries like automotive, healthcare, agriculture, and manufacturing due to increasing adoption of IoT, AI, and smart electronics. India alone is expected to see over $1 billion in Industrial IoT investments with job demand in embedded systems growing at 20% annually. This personalized report analyzes your current readiness, identifies key opportunities and missed learning areas, and provides a step-by-step roadmap for growth. The ultimate goal is to help you succeed in your career with confidence and direction.</p>

        <!-- Purpose of the Test -->
        <h2>Purpose of the Test</h2>
        <p>This test is designed to:</p>
        <ul>
            <li>Help you calibrate your skills against actual industry expectations, allowing you to understand how well your academic knowledge translates into the demands of a real job.</li>
            <li>Make you aware of where you excel and what needs improvement, giving you a clear view of your strong technical areas and those that require focused attention.</li>
            <li>Serve as a roadmap for structured growth, so you can prepare for your career journey step-by-step with measurable goals.</li>
        </ul>

        <!-- About the Test -->
        <h2>About the Test</h2>
        <p>The questions were carefully curated by experienced professionals in the embedded and IoT industry, drawing from real-life scenarios and interview-level challenges. The assessment not only evaluates your technical abilities but also gives you a benchmark against industry needs—making it a starting point for targeted learning and future success. This test was formulated with direct input from professionals working in embedded systems and IoT industries. The goal was to simulate a well-rounded evaluation similar to the first screening phase of technical interviews. Questions were crafted to span not only academic fundamentals but also real-world applications and industry workflows, offering a comprehensive assessment of a candidate's readiness for practical engineering roles.</p>

        <p>Each section of the test serves a specific purpose in evaluating key competencies:</p>
        <ul>
            <li><strong>Fundamentals</strong>: This section evaluates the depth of your understanding of core electronics concepts such as digital logic, number systems, microcontroller architecture, and basic circuit operations. These are non-negotiable foundations that every embedded and IoT engineer must master to build reliable systems.</li>
            <li><strong>Applied Knowledge</strong>: In this section, your ability to translate theory into functional code is tested. It covers embedded C programming, sensor interfacing, peripheral communication (UART, SPI, I2C), and logic debugging. Success in this section shows that you're capable of designing and developing embedded products that work in real-life scenarios.</li>
            <li><strong>Industry Orientation</strong>: This part tests your understanding of the practical ecosystem around embedded development. It includes version control tools, project workflows, documentation standards, and collaboration practices. These skills help you function effectively in professional teams and deliver high-quality, maintainable projects.</li>
        </ul>

        <!-- Test Results -->
        <h2>Test Results Overview</h2>
        <ul class="score-list">
            <li>Fundamentals Score: {{ fundamentals_score }}/100</li>
            <li>Applied Knowledge Score: {{ applied_score }}/100</li>
            <li>Industry Orientation Score: {{ industry_score }}/100</li>
            <li>Total Score: {{ total_score }}/300</li>
        </ul>

        <!-- Section 1: Fundamentals -->
        <h2>Section 1: Fundamentals</h2>

        <div class="opportunities-title">Opportunities:</div>
        <ul>
            {% for item in fundamentals_insights.opportunities %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <div class="work-towards-title">Work Towards Winning More Opportunities:</div>
        <ul>
            {% for item in fundamentals_insights.work_towards %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <!-- Section 2: Applied Knowledge -->
        <h2>Section 2: Applied Knowledge</h2>

        <div class="opportunities-title">Opportunities:</div>
        <ul>
            {% for item in applied_insights.opportunities %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <div class="work-towards-title">Work Towards Winning More Opportunities:</div>
        <ul>
            {% for item in applied_insights.work_towards %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <!-- Section 3: Industry Orientation -->
        <h2>Section 3: Industry Orientation</h2>

        <div class="opportunities-title">Opportunities:</div>
        <ul>
            {% for item in industry_insights.opportunities %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <div class="work-towards-title">Work Towards Winning More Opportunities:</div>
        <ul>
            {% for item in industry_insights.work_towards %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>

        <!-- 4-Week Plan -->
        <h2>Personalized 4-Week Learning Plan</h2>
        {% for week in learning_plan_weeks %}
        <div class="week-plan-item">
            <div class="week-title">Week {{ loop.index }}: {{ week.focus_area }}</div>
            <p><strong>Task:</strong> {{ week.tasks }}</p>
            <p><strong>Goal:</strong> {{ week.expected_outcome }}</p>
        </div>
        {% endfor %}

        <!-- Project Recommendations -->
        <h2>Project Recommendations</h2>
        <ol>
            {% for item in project_recommendations %}
            <li>{{ item }}</li>
            {% endfor %}
        </ol>

        <!-- Suggested Role Fit -->
        <h2>Suggested Role Fit</h2>
        <ul>
            <li>{{ role_fit }}</li>
        </ul>

        <!-- Mentorship Section -->
        <h2>ThinkBinary Mentorship & Career Scaling Program</h2>
        <p>At ThinkBinary, we believe that technical skills are just one part of building a successful career. Our Mentorship & Career Scaling Program is designed to bridge the final gap between knowledge and impactful employment. Through one-on-one guidance, structured project cycles, and access to real-world product design processes, our program ensures you are not only skilled but also industry-ready.</p>

        <p><strong>Program Offerings:</strong></p>
        <ul>
            <li>Dedicated Mentorship: Pair with industry experts for feedback and growth paths.</li>
            <li>Hands-On Projects: Work on capstone-level projects reflecting real industry cases.</li>
            <li>Weekly Knowledge Sessions: Expert talks, Q&A, and case reviews.</li>
            <li>Career Enablement Track: Resume building, LinkedIn/GitHub support, and mock interviews.</li>
            <li>Tech and Workflow Tools: Exposure to Jira, GitHub, Asana, Trello, and CI/CD.</li>
            <li>Community and Alumni Network: Collaborate on projects and research beyond the classroom.</li>
        </ul>

        <div class="footer">
            Generated by ThinkBinary Assessment Engine | Professional Career Guidance Report
        </div>
    </div>
</body>
</html>
        """
        return Template(html_content)

    def generate_report(
        self,
        submission_id: int,
        candidate_name: str,
        candidate_email: str,
        candidate_college: str = "N/A",
        candidate_course: str = "N/A",
        candidate_year: str = "N/A",
        candidate_phone: str = "N/A",
        candidate_specialization: str = None,
        candidate_linkedin: str = None,
        scores: Dict[str, int] = None,
        insights: Dict[str, any] = None
    ) -> str:
        """
        Generate PDF report and save to file
        """
        try:
            # Get template
            template = self.get_html_template()
            
            # Prepare context with safe defaults for new structure
            fundamentals_insights = insights.get('fundamentals_insights', {})
            if isinstance(fundamentals_insights, dict):
                 pass # it's already a dict
            else:
                 # Should not happen if pydantic model is dumped correctly, but safe fallback
                 fundamentals_insights = {'opportunities': [], 'work_towards': []}

            applied_insights = insights.get('applied_insights', {})
            industry_insights = insights.get('industry_insights', {})

            context = {
                'submission_id': submission_id,
                'generated_date': datetime.now().strftime('%B %d, %Y'),
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'candidate_college': candidate_college,
                'candidate_course': candidate_course,
                'candidate_year': candidate_year,
                'candidate_phone': candidate_phone,
                'candidate_specialization': candidate_specialization or 'N/A',
                'candidate_linkedin': candidate_linkedin or 'N/A',
                'fundamentals_score': scores.get('fundamentals', 0) if scores else 0,
                'applied_score': scores.get('applied', 0) if scores else 0,
                'industry_score': scores.get('industry', 0) if scores else 0,
                'total_score': scores.get('total', 0) if scores else 0,

                # New structured insights
                'fundamentals_insights': fundamentals_insights,
                'applied_insights': applied_insights,
                'industry_insights': industry_insights,

                'executive_summary': insights.get('executive_summary', 'Summary not available.'),
                'learning_plan_weeks': insights.get('learning_plan_weeks', []),
                'industry_readiness_level': insights.get('industry_readiness_level', 'Foundation Level'),
                'readiness_level_justification': insights.get('readiness_level_justification', ''),
                'project_recommendations': insights.get('project_recommendations', []),
                'role_fit': insights.get('role_fit', 'Junior Engineer')
            }
            
            # Render HTML
            html_content = template.render(**context)
            
            # Debug: Log first 500 chars of rendered HTML
            # HTML rendered (preview suppressed)
            
            # Generate PDF filename and path
            pdf_filename = f"assessment_{submission_id}_{candidate_email.split('@')[0]}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Check if WeasyPrint is available
            if not self.weasyprint_available or not self.HTML:
                error_msg = f"WeasyPrint not available: {_weasyprint_error}"
                logger.error(f"[Submission {submission_id}] {error_msg}")
                raise RuntimeError(error_msg)
            
            # Generate PDF
            # Rendering to PDF
            html_obj = self.HTML(string=html_content)
            html_obj.write_pdf(str(pdf_path))
            
            logger.info(f"PDF generated: {os.path.basename(pdf_path)}")
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

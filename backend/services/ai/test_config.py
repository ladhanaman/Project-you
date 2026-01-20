# services/ai/test_config.py - Test to Industry Domain Mapping
"""
Maps test names to industry contexts for dynamic prompt generation
"""
from typing import Dict

# Map test names to industry domains and contexts
TEST_INDUSTRY_MAP = {
    "IOT Readiness Assessment": {
        "domain": "IoT/Embedded Systems",
        "industry_context": "smart devices, industrial IoT, and connected systems",
        "industry_applications": "smart homes, industrial automation, healthcare monitoring, automotive IoT",
        "example_companies": "Bosch, Siemens, ARM, Texas Instruments, Qualcomm"
    },
    "Computer Science Fundamentals": {
        "domain": "Software Engineering/ML",
        "industry_context": "software development, data science, and ML engineering",
        "industry_applications": "web applications, ML models, data pipelines, cloud systems",
        "example_companies": "Google, Meta, Netflix, Amazon, Microsoft"
    },
    # Add more tests as needed
}


def get_industry_context(test_name: str) -> Dict[str, str]:
    """
    Get industry context for a given test name
    
    Args:
        test_name: Name of the test
    
    Returns:
        Dict with domain, industry_context, industry_applications, example_companies
    """
    return TEST_INDUSTRY_MAP.get(
        test_name,
        {
            "domain": "Technology",
            "industry_context": "software and technology",
            "industry_applications": "software projects",
            "example_companies": "tech companies"
        }
    )

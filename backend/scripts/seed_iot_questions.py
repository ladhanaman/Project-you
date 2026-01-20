#!/usr/bin/env python3
"""
Seed IoT questions with proper weights for all three categories
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models import Question, TestMetadata, CategoryEnum

def seed_iot_questions():
    """Seed balanced IoT questions"""
    db = SessionLocal()
    
    try:
        # Get IOT test
        test = db.query(TestMetadata).filter(
            TestMetadata.title == "IOT Readiness Assessment"
        ).first()
        
        if not test:
            print("❌ Test 'IOT Readiness Assessment' not found!")
            return
        
        print(f"📝 Seeding questions for: {test.title}")
        
        # ===================================================================
        # FUNDAMENTALS QUESTIONS (5 questions)
        # ===================================================================
        fundamentals_questions = [
            {
                "question_text": "What does IoT stand for?",
                "option_1": "Internet of Things",
                "option_2": "Integration of Technology",
                "option_3": "Internal Online Transmission",
                "option_4": "Interactive Object Technology",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 0,
                "weight_4": 1,
                "tags": ["iot_basics", "terminology", "fundamentals"]
            },
            {
                "question_text": "What is a sensor in IoT?",
                "option_1": "A device that collects data from environment",
                "option_2": "A display unit",
                "option_3": "A power supply",
                "option_4": "A network router",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 1,
                "weight_4": 0,
                "tags": ["sensors", "data_collection", "iot_fundamentals"]
            },
            {
                "question_text": "What protocol is commonly used for IoT communication?",
                "option_1": "HTTP only",
                "option_2": "MQTT",
                "option_3": "FTP",
                "option_4": "SMTP",
                "weight_1": 2,  # Partial - can be used
                "weight_2": 3,  # Correct - lightweight
                "weight_3": 0,
                "weight_4": 0,
                "tags": ["mqtt", "protocols", "communication"]
            },
            {
                "question_text": "What is an actuator in IoT?",
                "option_1": "Device that performs physical action",
                "option_2": "A type of sensor",
                "option_3": "A data storage unit",
                "option_4": "A network protocol",
                "weight_1": 3,  # Correct
                "weight_2": 1,  # Related but not same
                "weight_3": 0,
                "weight_4": 0,
                "tags": ["actuators", "iot_components", "control_systems"]
            },
            {
                "question_text": "What is edge computing in IoT?",
                "option_1": "Computing only in cloud",
                "option_2": "Processing data near the source instead of cloud",
                "option_3": "Connecting devices to internet",
                "option_4": "Using only wireless connections",
                "weight_1": 0,  # Opposite
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Too vague
                "weight_4": 0,
                "tags": ["edge_computing", "data_processing", "distributed_systems"]
            }
        ]
        
        # ===================================================================
        # APPLIED KNOWLEDGE QUESTIONS (5 questions)
        # ===================================================================
        applied_questions = [
            {
                "question_text": "How do you handle sensor data outliers?",
                "option_1": "Ignore all unusual values",
                "option_2": "Apply filtering and validation techniques",
                "option_3": "Always accept raw data",
                "option_4": "Delete the sensor",
                "weight_1": 1,  # Risky approach
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Wrong
                "weight_4": 0,  # Wrong
                "tags": ["data_cleaning", "sensor_data", "data_quality"]
            },
            {
                "question_text": "What is the purpose of a gateway in IoT?",
                "option_1": "To connect sensors to internet/cloud",
                "option_2": "To power devices",
                "option_3": "To display data only",
                "option_4": "To store data permanently",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 1,  # Partial function
                "weight_4": 2,  # Can do this but not main purpose
                "tags": ["gateway", "connectivity", "iot_architecture"]
            },
            {
                "question_text": "Why is security important in IoT?",
                "option_1": "Devices can be hacked and misused",
                "option_2": "It makes devices faster",
                "option_3": "It reduces cost",
                "option_4": "It's not important",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 0,
                "weight_4": 0,  # Dangerous thinking
                "tags": ["iot_security", "cybersecurity", "device_protection"]
            },
            {
                "question_text": "What is time-series data in IoT?",
                "option_1": "Data collected at specific time intervals",
                "option_2": "Historical device information",
                "option_3": "Current time on device",
                "option_4": "Data without timestamps",
                "weight_1": 3,  # Correct
                "weight_2": 2,  # Related concept
                "weight_3": 0,
                "weight_4": 0,  # Opposite
                "tags": ["time_series", "sensor_data", "data_types"]
            },
            {
                "question_text": "How do you optimize IoT device battery life?",
                "option_1": "Keep device always on",
                "option_2": "Use sleep modes and efficient protocols",
                "option_3": "Increase transmission frequency",
                "option_4": "Use only WiFi",
                "weight_1": 0,  # Opposite
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Opposite
                "weight_4": 1,  # Inefficient
                "tags": ["power_optimization", "battery_life", "device_efficiency"]
            }
        ]
        
        # ===================================================================
        # INDUSTRY ORIENTATION QUESTIONS (5 questions)
        # ===================================================================
        industry_questions = [
            {
                "question_text": "What is a common IoT use case in smart homes?",
                "option_1": "Automated lighting and temperature control",
                "option_2": "Manual switches only",
                "option_3": "Desktop computers",
                "option_4": "Paper-based systems",
                "weight_1": 3,  # Correct
                "weight_2": 0,  # Opposite
                "weight_3": 0,
                "weight_4": 0,
                "tags": ["smart_home", "automation", "iot_applications"]
            },
            {
                "question_text": "How is IoT used in industrial automation?",
                "option_1": "Monitoring and controlling manufacturing processes",
                "option_2": "Only for office work",
                "option_3": "Replacing all workers",
                "option_4": "Just for data storage",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 1,  # Misconception
                "weight_4": 2,  # Partial aspect
                "tags": ["industrial_iot", "manufacturing", "automation"]
            },
            {
                "question_text": "What is predictive maintenance in IoT?",
                "option_1": "Fixing devices only when broken",
                "option_2": "Using sensor data to predict failures before they occur",
                "option_3": "Regular manual inspection",
                "option_4": "Replacing all devices yearly",
                "weight_1": 0,  # Reactive, not predictive
                "weight_2": 3,  # Correct
                "weight_3": 2,  # Preventive but not predictive
                "weight_4": 1,  # Wasteful
                "tags": ["predictive_maintenance", "industrial_iot", "ml_applications"]
            },
            {
                "question_text": "What role does cloud play in IoT systems?",
                "option_1": "Data storage, processing, and analytics at scale",
                "option_2": "Only for backup",
                "option_3": "Not used in IoT",
                "option_4": "Just for device pairing",
                "weight_1": 3,  # Correct
                "weight_2": 1,  # Partial role
                "weight_3": 0,  # Wrong
                "weight_4": 0,
                "tags": ["cloud_computing", "iot_infrastructure", "data_analytics"]
            },
            {
                "question_text": "What is Digital Twin in IoT?",
                "option_1": "Virtual replica of physical device for simulation",
                "option_2": "Two identical devices",
                "option_3": "Backup device",
                "option_4": "Clone of software code",
                "weight_1": 3,  # Correct
                "weight_2": 0,
                "weight_3": 1,  # Misunderstanding
                "weight_4": 1,  # Different concept
                "tags": ["digital_twin", "simulation", "advanced_iot"]
            }
        ]
        
        # Add all questions
        question_count = 0
        
        for q_data in fundamentals_questions:
            q = Question(test_id=test.id, category=CategoryEnum.FUNDAMENTALS, **q_data)
            db.add(q)
            question_count += 1
        
        for q_data in applied_questions:
            q = Question(test_id=test.id, category=CategoryEnum.APPLIED, **q_data)
            db.add(q)
            question_count += 1
        
        for q_data in industry_questions:
            q = Question(test_id=test.id, category=CategoryEnum.INDUSTRY, **q_data)
            db.add(q)
            question_count += 1
        
        db.commit()
        
        print(f"\n✅ Successfully seeded {question_count} IoT questions!")
        print(f"   - Fundamentals: {len(fundamentals_questions)}")
        print(f"   - Applied: {len(applied_questions)}")
        print(f"   - Industry: {len(industry_questions)}")
        
        # Invalidate cache
        try:
            import redis
            r = redis.Redis()
            r.delete('tests:1:questions')
            print(f"   ✓ Cache invalidated")
        except Exception as e:
            print(f"   ⚠ Could not invalidate cache: {e}")
        
    except Exception as e:
        print(f"\n❌ Error seeding questions: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_iot_questions()

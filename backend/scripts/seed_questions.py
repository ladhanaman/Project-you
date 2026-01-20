#!/usr/bin/env python3
"""
Seed balanced ML questions with proper weights for all three categories
Weight 3 = Correct answer
Weight 2 = Partial understanding  
Weight 0-1 = Incorrect/misleading
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models import Question, TestMetadata, CategoryEnum

def seed_ml_questions():
    """Seed balanced ML fundamentals questions"""
    db = SessionLocal()
    
    try:
        # Get CS Fundamentals test
        test = db.query(TestMetadata).filter(
            TestMetadata.title == "Computer Science Fundamentals"
        ).first()
        
        if not test:
            print("❌ Test 'Computer Science Fundamentals' not found!")
            return
        
        print(f"📝 Seeding questions for: {test.title}")
        
        # ===================================================================
        # FUNDAMENTALS QUESTIONS (5 questions)
        # ===================================================================
        fundamentals_questions = [
            {
                "question_text": "What is the primary goal of Machine Learning?",
                "option_1": "Perfectly memorize training data",
                "option_2": "Learn patterns from data to make predictions",
                "option_3": "Replace human decision-making",
                "option_4": "Minimize computational resources",
                "weight_1": 1,  # Incorrect - overfitting
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Incorrect - too broad
                "weight_4": 2,  # Partial - optimization aspect
                "tags": ["ml_basics", "learning_objective", "generalization"]
            },
            {
                "question_text": "What does 'overfitting' mean in machine learning?",
                "option_1": "Model performs well on training but poorly on new data",
                "option_2": "Model is too simple to capture patterns",
                "option_3": "Training takes too long",
                "option_4": "Model uses too much memory",
                "weight_1": 3,  # Correct
                "weight_2": 0,  # Opposite (underfitting)
                "weight_3": 1,  # Irrelevant
                "weight_4": 1,  # Irrelevant
                "tags": ["overfitting", "model_evaluation", "bias_variance"]
            },
            {
                "question_text": "What is the bias-variance tradeoff?",
                "option_1": "Balance between model simplicity and complexity",
                "option_2": "Choice between different algorithms",
                "option_3": "Tradeoff between speed and accuracy",
                "option_4": "Balance between training and testing data",
                "weight_1": 3,  # Correct
                "weight_2": 1,  # Too vague
                "weight_3": 2,  # Partial - related concept
                "weight_4": 0,  # Incorrect
                "tags": ["bias_variance", "model_complexity", "ml_fundamentals"]
            },
            {
                "question_text": "Why do we split data into training and testing sets?",
                "option_1": "To save computational resources",
                "option_2": "To evaluate model performance on unseen data",
                "option_3": "To make training faster",
                "option_4": "To increase model accuracy",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Incorrect
                "weight_4": 2,  # Partial - outcome, not reason
                "tags": ["train_test_split", "model_evaluation", "validation"]
            },
            {
                "question_text": "What is cross-validation used for?",
                "option_1": "To clean data",
                "option_2": "To get more reliable performance estimates",
                "option_3": "To increase training data size",
                "option_4": "To reduce overfitting",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Incorrect
                "weight_4": 2,  # Partial benefit, not primary purpose
                "tags": ["cross_validation", "model_evaluation", "validation_strategy"]
            }
        ]
        
        # ===================================================================
        # APPLIED KNOWLEDGE QUESTIONS (5 questions)
        # ===================================================================
        applied_questions = [
            {
                "question_text": "What is data leakage in machine learning?",
                "option_1": "Using test data during training",
                "option_2": "Missing values in dataset",
                "option_3": "Data being too large",
                "option_4": "Incorrect data labels",
                "weight_1": 3,  # Correct
                "weight_2": 0,  # Different issue
                "weight_3": 0,  # Irrelevant
                "weight_4": 1,  # Different issue
                "tags": ["data_leakage", "preprocessing", "data_integrity"]
            },
            {
                "question_text": "Why is feature scaling important?",
                "option_1": "To make algorithms run faster",
                "option_2": "To prevent features with larger magnitudes from dominating",
                "option_3": "To remove missing values",
                "option_4": "To increase accuracy",
                "weight_1": 2,  # Partial benefit
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Incorrect
                "weight_4": 1,  # Outcome, not reason
                "tags": ["feature_scaling", "preprocessing", "normalization"]
            },
            {
                "question_text": "What is regularization in machine learning?",
                "option_1": "Making training faster",
                "option_2": "Technique to prevent overfitting by adding penalty to model complexity",
                "option_3": "Cleaning the dataset",
                "option_4": "Increasing model size",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Incorrect
                "weight_4": 0,  # Opposite
                "tags": ["regularization", "overfitting_prevention", "model_tuning"]
            },
            {
                "question_text": "When should you use k-fold cross-validation?",
                "option_1": "When you have limited data",
                "option_2": "Only for large datasets",
                "option_3": "Never, it's outdated",
                "option_4": "Only for neural networks",
                "weight_1": 3,  # Correct
                "weight_2": 1,  # Can use but not required
                "weight_3": 0,  # Incorrect
                "weight_4": 0,  # Incorrect
                "tags": ["cross_validation", "small_data", "validation_strategy"]
            },
            {
                "question_text": "What does GridSearchCV do?",
                "option_1": "Cleans the dataset",
                "option_2": "Finds best hyperparameters by testing combinations",
                "option_3": "Visualizes data",
                "option_4": "Scales features",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Incorrect
                "weight_4": 1,  # Incorrect
                "tags": ["hyperparameter_tuning", "grid_search", "model_optimization"]
            }
        ]
        
        # ===================================================================
        # INDUSTRY ORIENTATION QUESTIONS (5 questions)
        # ===================================================================
        industry_questions = [
            {
                "question_text": "What is the main challenge of deploying ML models to production?",
                "option_1": "Model drift and data distribution changes",
                "option_2": "Writing the initial code",
                "option_3": "Choosing the algorithm",
                "option_4": "Collecting training data",
                "weight_1": 3,  # Correct
                "weight_2": 1,  # Part of process
                "weight_3": 2,  # Important but not main challenge
                "weight_4": 2,  # Important but not deployment issue
                "tags": ["model_deployment", "production_ml", "model_drift"]
            },
            {
                "question_text": "Why is model monitoring important in production?",
                "option_1": "To retrain models periodically",
                "option_2": "To detect performance degradation and data drift",
                "option_3": "To save costs",
                "option_4": "To improve training speed",
                "weight_1": 2,  # Outcome, not main reason
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Secondary benefit
                "weight_4": 0,  # Irrelevant
                "tags": ["model_monitoring", "production_ml", "ml_ops"]
            },
            {
                "question_text": "What is A/B testing in ML product development?",
                "option_1": "Testing two different algorithms",
                "option_2": "Comparing model performance against baseline with real users",
                "option_3": "Testing code for bugs",
                "option_4": "Validating training data",
                "weight_1": 2,  # Partial - can be part of it
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Different concept
                "weight_4": 1,  # Different concept
                "tags": ["ab_testing", "model_evaluation", "production_ml"]
            },
            {
                "question_text": "What is MLOps?",
                "option_1": "A cloud service",
                "option_2": "Practices for deploying and maintaining ML systems in production",
                "option_3": "A machine learning library",
                "option_4": "An optimization algorithm",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 0,  # Incorrect
                "weight_4": 0,  # Incorrect
                "tags": ["mlops", "production_ml", "ml_engineering"]
            },
            {
                "question_text": "Why do companies use feature stores?",
                "option_1": "To store model weights",
                "option_2": "To share and reuse engineered features across teams",
                "option_3": "To save disk space",
                "option_4": "To train models faster",
                "weight_1": 0,  # Incorrect
                "weight_2": 3,  # Correct
                "weight_3": 1,  # Minor benefit
                "weight_4": 2,  # Secondary benefit
                "tags": ["feature_store", "ml_infrastructure", "feature_engineering"]
            }
        ]
        
        # Add all questions to database
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
        
        print(f"\n✅ Successfully seeded {question_count} questions!")
        print(f"   - Fundamentals: {len(fundamentals_questions)}")
        print(f"   - Applied: {len(applied_questions)}")
        print(f"   - Industry: {len(industry_questions)}")
        
        # Invalidate cache
        try:
            import redis
            r = redis.Redis()
            r.delete('tests:2:questions')
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
    seed_ml_questions()

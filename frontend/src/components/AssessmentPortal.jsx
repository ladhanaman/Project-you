// src/components/AssessmentPortal.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore.js';
import { submitAssessment, fetchQuestions } from '../services/apiService.js';
import QuestionCard from './QuestionCard.jsx';
import Stepper from './Stepper.jsx';
import LoadingScreen from './LoadingScreen.jsx';
import MainLayout from './MainLayout.jsx';

export default function AssessmentPortal() {
  const { testId } = useParams();
  const navigate = useNavigate();

  const {
    testState,
    setCurrentSection,
    setCurrentQuestionIndex,
    setAnswer,
    user,
    questions,
    setQuestions,
    setSubmissionResult,
    isSubmitting,
    setIsSubmitting,
    resetTestState,
    loadTestState,
    setCurrentTestId,
    clearTestState,
  } = useStore();

  const [submitError, setSubmitError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [restoredProgress, setRestoredProgress] = useState(false);

  // Reset submitting state on mount/unmount to prevent stale loading screens
  useEffect(() => {
    setIsSubmitting(false);
    return () => setIsSubmitting(false);
  }, [setIsSubmitting]);

  useEffect(() => {
    let timeoutId;

    const loadQuestions = async () => {
      try {
        const testIdNum = parseInt(testId);
        const data = await fetchQuestions(testIdNum);
        setQuestions(data);
        setCurrentTestId(testIdNum);

        // Try to load saved test state
        const wasRestored = loadTestState(testIdNum);

        if (wasRestored) {
          // Find first unanswered question
          const findFirstUnanswered = () => {
            // Access the current state from the store directly to ensure it's the loaded state
            const { answers } = useStore.getState().testState;

            // Check fundamentals
            for (let i = 0; i < data.fundamentals.length; i++) {
              if (!answers[data.fundamentals[i].id]) {
                return { section: 'fundamentals', index: i };
              }
            }

            // Check applied
            for (let i = 0; i < data.applied.length; i++) {
              if (!answers[data.applied[i].id]) {
                return { section: 'applied', index: i };
              }
            }

            // Check industry
            for (let i = 0; i < data.industry.length; i++) {
              if (!answers[data.industry[i].id]) {
                return { section: 'industry', index: i };
              }
            }

            // All answered - go to last question
            return {
              section: 'industry',
              index: data.industry.length - 1
            };
          };

          const firstUnanswered = findFirstUnanswered();
          setCurrentSection(firstUnanswered.section);
          setCurrentQuestionIndex(firstUnanswered.index);

          setRestoredProgress(true);
          timeoutId = setTimeout(() => setRestoredProgress(false), 2000);
        } else {
          // No saved state - start fresh
          resetTestState();
        }
      } catch (err) {
        setLoadError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadQuestions();

    // Cleanup timeout on unmount
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [testId, setQuestions, resetTestState, loadTestState, setCurrentTestId]);

  const currentSectionQuestions = questions[testState.currentSection] || [];
  const currentQuestion = currentSectionQuestions[testState.currentQuestionIndex];
  const answeredCount = Object.values(testState.answers).length;

  const totalQuestions =
    questions.fundamentals.length +
    questions.applied.length +
    questions.industry.length;

  const handleAnswer = (option) => {
    if (currentQuestion) {
      setAnswer(currentQuestion.id, option);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const result = await submitAssessment(parseInt(testId), testState.answers);
      setSubmissionResult(result);

      // Clear saved test state after successful submission
      clearTestState();

      // Use replace to prevent user from going back to test page
      navigate(`/results/${result.submission_id}`, { replace: true });
    } catch (err) {
      setSubmitError(err.message);
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    if (testState.currentQuestionIndex < currentSectionQuestions.length - 1) {
      setCurrentQuestionIndex(testState.currentQuestionIndex + 1);
    } else if (testState.currentSection === 'fundamentals') {
      setCurrentSection('applied');
    } else if (testState.currentSection === 'applied') {
      setCurrentSection('industry');
    } else {
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (testState.currentQuestionIndex > 0) {
      setCurrentQuestionIndex(testState.currentQuestionIndex - 1);
    } else if (testState.currentSection === 'applied') {
      setCurrentSection('fundamentals');
      setCurrentQuestionIndex(questions.fundamentals.length - 1);
    } else if (testState.currentSection === 'industry') {
      setCurrentSection('applied');
      setCurrentQuestionIndex(questions.applied.length - 1);
    }
  };

  if (isLoading) {
    return <LoadingScreen message="Loading assessment questions..." />;
  }

  if (loadError) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 max-w-md text-center">
            <div className="text-red-600 text-5xl mb-4">⚠</div>
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Error Loading Questions</h2>
            <p className="text-slate-600 mb-6">{loadError}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-slate-900 hover:bg-slate-800 text-white font-medium py-3 px-6 rounded-lg transition"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (isSubmitting) {
    return <LoadingScreen message="Submitting your assessment..." />;
  }

  if (!currentQuestion) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <p className="text-xl text-slate-500">No questions available</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto">
        <div className="mb-10">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Assessment Portal</h1>
              <p className="text-slate-500 mt-1">Candidate: {user?.full_name}</p>
            </div>
            <div className="text-right">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Progress
              </div>
              <div className="text-xl font-bold text-slate-900">
                {testState.currentQuestionIndex + 1}{' '}
                <span className="text-slate-400 font-normal">/ {currentSectionQuestions.length}</span>
              </div>
            </div>
          </div>

          <Stepper currentSection={testState.currentSection} />
        </div>

        {/* Small top-right popup notification */}
        {restoredProgress && (
          <div className="fixed top-6 right-6 bg-slate-800 text-slate-100 px-4 py-2.5 rounded-lg shadow-lg text-sm flex items-center gap-2 z-50 animate-fade-in">
            <span>
              Resumed at {testState.currentSection === 'fundamentals' ? 'Fundamentals' :
                testState.currentSection === 'applied' ? 'Applied' : 'Industry'}
            </span>
          </div>
        )}

        {submitError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm">
            <p className="font-medium">Submission Failed</p>
            <p>{submitError}</p>
          </div>
        )}

        <QuestionCard
          question={currentQuestion}
          onAnswer={handleAnswer}
          onNext={handleNext}
          onPrev={handlePrev}
          hasAnswered={testState.answers[currentQuestion.id]}
          isLastQuestion={
            testState.currentSection === 'industry' &&
            testState.currentQuestionIndex === currentSectionQuestions.length - 1
          }
          isSubmitting={isSubmitting}
        />

        <div className="flex justify-end items-center text-sm text-slate-400 mt-8">
          <p>
            Total answers: {answeredCount} of {totalQuestions}
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
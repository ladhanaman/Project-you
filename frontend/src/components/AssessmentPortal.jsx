// src/components/AssessmentPortal.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore.js';
import { submitAssessment, fetchQuestions } from '../services/apiService.js';
import QuestionCard from './QuestionCard.jsx';
// Removed Stepper.jsx and LoadingScreen.jsx - using inline components
import MainLayout from './MainLayout.jsx';

// Inline LoadingScreen replacement
const LoadingScreen = ({ message }) => (
  <MainLayout>
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  </MainLayout>
);

// Inline Stepper replacement (removed - not needed for PRI)
const Stepper = () => null;

export default function AssessmentPortal() {
  const { testId } = useParams();
  const navigate = useNavigate();
  const isPRI = parseInt(testId) === 1;

  const {
    testState,
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
        setCurrentTestId(testIdNum);

        // Try to load saved test state first (which now includes questions)
        const wasRestored = loadTestState(testIdNum);

        // Check if we have questions in the store (restored from cache)
        const currentStore = useStore.getState();
        if (wasRestored && currentStore.questions && currentStore.questions.length > 0) {
          console.log('Restored questions and state from local storage - Skipping API fetch');

          // Restore progress UI logic
          const { answers } = currentStore.testState;

          // Find first unanswered question
          const findFirstUnanswered = () => {
            for (let i = 0; i < currentStore.questions.length; i++) {
              if (!answers[currentStore.questions[i].id]) {
                return i;
              }
            }
            return currentStore.questions.length - 1;
          };

          setCurrentQuestionIndex(findFirstUnanswered());
          setRestoredProgress(true);
          timeoutId = setTimeout(() => setRestoredProgress(false), 2000);

          setIsLoading(false);
          return; // EXIT EARLY - DO NOT FETCH
        }

        // If not found in cache, fetch from API
        console.log('No cached questions found - Fetching from API');
        const data = await fetchQuestions(testIdNum);
        setQuestions(data.questions);  // Extract questions array from response

        // After fetching, save to store immediately to persist for next time
        // We trigger a dummy state save to persist the questions we just loaded
        useStore.getState().setCurrentQuestionIndex(0);

        // No saved state - start fresh
        resetTestState();

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

  const currentQuestion = questions[testState.currentQuestionIndex];
  const answeredCount = Object.values(testState.answers).length;
  const totalQuestions = questions.length;

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
    if (testState.currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(testState.currentQuestionIndex + 1);
    } else {
      // Last question - submit
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (testState.currentQuestionIndex > 0) {
      setCurrentQuestionIndex(testState.currentQuestionIndex - 1);
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
      <div className="max-w-full sm:max-w-3xl mx-auto px-4 sm:px-0">
        <div className="mb-10">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end mb-8 gap-4 sm:gap-0">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Assessment Portal</h1>
              <p className="text-slate-500 mt-1">Candidate: {user?.full_name}</p>
            </div>
            <div className="text-left sm:text-right">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Progress
              </div>
              <div className="text-xl font-bold text-slate-900">
                {testState.currentQuestionIndex + 1}{' '}
                <span className="text-slate-400 font-normal">/ {totalQuestions}</span>
              </div>
            </div>
          </div>

          {!isPRI && <Stepper />}
        </div>

        {/* Progress restoration notification */}
        {restoredProgress && (
          <div className="fixed top-6 right-6 bg-slate-800 text-slate-100 px-4 py-2.5 rounded-lg shadow-lg text-sm flex items-center gap-2 z-50 animate-fade-in">
            <span>
              Progress Restored - Question {testState.currentQuestionIndex + 1}
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
          isLastQuestion={testState.currentQuestionIndex === totalQuestions - 1}
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
// src/store/useStore.js
import { create } from 'zustand';

export const useStore = create((set, get) => ({
  // ============================================================================
  // AUTHENTICATION
  // ============================================================================
  // Initialize from localStorage to persist auth across page reloads
  user: (() => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  })(),
  token: localStorage.getItem('token') || null,

  setUser: (user) => set({ user }),
  setToken: (token) => {
    set({ token });
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  },

  setAuth: (user, token) => {
    set({ user, token });
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    }
  },

  logout: () => {
    set({ user: null, token: null, currentTestId: null });
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('testState');  // Clear test progress on logout
  },

  // No longer needed - state initializes from localStorage
  // Keeping for backward compatibility
  initializeAuth: () => {
    // This is now a no-op since initialization happens at store creation
  },

  // ============================================================================
  // TESTS
  // ============================================================================
  tests: [],
  setTests: (tests) => set({ tests }),

  currentTestId: null,
  setCurrentTestId: (testId) => set({ currentTestId: testId }),

  // ============================================================================
  // QUESTIONS (fetched from backend for specific test)
  // ============================================================================
  questions: [],
  setQuestions: (questions) => set({ questions }),

  // Get all questions (kept for compatibility, now just returns the array)
  getAllQuestions: () => {
    const { questions } = get();
    return questions;
  },

  // ============================================================================
  // TEST STATE (with localStorage persistence)
  // ============================================================================

  // Helper function to load test state from localStorage
  _loadTestState: (testId) => {
    try {
      const { user } = get();
      if (!user?.id) return null;

      // Use user-specific key key
      const key = `testState_user_${user.id}_test_${testId}`;
      const savedStateStr = localStorage.getItem(key);
      if (!savedStateStr) return null;

      const savedState = JSON.parse(savedStateStr);

      // Validate test ID matches (redundant with key but safe)
      if (savedState.testId !== testId) {
        localStorage.removeItem(key);
        return null;
      }

      // Check expiration (24 hours)
      const now = Date.now();
      const savedTime = savedState.timestamp || 0;
      const expirationTime = 24 * 60 * 60 * 1000; // 24 hours



      if (now - savedTime > expirationTime) {
        localStorage.removeItem(key);
        return null;
      }

      return savedState.state;
    } catch (error) {
      console.error('Failed to load test state:', error);
      localStorage.removeItem('testState');
      return null;
    }
  },

  // Helper function to save test state to localStorage
  _saveTestState: (testId, state) => {
    try {
      const { user } = get();
      if (!user?.id) return;

      const toSave = {
        testId,
        userId: user.id,  // Associate with current user
        state,
        timestamp: Date.now()
      };

      const key = `testState_user_${user.id}_test_${testId}`;
      localStorage.setItem(key, JSON.stringify(toSave));
    } catch (error) {
      console.error('Failed to save test state:', error);
      // Continue without persistence - non-critical error
    }
  },

  testState: {
    currentQuestionIndex: 0,
    answers: {},
  },

  // Load test state for a specific test (call when test loads)
  loadTestState: (testId) => {
    const { _loadTestState } = get();
    const savedState = _loadTestState(testId);

    if (savedState) {
      set({ testState: savedState });
      return true; // State was restored
    }
    return false; // No saved state
  },

  setCurrentQuestionIndex: (index) =>
    set((state) => {
      const newTestState = {
        ...state.testState,
        currentQuestionIndex: index
      };

      // Persist to localStorage
      const { currentTestId, _saveTestState } = get();
      if (currentTestId) {
        _saveTestState(currentTestId, newTestState);
      }

      return { testState: newTestState };
    }),

  setAnswer: (questionId, option) =>
    set((state) => {
      const newTestState = {
        ...state.testState,
        answers: { ...state.testState.answers, [questionId]: option },
      };

      // Persist to localStorage
      const { currentTestId, _saveTestState } = get();
      if (currentTestId) {
        _saveTestState(currentTestId, newTestState);
      }

      return { testState: newTestState };
    }),

  resetTestState: () => {
    // Clear localStorage for current user/test
    const { user, currentTestId } = get();
    if (user?.id && currentTestId) {
      const key = `testState_user_${user.id}_test_${currentTestId}`;
      localStorage.removeItem(key);
    }

    set({
      testState: {
        currentQuestionIndex: 0,
        answers: {},
      },
    });
  },

  // Clear test state after submission
  clearTestState: () => {
    const { user, currentTestId } = get();
    if (user?.id && currentTestId) {
      const key = `testState_user_${user.id}_test_${currentTestId}`;
      localStorage.removeItem(key);
    }

    set({
      testState: {
        currentQuestionIndex: 0,
        answers: {},
      },
    });
  },

  // ============================================================================
  // SUBMISSION RESULT
  // ============================================================================
  submissionResult: null,
  setSubmissionResult: (result) => set({ submissionResult: result }),

  submissionDetails: null,
  setSubmissionDetails: (details) => set({ submissionDetails: details }),

  // ============================================================================
  // LOADING & ERROR STATES
  // ============================================================================
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  isSubmitting: false,
  setIsSubmitting: (submitting) => set({ isSubmitting: submitting }),

  error: null,
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}));
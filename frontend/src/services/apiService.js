// src/services/apiService.js
import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Cache busting for GET requests to prevent stale data
  if (config.method === 'get' && config.url.includes('/submissions/')) {
    config.params = { ...config.params, _t: Date.now() };
  }

  return config;
});

// Response interceptor for handling 401 errors (token expired/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('testState');

      // Only redirect if not already on login page
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Parse Pydantic validation errors into user-friendly messages
const parseValidationError = (data) => {
  if (data?.detail && Array.isArray(data.detail)) {
    // Pydantic validation error format: { detail: [{ loc: [...], msg: "...", type: "..." }] }
    const firstError = data.detail[0];
    if (firstError?.msg) {
      // Clean up the message (remove "Value error, " prefix if present)
      return firstError.msg.replace(/^Value error,\s*/i, '');
    }
  }
  return 'Please check your input and try again.';
};

// Error handler with specific, user-friendly messages
const handleApiError = (error, context = 'request') => {
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail;

    // Map common errors to user-friendly messages
    const errorMessages = {
      400: {
        'Email already registered': 'This email is already registered. Please sign in or use a different email.',
        'default': detail || 'Invalid request. Please check your input and try again.'
      },
      401: {
        'Incorrect email or password': 'Invalid email or password. Please check your credentials and try again.',
        'default': 'Your session has expired. Please sign in again.'
      },
      403: {
        'default': 'You don\'t have permission to perform this action.'
      },
      404: {
        'default': 'The requested resource was not found.'
      },
      422: {
        'default': parseValidationError(error.response.data)
      },
      429: {
        'default': 'Too many attempts. Please wait a moment and try again.'
      },
      500: {
        'default': 'Server error. Please try again later.'
      }
    };

    // Find specific error message or use default for status code
    const statusMessages = errorMessages[status] || { 'default': 'An unexpected error occurred.' };
    const message = statusMessages[detail] || statusMessages['default'];

    throw new Error(message);
  } else if (error.request) {
    throw new Error('Unable to connect to server. Please check your internet connection.');
  } else {
    throw new Error('Something went wrong. Please try again.');
  }
};

// ============================================================================
// AUTHENTICATION
// ============================================================================

export const signup = async (email, password, fullName) => {
  try {
    const response = await api.post('/auth/signup', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/auth/me');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const completeOnboarding = async (data) => {
  try {
    const response = await api.post('/auth/onboarding', data);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const requestPasswordReset = async (email) => {
  try {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const resetPassword = async (token, newPassword) => {
  try {
    const response = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// ============================================================================
// TESTS
// ============================================================================

export const fetchTests = async () => {
  try {
    const response = await api.get('/tests');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const fetchQuestions = async (testId) => {
  try {
    const response = await api.get(`/tests/${testId}/questions`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

// ============================================================================
// SUBMISSIONS
// ============================================================================

export const submitAssessment = async (testId, answers) => {
  try {
    const formattedAnswers = Object.entries(answers).map(([questionId, selectedAnswer]) => ({
      question_id: parseInt(questionId, 10),
      selected_answer: selectedAnswer,
    }));

    const payload = {
      test_id: testId,
      answers: formattedAnswers,
    };

    const response = await api.post('/submissions', payload);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getSubmission = async (submissionId) => {
  try {
    const response = await api.get(`/submissions/${submissionId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getReportDownloadUrl = (submissionId) => {
  return `${API_BASE_URL}/submissions/${submissionId}/download`;
};

export const retryReportGeneration = async (submissionId) => {
  try {
    const response = await api.post(`/submissions/${submissionId}/retry`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getPRIReport = async (submissionId) => {
  try {
    const response = await api.get(`/pri/report/${submissionId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getReflectionSession = async (submissionId) => {
  try {
    const response = await api.get(`/pri/reflection-session/${submissionId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const submitDailyReflection = async (dayNumber, answer) => {
  try {
    const response = await api.post('/journey/submit', {
      day_number: dayNumber,
      answer: answer
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

export const getDailyReflections = async () => {
  try {
    const response = await api.get('/journey/history');
    return response.data;
  } catch (error) {
    // Don't throw error - this endpoint might not exist yet
    // Just return empty array so the UI can continue
    console.warn('Daily reflections endpoint not available:', error.response?.status);
    return [];
  }
};

export default {
  signup,
  login,
  getCurrentUser,
  fetchTests,
  fetchQuestions,
  submitAssessment,
  getSubmission,
  getReportDownloadUrl,
  retryReportGeneration,
  getPRIReport,
  getReflectionSession,
  submitDailyReflection,
  getDailyReflections,
};

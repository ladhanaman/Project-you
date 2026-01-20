// components/QuestionCard.jsx
import React from 'react';
import { ChevronRight, ChevronLeft, Send } from 'lucide-react';

export default function QuestionCard({
  question,
  onAnswer,
  onNext,
  onPrev,
  hasAnswered,
  isLastQuestion = false,
  isSubmitting = false
}) {
  // Handle both frontend format (question, options) and backend format (question_text, option_1-4)
  const questionText = question.question_text || question.question;
  const options = question.options || [
    question.option_1,
    question.option_2,
    question.option_3,
    question.option_4,
  ].filter(Boolean);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-6">
      {/* Question */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-slate-800 mb-4 leading-relaxed">{questionText}</h2>
      </div>

      {/* Options */}
      <div className="space-y-3 mb-8">
        {options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => onAnswer(option)}
            className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${hasAnswered === option
              ? 'border-slate-500 bg-slate-50 text-slate-900 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 cursor-pointer'
              }`}
          >
            <div className="flex items-center gap-4">
              <div
                className={`w-5 h-5 rounded-full border flex-shrink-0 transition-colors flex items-center justify-center ${hasAnswered === option
                  ? 'border-slate-800 bg-slate-800'
                  : 'border-slate-300'
                  }`}
              >
                {hasAnswered === option && (
                  <div className="w-2 h-2 rounded-full bg-white"></div>
                )}
              </div>
              <span className="font-medium text-slate-700 leading-relaxed">{option}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 pt-8 border-t border-slate-100">
        <button
          onClick={onPrev}
          className="flex items-center gap-2 px-4 py-2 text-slate-500 hover:text-slate-800 font-medium transition"
        >
          <ChevronLeft size={18} />
          Previous
        </button>



        <button
          onClick={onNext}
          disabled={!hasAnswered || (isLastQuestion && isSubmitting)}
          className={`ml-auto flex items-center gap-2 px-8 py-3 font-medium rounded-lg transition shadow-sm hover:shadow-md ${!hasAnswered || (isLastQuestion && isSubmitting)
            ? 'bg-slate-300 text-slate-500 cursor-not-allowed shadow-none'
            : isLastQuestion
              ? 'bg-slate-900 text-white hover:bg-slate-800'
              : 'bg-slate-900 text-white hover:bg-slate-800'
            }`}
        >
          {isLastQuestion ? (
            isSubmitting ? (
              <>
                Submitting...
                <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
              </>
            ) : (
              <>
                Submit Assessment
                <Send size={16} />
              </>
            )
          ) : (
            <>
              Next Question
              <ChevronRight size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
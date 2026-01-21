import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ReportViewer = ({ markdownContent }) => {
    if (!markdownContent) {
        return (
            <div className="text-gray-500 italic text-center p-8 bg-gray-50 rounded-lg">
                Report content is not available yet.
            </div>
        );
    }

    return (
        <div className="prose prose-indigo max-w-none">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Override headers for better styling
                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold text-gray-900 mt-8 mb-4 border-b border-gray-200 pb-2" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-xl font-bold text-gray-800 mt-6 mb-3" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-lg font-semibold text-indigo-700 mt-4 mb-2" {...props} />,
                    // Style lists
                    ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-4 space-y-1 text-gray-700" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-4 space-y-1 text-gray-700" {...props} />,
                    li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                    // Style paragraphs
                    p: ({ node, ...props }) => <p className="mb-4 text-gray-700 leading-relaxed" {...props} />,
                    // Style blockquotes
                    blockquote: ({ node, ...props }) => (
                        <blockquote className="border-l-4 border-indigo-300 pl-4 py-2 italic bg-indigo-50 rounded-r-lg my-4 text-gray-700" {...props} />
                    ),
                    // Style strong/bold
                    strong: ({ node, ...props }) => <strong className="font-bold text-gray-900" {...props} />,
                }}
            >
                {markdownContent}
            </ReactMarkdown>
        </div>
    );
};

export default ReportViewer;

// src/data/questions.js
const QUESTIONS = {
  "fundamentals": [
    {
      "id": "f1",
      "question": "What is the time complexity of binary search?",
      "options": ["O(n)", "O(log n)", "O(n²)", "O(2^n)"],
      "correct": "O(log n)"
    },
    {
      "id": "f2",
      "question": "Which data structure uses LIFO principle?",
      "options": ["Queue", "Stack", "Array", "Linked List"],
      "correct": "Stack"
    },
    {
      "id": "f3",
      "question": "What does HTTP stand for?",
      "options": [
        "Hyper Text Transfer Protocol",
        "High Transfer Text Protocol",
        "Hyper Transfer Text Protocol",
        "High Text Transfer Protocol"
      ],
      "correct": "Hyper Text Transfer Protocol"
    },
    {
      "id": "f4",
      "question": "Which sorting algorithm has O(n²) worst-case complexity?",
      "options": ["Quick Sort", "Merge Sort", "Bubble Sort", "Heap Sort"],
      "correct": "Bubble Sort"
    },
    {
      "id": "f5",
      "question": "What is a pure function?",
      "options": [
        "A function that returns nothing",
        "A function with no side effects that always returns the same output for the same input",
        "A function that uses pure HTML",
        "A function written in Python"
      ],
      "correct": "A function with no side effects that always returns the same output for the same input"
    }
  ],
  "applied": [
    {
      "id": "a1",
      "question": "How would you optimize a React component that re-renders unnecessarily?",
      "options": [
        "Use React.memo and useCallback",
        "Add more state variables",
        "Use inline styling",
        "Increase component complexity"
      ],
      "correct": "Use React.memo and useCallback"
    },
    {
      "id": "a2",
      "question": "What is the purpose of middleware in Express.js?",
      "options": [
        "To slow down requests",
        "To process requests/responses and pass control to the next middleware",
        "To store data permanently",
        "To create database connections only"
      ],
      "correct": "To process requests/responses and pass control to the next middleware"
    },
    {
      "id": "a3",
      "question": "Which approach helps prevent SQL injection attacks?",
      "options": [
        "String concatenation",
        "Parameterized queries",
        "Direct SQL execution",
        "Using public databases"
      ],
      "correct": "Parameterized queries"
    },
    {
      "id": "a4",
      "question": "How does the Virtual DOM improve React performance?",
      "options": [
        "It directly manipulates the browser DOM",
        "It batches updates and only re-renders changed elements",
        "It removes the need for state management",
        "It eliminates JavaScript entirely"
      ],
      "correct": "It batches updates and only re-renders changed elements"
    },
    {
      "id": "a5",
      "question": "What is the main benefit of using REST API over SOAP?",
      "options": [
        "REST is always faster",
        "REST is simpler, uses HTTP, and is more scalable",
        "REST requires less code to write",
        "REST can only work with JSON"
      ],
      "correct": "REST is simpler, uses HTTP, and is more scalable"
    }
  ],
  "industry": [
    {
      "id": "i1",
      "question": "How should you approach system design for a large-scale application?",
      "options": [
        "Start coding immediately",
        "Plan architecture, database schema, and scalability concerns upfront",
        "Use the smallest database possible",
        "Optimize prematurely"
      ],
      "correct": "Plan architecture, database schema, and scalability concerns upfront"
    },
    {
      "id": "i2",
      "question": "What is the advantage of microservices over monolithic architecture?",
      "options": [
        "Easier to debug",
        "Reduced complexity",
        "Better scalability, independent deployment, and fault isolation",
        "Lower cost"
      ],
      "correct": "Better scalability, independent deployment, and fault isolation"
    },
    {
      "id": "i3",
      "question": "Which practice is crucial for maintaining code quality in teams?",
      "options": [
        "Code reviews and continuous integration",
        "Writing code as fast as possible",
        "Avoiding documentation",
        "Using only JavaScript"
      ],
      "correct": "Code reviews and continuous integration"
    },
    {
      "id": "i4",
      "question": "How do you handle version control in a collaborative environment?",
      "options": [
        "Commit directly to main branch",
        "Use feature branches, pull requests, and code reviews",
        "Never merge branches",
        "Avoid using Git"
      ],
      "correct": "Use feature branches, pull requests, and code reviews"
    },
    {
      "id": "i5",
      "question": "What is the role of monitoring and observability in production systems?",
      "options": [
        "To slow down the system",
        "Unnecessary for modern applications",
        "To detect issues, track performance, and enable quick incident response",
        "To replace testing"
      ],
      "correct": "To detect issues, track performance, and enable quick incident response"
    }
  ]
};

export default QUESTIONS;
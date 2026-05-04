# Flash Quiz - Lab 8 Pygame Learning Tool

A web-based interactive quiz application for testing knowledge of the Lab 8 Pygame project, architecture, physics mechanics, and web utilities.

## Overview

Flash Quiz provides a comprehensive assessment tool with 6 different quiz modules covering:

- **Pygame Fundamentals** - Core Pygame concepts and project basics (Beginner)
- **Physics & Movement** - Physics simulation, collision detection, and kinematics (Intermediate)
- **Architecture & Design** - Project architecture, system design patterns (Intermediate)
- **Code Organization** - Codebase structure, functions, and best practices (Beginner)
- **Code Explorer Utility** - Web-based file browser and API (Beginner)
- **Advanced Pygame Concepts** - Deep dive into simulation mechanics (Advanced)

## Quick Start

### 1. Start the Quiz Server

```bash
python quiz/serve.py
```

The quiz will run on `http://127.0.0.1:8001`

### 2. Open in Browser

Navigate to:

```
http://127.0.0.1:8001
```

### 3. Select a Quiz

Click on any quiz card to begin. Each quiz includes:

- Multiple-choice questions
- Time tracking
- Progress indicator
- Detailed explanations for each question

## Features

### Quiz Interface

- **Quiz Selection**: Browse available quizzes with difficulty ratings and time estimates
- **Question Navigation**: Move between questions with Previous/Next buttons
- **Progress Tracking**: Visual progress bar and question counter
- **Timer**: Real-time elapsed time display
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Results Screen

After completing a quiz, view:

- **Score Summary**: Total correct out of total questions
- **Performance Percentage**: Visual percentage circle
- **Time Taken**: Total duration of quiz
- **Answer Review**: Detailed review of each question with:
  - Your answer
  - Correct answer (if wrong)
  - Explanation of correct answer

### Quiz Modes

| Quiz                     | Questions | Time Limit | Difficulty   |
| ------------------------ | --------- | ---------- | ------------ |
| Pygame Fundamentals      | 5         | 10 min     | Beginner     |
| Physics & Movement       | 5         | 15 min     | Intermediate |
| Architecture & Design    | 5         | 15 min     | Intermediate |
| Code Organization        | 5         | 10 min     | Beginner     |
| Code Explorer Utility    | 5         | 10 min     | Beginner     |
| Advanced Pygame Concepts | 5         | 20 min     | Advanced     |

## Question Types

### Multiple Choice

Each question presents 4 options. Select the correct answer and proceed to the next question.

Example:

```
Q: What is the target frame rate (FPS)?
A) 30 FPS
B) 60 FPS ← Correct
C) 120 FPS
D) 144 FPS
```

## API Endpoints

The quiz server provides a RESTful API for quiz management:

### GET `/api/quizzes`

Returns all available quizzes with metadata:

```json
{
  "quizzes": [
    {
      "id": "pygame-basics",
      "title": "Pygame Fundamentals",
      "description": "...",
      "difficulty": "beginner",
      "timeLimit": 600,
      "questions": [...]
    }
  ]
}
```

### GET `/api/quiz?id=<quiz_id>`

Returns detailed quiz data including all questions:

```json
{
  "id": "pygame-basics",
  "title": "Pygame Fundamentals",
  "questions": [
    {
      "id": 1,
      "question": "What is the target frame rate?",
      "type": "multiple-choice",
      "options": ["30 FPS", "60 FPS", "120 FPS", "144 FPS"],
      "correct": 1,
      "explanation": "..."
    }
  ]
}
```

### GET `/api/submit?id=<quiz_id>`

Submits quiz answers and returns completion status:

```json
{
  "quizId": "pygame-basics",
  "status": "submitted"
}
```

## File Structure

```
quiz/
├── serve.py              # Python HTTP server backend
├── index.html            # Quiz interface HTML
├── app.js                # Client-side JavaScript logic
├── styles.css            # Responsive styling
├── questions.json        # Quiz questions database
└── README.md             # This file
```

## Architecture

### Backend (serve.py)

- **ThreadingHTTPServer**: Serves quiz API and static assets on port 8001
- **Route Handlers**:
  - `/api/quizzes` - List all quizzes
  - `/api/quiz?id=...` - Get specific quiz
  - `/api/submit?id=...` - Submit answers
  - `/`, `/index.html`, `/app.js`, `/styles.css` - Static assets

### Frontend (HTML/CSS/JavaScript)

- **State Management**: Tracks current quiz, question index, user answers, timing
- **Views**:
  - Quiz Selection - Browse and start quizzes
  - Quiz Taking - Answer questions with progress tracking
  - Results - Review performance and answers
- **Features**:
  - Real-time timer
  - Progress bar
  - Answer review with explanations
  - Retake functionality

## Usage Workflow

```
1. Load Quiz Selection View
   ↓
2. Click "Start Quiz"
   ↓
3. Answer Questions (navigate with Previous/Next)
   ↓
4. Click "Finish Quiz"
   ↓
5. View Results & Explanations
   ↓
6. Retake or Return to Quizzes
```

## Question Design

Each question includes:

- **Question Text**: Clear, concise learning objective
- **Multiple Options**: 4 answer choices (beginner) to challenge learners
- **Correct Answer**: Marked in questions.json
- **Explanation**: Learning resource explaining why the answer is correct

### Topics Covered

**Pygame Fundamentals**

- FPS and frame rate targets
- Core classes and data structures
- Rendering and display management

**Physics & Movement**

- Collision detection and response
- Velocity and acceleration
- Size-based physics scaling
- Entity lifecycle management

**Architecture & Design**

- Multi-runtime architecture
- Performance characteristics
- Data structure choices

**Code Organization**

- Function naming conventions
- Module structure
- Type annotations
- Helper function patterns

**Web Utilities**

- HTTP API design
- File serving and security
- Query parameters
- Response formats

**Advanced Topics**

- Physics integration with delta time
- Rendering optimization
- Chase and behavior blending
- Performance tuning

## Extending the Quiz

### Add New Quiz

1. Edit `questions.json`
2. Add quiz object to `quizzes` array:

```json
{
  "id": "new-quiz",
  "title": "New Quiz Title",
  "description": "Description",
  "difficulty": "beginner|intermediate|advanced",
  "timeLimit": 600,
  "questions": [
    {
      "id": 1,
      "question": "Question text?",
      "type": "multiple-choice",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Why this is correct..."
    }
  ]
}
```

### Add New Question Type

1. Update `questions.json` with new `type` field
2. Modify `renderQuestion()` in `app.js` to handle new type
3. Update `selectAnswer()` to store answers for new type

## Performance Notes

- **Quiz Data**: ~300 KB questions.json (all 30 questions across 6 quizzes)
- **Load Time**: <500ms on typical connection
- **UI Response**: <50ms on most interactions
- **Memory**: ~2-5 MB during quiz session

## Security

- **Local-only**: Server runs on 127.0.0.1:8001 (no remote access)
- **No persistence**: Quiz results not stored
- **No authentication**: Assumes trusted local environment
- **No external dependencies**: Uses Python standard library only

## Troubleshooting

### Quiz won't load

```bash
# Check if server is running
curl http://127.0.0.1:8001/api/quizzes

# Check file permissions
ls -la quiz/
```

### Questions not displaying

- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for JavaScript errors (F12)
- Verify `questions.json` is valid JSON

### Timer not updating

- Check browser JavaScript is enabled
- Verify no browser extensions are blocking JavaScript

## Related Tools

- **Pygame Simulation**: Run `python main.py`
- **Code Explorer**: Run `python code-explorer/serve.py` on port 8000
- **Architecture Docs**: See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Project README**: See [README.md](../README.md)

## License

Part of Lab 8 - Educational Project

## Support

For issues or questions, refer to:

- [Architecture Documentation](../ARCHITECTURE.md)
- [Project README](../README.md)
- [Code Explorer](../code-explorer/README.md)

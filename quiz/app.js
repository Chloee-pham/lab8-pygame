/**
 * Flash Quiz - Interactive Learning Application
 * Lab 8 Pygame Project Knowledge Assessment Tool
 */

const state = {
  quizzes: [],
  currentQuiz: null,
  currentQuestionIndex: 0,
  userAnswers: {},
  startTime: null,
  timerInterval: null,
};

// DOM Elements
const quizSelectionView = document.getElementById("quizSelectionView");
const quizTakingView = document.getElementById("quizTakingView");
const resultsView = document.getElementById("resultsView");
const quizList = document.getElementById("quizList");
const quizTitle = document.getElementById("quizTitle");
const questionContainer = document.getElementById("questionContainer");
const questionProgress = document.getElementById("questionProgress");
const progressFill = document.getElementById("progressFill");
const timer = document.getElementById("timer");
const prevButton = document.getElementById("prevButton");
const nextButton = document.getElementById("nextButton");
const backButton = document.getElementById("backButton");
const retakeButton = document.getElementById("retakeButton");
const homeButton = document.getElementById("homeButton");

/**
 * Format seconds into MM:SS format
 */
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Start timer and update UI
 */
function startTimer() {
  state.startTime = Date.now();
  state.timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    timer.textContent = `Time: ${formatTime(elapsed)}`;
  }, 1000);
}

/**
 * Stop timer
 */
function stopTimer() {
  if (state.timerInterval) {
    clearInterval(state.timerInterval);
  }
}

/**
 * Load quizzes from API
 */
async function loadQuizzes() {
  try {
    const response = await fetch("/api/quizzes");
    const data = await response.json();
    state.quizzes = data.quizzes || [];
    renderQuizSelection();
  } catch (error) {
    console.error("Failed to load quizzes:", error);
    quizList.innerHTML =
      '<p class="error">Failed to load quizzes. Please refresh the page.</p>';
  }
}

/**
 * Render quiz selection view
 */
function renderQuizSelection() {
  quizList.innerHTML = state.quizzes
    .map(
      (quiz) => `
    <div class="quiz-card" data-quiz-id="${quiz.id}">
      <div class="quiz-card-header">
        <h3>${quiz.title}</h3>
        <span class="difficulty ${quiz.difficulty}">${quiz.difficulty}</span>
      </div>
      <p class="quiz-description">${quiz.description}</p>
      <div class="quiz-info">
        <span class="info-item">📝 ${quiz.questions.length} questions</span>
        <span class="info-item">⏱️ ${Math.ceil(quiz.timeLimit / 60)} minutes</span>
      </div>
      <button class="btn-primary" onclick="startQuiz('${quiz.id}')">Start Quiz</button>
    </div>
  `,
    )
    .join("");
}

/**
 * Start a quiz
 */
function startQuiz(quizId) {
  state.currentQuiz = state.quizzes.find((q) => q.id === quizId);
  if (!state.currentQuiz) return;

  state.currentQuestionIndex = 0;
  state.userAnswers = {};
  state.startTime = null;

  showView(quizTakingView);
  quizTitle.textContent = state.currentQuiz.title;
  startTimer();
  renderQuestion();
  updateProgressBar();
}

/**
 * Show specific view, hide others
 */
function showView(view) {
  [quizSelectionView, quizTakingView, resultsView].forEach((v) =>
    v.classList.remove("active"),
  );
  view.classList.add("active");
}

/**
 * Render current question
 */
function renderQuestion() {
  const question = state.currentQuiz.questions[state.currentQuestionIndex];
  const totalQuestions = state.currentQuiz.questions.length;
  questionProgress.textContent = `Question ${state.currentQuestionIndex + 1}/${totalQuestions}`;

  let html = `
    <div class="question">
      <h3>${question.question}</h3>
  `;

  if (question.type === "multiple-choice") {
    html += '<div class="options">';
    question.options.forEach((option, index) => {
      const isSelected =
        state.userAnswers[state.currentQuestionIndex] === index;
      html += `
        <label class="option ${isSelected ? "selected" : ""}">
          <input 
            type="radio" 
            name="answer" 
            value="${index}"
            ${isSelected ? "checked" : ""}
            onchange="selectAnswer(${index})"
          />
          <span>${option}</span>
        </label>
      `;
    });
    html += "</div>";
  }

  html += "</div>";
  questionContainer.innerHTML = html;

  // Update button states
  prevButton.disabled = state.currentQuestionIndex === 0;
  nextButton.textContent =
    state.currentQuestionIndex === totalQuestions - 1
      ? "Finish Quiz"
      : "Next →";
}

/**
 * Select an answer
 */
function selectAnswer(answerIndex) {
  state.userAnswers[state.currentQuestionIndex] = answerIndex;
  updateProgressBar();
}

/**
 * Move to next question
 */
function nextQuestion() {
  if (state.currentQuestionIndex < state.currentQuiz.questions.length - 1) {
    state.currentQuestionIndex++;
    renderQuestion();
    updateProgressBar();
  } else {
    finishQuiz();
  }
}

/**
 * Move to previous question
 */
function prevQuestion() {
  if (state.currentQuestionIndex > 0) {
    state.currentQuestionIndex--;
    renderQuestion();
    updateProgressBar();
  }
}

/**
 * Update progress bar
 */
function updateProgressBar() {
  const totalQuestions = state.currentQuiz.questions.length;
  const answeredQuestions = Object.keys(state.userAnswers).length;
  const percentage = (answeredQuestions / totalQuestions) * 100;
  progressFill.style.width = `${percentage}%`;
}

/**
 * Finish quiz and show results
 */
function finishQuiz() {
  stopTimer();
  const timeTaken = Math.floor((Date.now() - state.startTime) / 1000);
  calculateAndShowResults(timeTaken);
}

/**
 * Calculate results and show results view
 */
function calculateAndShowResults(timeTaken) {
  let correct = 0;
  state.currentQuiz.questions.forEach((question, index) => {
    if (state.userAnswers[index] === question.correct) {
      correct++;
    }
  });

  const total = state.currentQuiz.questions.length;
  const percentage = Math.round((correct / total) * 100);

  document.getElementById("scoreValue").textContent = correct;
  document.getElementById("totalValue").textContent = total;
  document.getElementById("percentageValue").textContent = `${percentage}%`;
  document.getElementById("correctCount").textContent = correct;
  document.getElementById("incorrectCount").textContent = total - correct;
  document.getElementById("timeTaken").textContent = formatTime(timeTaken);

  renderReview();
  showView(resultsView);
}

/**
 * Render review of answers
 */
function renderReview() {
  const reviewHtml = state.currentQuiz.questions
    .map((question, index) => {
      const userAnswerIndex = state.userAnswers[index];
      const isCorrect = userAnswerIndex === question.correct;
      const userAnswer = question.options[userAnswerIndex] || "Not answered";
      const correctAnswer = question.options[question.correct];

      return `
        <div class="review-item ${isCorrect ? "correct" : "incorrect"}">
          <div class="review-question">
            <span class="review-icon">${isCorrect ? "✓" : "✗"}</span>
            <h4>${question.question}</h4>
          </div>
          <div class="review-answer">
            <div class="your-answer">
              <strong>Your Answer:</strong> ${userAnswer}
            </div>
            ${
              !isCorrect
                ? `<div class="correct-answer"><strong>Correct Answer:</strong> ${correctAnswer}</div>`
                : ""
            }
            <div class="explanation">${question.explanation}</div>
          </div>
        </div>
      `;
    })
    .join("");

  document.getElementById("reviewSection").innerHTML = reviewHtml;
}

/**
 * Retake current quiz
 */
function retakeQuiz() {
  const quizId = state.currentQuiz.id;
  startQuiz(quizId);
}

/**
 * Go back to quiz selection
 */
function goHome() {
  stopTimer();
  showView(quizSelectionView);
  state.currentQuiz = null;
}

// Event Listeners
prevButton.addEventListener("click", prevQuestion);
nextButton.addEventListener("click", nextQuestion);
backButton.addEventListener("click", goHome);
retakeButton.addEventListener("click", retakeQuiz);
homeButton.addEventListener("click", goHome);

// Initialize
document.addEventListener("DOMContentLoaded", loadQuizzes);

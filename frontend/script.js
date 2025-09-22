// --- Constants ---
const API_BASE_URL = 'http://127.0.0.1:5000/api';
let currentLessonContent = ''; // Store the current lesson text
let currentAssessment = null; // Store the current assessment

// --- DOM Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners when the page is fully loaded
    const topicButtonsContainer = document.getElementById('topic-buttons');
    if (topicButtonsContainer) {
        topicButtonsContainer.addEventListener('click', handleTopicClick);
    }

    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    const lessonDisplay = document.getElementById('lesson-display');
    if (lessonDisplay) {
        lessonDisplay.addEventListener('mouseup', handleTextSelection);
    }

    const popup = document.getElementById('text-selection-popup');
    if (popup) {
        popup.addEventListener('click', handleExplainPopupClick);
    }
});

// --- API Helper Function ---
async function postToApi(endpoint, body) {
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error calling API endpoint: ${endpoint}`, error);
        throw error; // Re-throw the error to be handled by the caller
    }
}

// --- Chat Functionality ---
async function handleChatSubmit(event) {
    event.preventDefault();
    const chatInput = document.getElementById('chat-input');
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, 'user-message');
    chatInput.value = '';
    const loadingMessage = appendMessage('Thinking...', 'bot-message');

    try {
        const data = await postToApi('chat', { message: userMessage });
        loadingMessage.textContent = data.reply;
    } catch (error) {
        loadingMessage.textContent = 'Sorry, I encountered an error. Please try again.';
    }
    scrollToBottom('chat-messages');
}

function appendMessage(text, className) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElem = document.createElement('div');
    messageElem.className = `message ${className}`;
    messageElem.textContent = text;
    chatMessages.appendChild(messageElem);
    scrollToBottom('chat-messages');
    return messageElem;
}

// --- Lesson Generation ---
async function handleTopicClick(event) {
    if (event.target.tagName !== 'BUTTON') return;

    const topic = event.target.dataset.topic;
    const lessonDisplay = document.getElementById('lesson-display');
    lessonDisplay.style.display = 'block';
    lessonDisplay.innerHTML = `<h2>Loading lesson on "${topic}"...</h2><p>Please wait while the AI generates your personalized content.</p>`;
    
    try {
        const data = await postToApi('generate_lesson', { topic });
        currentLessonContent = data.lesson_content; // Save lesson content
        renderLesson(data.topic, data.lesson_content);
    } catch (error) {
        lessonDisplay.innerHTML = `<h2>Error</h2><p>Sorry, we couldn't generate the lesson. Please try again later.</p>`;
    }
}

function renderLesson(topic, content) {
    const lessonDisplay = document.getElementById('lesson-display');
    // Basic formatting for presentation
    const formattedContent = content.replace(/\n/g, '<br>');
    lessonDisplay.innerHTML = `
        <h2>${topic}</h2>
        <div id="lesson-text-content">${formattedContent}</div>
        <div class="ai-tools">
            <button id="summarize-btn">✨ Get Revision Notes</button>
            <button id="practice-btn">📝 Take Assessment</button>
        </div>
        <div id="revision-notes-container" style="display:none;"></div>
        <div id="assessment-container" style="display:none;"></div>
    `;
    // Add event listeners to the new buttons
    document.getElementById('summarize-btn').addEventListener('click', handleSummarizeClick);
    document.getElementById('practice-btn').addEventListener('click', handlePracticeClick);
}

// --- AI Tools for Lessons ---
async function handleSummarizeClick() {
    const notesContainer = document.getElementById('revision-notes-container');
    notesContainer.style.display = 'block';
    notesContainer.innerHTML = '<h3>Generating Revision Notes...</h3>';
    try {
        const data = await postToApi('revision_notes', { text: currentLessonContent });
        notesContainer.innerHTML = `<h3>Revision Notes</h3><div>${data.notes.replace(/\n/g, '<br>')}</div>`;
    } catch (error) {
        notesContainer.innerHTML = '<h3>Error</h3><p>Could not generate revision notes.</p>';
    }
}

async function handlePracticeClick() {
    const assessmentContainer = document.getElementById('assessment-container');
    assessmentContainer.style.display = 'block';
    assessmentContainer.innerHTML = '<h3>Generating Assessment...</h3>';
    try {
        let data = await postToApi('generate_assessment', { text: currentLessonContent });
        // The backend returns a stringified JSON, so we need to parse it
        currentAssessment = JSON.parse(data); 
        renderAssessment(currentAssessment);
    } catch (error) {
        assessmentContainer.innerHTML = '<h3>Error</h3><p>Could not generate the assessment.</p>';
    }
}

// --- Assessment Rendering and Logic ---
function renderAssessment(assessment) {
    const assessmentContainer = document.getElementById('assessment-container');
    let questionsHtml = assessment.questions.map((q, index) => `
        <div class="question" id="question-${index}">
            <p><strong>${index + 1}. ${q.question}</strong></p>
            ${q.options.map(opt => `
                <label>
                    <input type="radio" name="question-${index}" value="${opt}">
                    ${opt}
                </label>
            `).join('')}
        </div>
    `).join('');

    assessmentContainer.innerHTML = `
        <h3>Assessment</h3>
        <form id="assessment-form">
            ${questionsHtml}
            <button type="submit" class="ai-tools-button">Submit Answers</button>
        </form>
        <div id="assessment-results" style="display:none;"></div>
    `;
    document.getElementById('assessment-form').addEventListener('submit', handleSubmitAssessment);
}

function handleSubmitAssessment(event) {
    event.preventDefault();
    const resultsContainer = document.getElementById('assessment-results');
    resultsContainer.style.display = 'block';

    let score = 0;
    currentAssessment.questions.forEach((q, index) => {
        const form = event.target;
        const selectedOption = form.querySelector(`input[name="question-${index}"]:checked`);
        if (selectedOption && selectedOption.value === q.answer) {
            score++;
        }
    });

    resultsContainer.innerHTML = `
        <h3>Assessment Results</h3>
        <p>You scored <strong>${score} out of ${currentAssessment.questions.length}</strong>.</p>
    `;
}


// --- Text Selection Popup ---
function handleTextSelection() {
    const popup = document.getElementById('text-selection-popup');
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (selectedText.length > 5) { // Only show for meaningful selections
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        popup.style.top = `${rect.top + window.scrollY - popup.offsetHeight - 5}px`;
        popup.style.left = `${rect.left + window.scrollX + (rect.width / 2) - (popup.offsetWidth / 2)}px`;
        popup.style.display = 'block';
    } else {
        popup.style.display = 'none';
    }
}

async function handleExplainPopupClick() {
    const popup = document.getElementById('text-selection-popup');
    const selectedText = window.getSelection().toString().trim();
    popup.style.display = 'none'; // Hide popup after click

    if (selectedText) {
        const userMessage = `Can you explain this concept in simpler terms: "${selectedText}"`;
        appendMessage(userMessage, 'user-message');
        const loadingMessage = appendMessage('Explaining...', 'bot-message');
        
        try {
            const data = await postToApi('chat', { message: userMessage });
            loadingMessage.textContent = data.reply;
        } catch (error) {
            loadingMessage.textContent = 'Sorry, I couldn\'t explain that. Please try again.';
        }
        scrollToBottom('chat-messages');
    }
}


// --- Utility Functions ---
function scrollToBottom(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
}


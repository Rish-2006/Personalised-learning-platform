// Set the backend API address
const API_URL = 'http://127.0.0.1:5000';

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Attach event listeners to topic buttons
    const topicButtons = document.getElementById('topic-buttons');
    if (topicButtons) {
        topicButtons.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON') {
                const topic = event.target.dataset.topic;
                generateLesson(topic);
            }
        });
    }

    // Attach event listener to the chat form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    // Text selection popup logic
    const lessonDisplay = document.getElementById('lesson-display');
    const popup = document.getElementById('text-selection-popup');
    if (lessonDisplay && popup) {
        lessonDisplay.addEventListener('mouseup', (event) => {
            const selection = window.getSelection().toString().trim();
            if (selection) {
                popup.style.left = `${event.pageX}px`;
                popup.style.top = `${event.pageY}px`;
                popup.style.display = 'block';
                popup.dataset.selectedText = selection;
            } else {
                popup.style.display = 'none';
            }
        });

        // Hide popup when clicking elsewhere
        document.addEventListener('mousedown', (event) => {
            if (!popup.contains(event.target)) {
                popup.style.display = 'none';
            }
        });

        popup.addEventListener('click', () => {
            const text = popup.dataset.selectedText;
            explainText(text);
            popup.style.display = 'none';
        });
    }
});


// --- Core Functions ---

// Function to generate a new lesson
async function generateLesson(topic) {
    const lessonDisplay = document.getElementById('lesson-display');
    lessonDisplay.style.display = 'block';
    lessonDisplay.innerHTML = `<h2>Generating Lesson on "${topic}"...</h2><p>Please wait while the AI prepares your content.</p>`;

    try {
        const response = await fetch(`${API_URL}/api/generate_lesson`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        lessonDisplay.innerHTML = `
            <h2>${data.topic}</h2>
            <div id="lesson-content-text">${data.lesson_content.replace(/\n/g, '<br>')}</div>
            <div class="ai-tools">
                <button id="summarize-btn">✨ Get Revision Notes</button>
                <button id="questions-btn">✨ Take Assessment</button>
            </div>
            <div id="revision-notes-container" style="display:none; margin-top: 1.5rem; padding: 1rem; background: #eef2ff; border-radius: 8px;"></div>
            <div id="assessment-container" style="display:none; margin-top: 1.5rem;"></div>
        `;

        // Attach event listeners to the new buttons
        document.getElementById('summarize-btn').addEventListener('click', () => getRevisionNotes(data.lesson_content));
        document.getElementById('questions-btn').addEventListener('click', () => getAssessment(data.lesson_content));

    } catch (error) {
        console.error('Failed to generate lesson:', error);
        lessonDisplay.innerHTML = `<h2>Error</h2><p>Sorry, we couldn't generate the lesson. Please try again later.</p>`;
    }
}

// Function to handle chat submissions
async function handleChatSubmit(event) {
    event.preventDefault();
    const chatInput = document.getElementById('chat-input');
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    addMessageToChat('user-message', userMessage);
    chatInput.value = '';

    const botMessageElem = addMessageToChat('bot-message', 'Thinking...');

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });
        const data = await response.json();
        botMessageElem.textContent = data.reply;
    } catch (error) {
        console.error('Chat error:', error);
        botMessageElem.textContent = 'Sorry, I encountered an error. Please try again.';
    }
}

// Function to get revision notes
async function getRevisionNotes(lessonContent) {
    const notesContainer = document.getElementById('revision-notes-container');
    notesContainer.style.display = 'block';
    notesContainer.innerHTML = `<h3>Revision Notes</h3><p>Generating summary...</p>`;
    
    try {
        const response = await fetch(`${API_URL}/api/revision_notes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: lessonContent })
        });
        const data = await response.json();
        notesContainer.innerHTML = `<h3>Revision Notes</h3><div>${data.notes.replace(/\n/g, '<br>')}</div>`;
    } catch (error) {
        console.error('Failed to get revision notes:', error);
        notesContainer.innerHTML = `<h3>Error</h3><p>Sorry, I couldn't create a summary.</p>`;
    }
}

// Function to get an assessment
async function getAssessment(lessonContent) {
    const assessmentContainer = document.getElementById('assessment-container');
    assessmentContainer.style.display = 'block';
    assessmentContainer.innerHTML = `<h3>Practice Questions</h3><p>Generating assessment...</p>`;

    try {
        const response = await fetch(`${API_URL}/api/generate_assessment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: lessonContent })
        });
        const data = JSON.parse(await response.json()); // The backend sends a JSON string
        
        if (data.questions && data.questions.length > 0) {
            let assessmentHTML = '<h3>Practice Questions</h3><form id="assessment-form">';
            data.questions.forEach((q, index) => {
                const safeName = `question-${index}`;
                assessmentHTML += `<div class="question-block" style="margin-bottom: 1rem;">
                    <p><strong>${index + 1}. ${q.question}</strong></p>`;
                q.options.forEach((option, i) => {
                    const safeId = `q${index}-option${i}`;
                    assessmentHTML += `<div class="option" style="margin-bottom: 0.5rem;">
                        <input type="radio" name="${safeName}" value="${option}" id="${safeId}">
                        <label for="${safeId}" style="margin-left: 0.5rem;">${option}</label>
                    </div>`;
                });
                assessmentHTML += `<input type="hidden" id="answer-${index}" value="${q.answer}"></div>`;
            });
            assessmentHTML += `<button type="submit" style="padding: 0.7rem 1.2rem; border: none; background: var(--primary-color); color: var(--white); border-radius: 8px; cursor: pointer;">Submit Answers</button></form><div id="assessment-results" style="margin-top: 1rem; font-weight: bold;"></div>`;
            assessmentContainer.innerHTML = assessmentHTML;

            document.getElementById('assessment-form').addEventListener('submit', handleAssessmentSubmit);
        } else {
            throw new Error("No questions found in response.");
        }
    } catch (error) {
        console.error('Failed to get assessment:', error);
        assessmentContainer.innerHTML = `<h3>Error</h3><p>Sorry, I couldn't generate practice questions.</p>`;
    }
}

// Function to handle submitting the assessment
function handleAssessmentSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const resultsContainer = document.getElementById('assessment-results');
    let score = 0;
    const questionCount = form.querySelectorAll('.question-block').length;

    for (let i = 0; i < questionCount; i++) {
        const correctAnswer = document.getElementById(`answer-${i}`).value;
        const selectedOption = form.querySelector(`input[name="question-${i}"]:checked`);
        
        // Give feedback on each question
        const questionBlock = selectedOption.closest('.question-block');
        const options = questionBlock.querySelectorAll('.option');
        options.forEach(opt => {
            const label = opt.querySelector('label');
            if(label.innerText === correctAnswer) {
                label.style.color = 'green';
                label.style.fontWeight = 'bold';
            }
            if(selectedOption && label.innerText === selectedOption.value && selectedOption.value !== correctAnswer) {
                 label.style.color = 'red';
            }
        });
        
        if (selectedOption && selectedOption.value === correctAnswer) {
            score++;
        }
    }
    
    resultsContainer.innerHTML = `<h4>Your Result: ${score} out of ${questionCount}</h4>`;
}

// Function to explain selected text via the AI Assistant
function explainText(text) {
    const prompt = `Can you please explain this concept in simple terms: "${text}"`;
    addMessageToChat('user-message', prompt);
    const botMessageElem = addMessageToChat('bot-message', 'Thinking...');
    
    fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prompt })
    })
    .then(response => response.json())
    .then(data => {
        botMessageElem.textContent = data.reply;
    })
    .catch(error => {
        console.error('Explain text error:', error);
        botMessageElem.textContent = 'Sorry, an error occurred while trying to explain this.';
    });
}


// --- Helper Functions ---

// Helper to add a message to the chat window
function addMessageToChat(className, text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElem = document.createElement('div');
    messageElem.className = `message ${className}`;
    messageElem.textContent = text;
    chatMessages.appendChild(messageElem);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the latest message
    return messageElem;
}


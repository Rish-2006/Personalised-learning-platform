// Simple light/dark mode toggle
function toggleMode() {
	const body = document.body;
	if (body.classList.contains('light-mode')) {
		body.classList.remove('light-mode');
		body.classList.add('dark-mode');
	} else {
		body.classList.remove('dark-mode');
		body.classList.add('light-mode');
	}
}

// Example: Attach to a button with id 'toggleModeBtn'
// document.getElementById('toggleModeBtn').addEventListener('click', toggleMode);
// Function to handle login form submission
async function loginUser(event) {
	event.preventDefault();
	const username = document.getElementById('username').value;
	const password = document.getElementById('password').value;

	try {
		const response = await fetch('/api/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});

		if (response.ok) {
			window.location.href = 'dashboard.html';
		} else {
			const data = await response.json();
			alert(data.error || 'Login failed.');
		}
	} catch (error) {
		alert('An error occurred. Please try again.');
	}
}

// Example: Attach to form with id 'loginForm'
// document.getElementById('loginForm').addEventListener('submit', loginUser);

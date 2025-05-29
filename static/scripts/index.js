// Toggle between login and registration forms
function toggleForm(form) {
  document.getElementById('loginForm').classList.remove('active');
  document.getElementById('registerForm').classList.remove('active');

  if (form === 'login') {
    document.getElementById('loginForm').classList.add('active');
  } else {
    document.getElementById('registerForm').classList.add('active');
  }
}

// Login function
async function login() {
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;

  if (!username || !password) {
    showNotification('Please fill in both fields', true);
    return;
  }

  try {
    const response = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (response.redirected) {
      showNotification('Login successful!');
      setTimeout(() => {
        window.location.href = response.url; // Redirect after the notification disappears
      }, 3000); // Wait for 3 seconds before redirecting
    } else {
      const data = await response.json();
      if (data.error) {
        showNotification(data.error, true); // Display error message
      }
    }
  } catch (error) {
    console.error('Error:', error);
    showNotification('An error occurred during login', true);
  }
}

// Register function
async function register() {
  const username = document.getElementById('regUsername').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  const role = document.getElementById('userRole').value; // Ensure the correct ID is used

  if (!username || !email || !password || !role) {
    showNotification('Please fill in all fields', true);
    return;
  }

  try {
    const response = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role }),
    });

    const data = await response.json();
    if (response.ok) {
      showNotification('Registration successful! Redirecting to login...');
      setTimeout(() => {
        window.location.href = '/index?form=login'; // Redirect to login page after registration
      }, 3000); // Wait for the notification to disappear before redirecting
    } else {
      showNotification(data.error, true); // Display error message
    }
  } catch (error) {
    console.error('Error:', error);
    showNotification('An error occurred during registration', true);
  }
}

// Redirect to login page
function redirectToLogin() {
  toggleForm('login');
}

// Redirect to registration page
function redirectToRegister() {
  toggleForm('register');
}

function showNotification(message, isError = false) {
  const notification = document.getElementById('notification');
  notification.textContent = message;
  notification.className = 'notification'; // Reset classes
  if (isError) {
    notification.classList.add('error'); // Add error class if needed
  }
  notification.style.display = 'block'; // Show notification

  // Hide notification after 3 seconds
  setTimeout(() => {
    notification.style.display = 'none';
  }, 3000);
}
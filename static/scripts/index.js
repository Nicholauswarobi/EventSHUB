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
    alert('Please fill in both fields');
    return;
  }

  try {
    const response = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.ok) {
      alert(data.message);
      window.location.href = '/'; // Redirect to the EventHub page
    } else {
      alert(data.error);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Register function
async function register() {
  const username = document.getElementById('regUsername').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;

  if (!username || !email || !password) {
    alert('Please fill in all fields');
    return;
  }

  try {
    const response = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    const data = await response.json();
    if (response.ok) {
      alert(data.message);
      toggleForm('login'); // Switch to login form after registration
    } else {
      alert(data.error);
    }
  } catch (error) {
    console.error('Error:', error);
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
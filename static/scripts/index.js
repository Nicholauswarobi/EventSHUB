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

    if (response.redirected) {
      // Redirect to the URL provided by the backend
      window.location.href = response.url;
    } else {
      const data = await response.json();
      if (data.error) {
        alert(data.error); // Display error message
      }
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
  const role = document.getElementById('userRole').value; // Ensure the correct ID is used

  if (!username || !email || !password || !role) {
    alert('Please fill in all fields');
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
      alert(data.message);
      window.location.href = '/index?form=login'; // Redirect to login page after registration
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
// Function to open a modal by ID
function openModal(modalId) {
  document.getElementById(modalId).style.display = 'flex'; // Use 'flex' to center the modal
}

// Function to close a modal by ID
function closeModal(modalId) {
  document.getElementById(modalId).style.display = 'none';
}

// Function to switch between tabs
function openTab(event, tabId) {
  // Hide all tab contents
  const tabContents = document.querySelectorAll('.tab-content');
  tabContents.forEach(content => content.classList.remove('active'));

  // Remove active class from all tab buttons
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(button => button.classList.remove('active'));

  // Show the selected tab content and set the button as active
  document.getElementById(tabId).classList.add('active');
  event.currentTarget.classList.add('active');
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

    console.log('Response:', response); // Debugging

    if (response.redirected) {
      console.log('Redirecting to:', response.url); // Debugging
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

function toggleForm(form) {
  document.getElementById('loginForm').classList.remove('active');
  document.getElementById('registerForm').classList.remove('active');

  if (form === 'login') {
    document.getElementById('loginForm').classList.add('active');
  } else {
    document.getElementById('registerForm').classList.add('active');
  }
}

// Automatically toggle form based on query parameter
const urlParams = new URLSearchParams(window.location.search);
const formType = urlParams.get('form') || 'login';
toggleForm(formType);

// Function to handle form submission and move to the next tab
function handleFormSubmit(event, currentTabId, nextTabId, modalId) {
  event.preventDefault(); // Prevent default form submission

  // Simulate form submission (you can replace this with actual AJAX submission logic)
  console.log(`Form in ${currentTabId} submitted`);

  if (nextTabId) {
    // Move to the next tab
    openTab({ currentTarget: document.querySelector(`[onclick="openTab(event, '${nextTabId}')"]`) }, nextTabId);
  } else {
    // Close the modal if it's the last tab
    closeModal(modalId);
  }
}
# EventHub Website

Welcome to the **EventHub** website! This project is a web-based platform for managing events, venues, and user accounts. Follow the instructions below to set up and run the website locally.

---

## Features
- **Login and Registration**: Users can log in or register for an account.
- **Dynamic Navigation**: Redirects users to the main page after login or registration.
- **Responsive Design**: Optimized for various screen sizes.
- **Frontend Technologies**: HTML, CSS, and JavaScript.

---

## Prerequisites
Before running the website, ensure you have the following installed:
1. A modern web browser (e.g., Chrome, Firefox, Edge).
2. A code editor (e.g., Visual Studio Code) for editing files (optional).
3. [Live Server Extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) for Visual Studio Code (optional but recommended).

---

## Project Structure

    EventSHUB/
    │
    ├── template/
    │   ├── index.html          # Login and Registration Page
    │   ├── EventHub.html       # Main Page (redirect after login)
    │   ├── styles/
    │   │   ├── eventHub-login.css # CSS for Login and Registration Page
    │   │   └── style.css       # General Styles for the Website
    │   ├── static/
    │   ├── images/             # Images used in the website
    │   └── README.md           # Instructions for running the website

---

## Running the Website

### Option 1: Open Directly in a Web Browser
1. Navigate to the `template/` folder in your project directory.
2. Open the `index.html` file in your web browser by double-clicking it.
3. The login and registration page will load.
4. Use the login or registration form to navigate to the main page (`EventHub.html`).

---

### Option 2: Use Live Server (Recommended)
1. Open the project folder (`EventSHUB/`) in Visual Studio Code.
2. Install the **Live Server** extension if you haven't already:
   - Go to the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X` on Mac).
   - Search for "Live Server" and click **Install**.
3. Right-click on the `index.html` file in the `template/` folder.
4. Select **Open with Live Server**.
5. The website will open in your default browser at `http://127.0.0.1:5500/` or a similar address.
6. Use the login or registration form to navigate to the main page (`EventHub.html`).

---

## Notes
- The `window.location.href` in the JavaScript code redirects users to `EventHub.html` after login and `index.html` after registration. Ensure these files exist in the `template/` folder.
- If you make changes to the HTML, CSS, or JavaScript files, refresh the browser to see the updates.

---

## Troubleshooting
1. **Live Server Not Working**:
   - Ensure the Live Server extension is installed and enabled in Visual Studio Code.
   - Restart Visual Studio Code and try again.
2. **CSS Not Loading**:
   - Check the file paths in the `<link>` tag of your HTML files.
   - Ensure the `styles/` folder contains the correct CSS files.
3. **JavaScript Errors**:
   - Open the browser's developer tools (`F12` or `Ctrl+Shift+I`) and check the console for errors.

---


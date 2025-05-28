    function openModal(modalId) {
      document.getElementById(modalId).style.display = 'flex'; // Use 'flex' to center the modal
    }

    function closeModal(modalId) {
      document.getElementById(modalId).style.display = 'none';
    }

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
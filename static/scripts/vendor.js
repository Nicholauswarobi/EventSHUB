function openModal(modalId) {
  document.getElementById(modalId).style.display = 'flex'; // Center the modal
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

  // Reload dropdown data for the current tab
  reloadDropdownData(tabId);
}

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

// Function to reload dropdown data dynamically
function reloadDropdownData(tabId) {
  let url = '';

  // Determine the endpoint based on the tab
  if (tabId === 'venueTab') {
    url = '/get_locations'; // Endpoint to fetch locations
  } else if (tabId === 'eventTab') {
    url = '/get_venues_and_services'; // Endpoint to fetch venues and services
  }

  if (url) {
    fetch(url)
      .then(response => response.json())
      .then(data => {
        if (tabId === 'venueTab') {
          const locationDropdown = document.querySelector('#venueTab select[name="location_id"]');
          locationDropdown.innerHTML = '<option value="" disabled selected>Select Location</option>';
          data.locations.forEach(location => {
            locationDropdown.innerHTML += `<option value="${location.id}">${location.address}, ${location.city}</option>`;
          });
        } else if (tabId === 'eventTab') {
          const venueDropdown = document.querySelector('#eventTab select[name="event_venue_id"]');
          const serviceDropdown = document.querySelector('#eventTab select[name="event_service_id"]');
          venueDropdown.innerHTML = '<option value="" disabled selected>Select Venue</option>';
          serviceDropdown.innerHTML = '<option value="" disabled selected>Select Service (Optional)</option>';
          data.venues.forEach(venue => {
            venueDropdown.innerHTML += `<option value="${venue.id}">${venue.name}</option>`;
          });
          data.services.forEach(service => {
            serviceDropdown.innerHTML += `<option value="${service.id}">${service.name}</option>`;
          });
        }
      })
      .catch(error => console.error('Error fetching dropdown data:', error));
  }
}
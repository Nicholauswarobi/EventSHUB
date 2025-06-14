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

  const formData = new FormData(document.querySelector(`#${currentTabId} form`));

  let url = '';
  if (currentTabId === 'locationTab') {
    url = '/add_location'; // Endpoint to add location
  } else if (currentTabId === 'venueTab') {
    url = '/add_venue'; // Endpoint to add venue
  } else if (currentTabId === 'serviceTab') {
    url = '/add_service'; // Endpoint to add service
  } else if (currentTabId === 'eventTab') {
    url = '/add_event'; // Endpoint to add event
  }

  if (url) {
    fetch(url, {
      method: 'POST',
      body: formData,
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to submit form for ${currentTabId}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          console.log(`${currentTabId} submitted successfully`);
          showNotification(`${currentTabId} added successfully!`);

          if (nextTabId) {
            // Move to the next tab and reload dropdown data
            openTab({ currentTarget: document.querySelector(`[onclick="openTab(event, '${nextTabId}')"]`) }, nextTabId);
            reloadDropdownData(nextTabId); // Reload dropdown data for the next tab
          } else {
            // Close the modal if it's the last tab
            closeModal(modalId);
          }
        } else {
          console.error(`Error submitting ${currentTabId}:`, data.error);
          showNotification(`Failed to add ${currentTabId}: ${data.error}`, true);
        }
      })
      .catch(error => {
        console.error(`Error submitting ${currentTabId}:`, error);
        showNotification(`Failed to add ${currentTabId}: ${error.message}`, true);
      });
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
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to fetch data for ${tabId}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        if (tabId === 'venueTab') {
          const locationDropdown = document.querySelector('#venueTab select[name="location_id"]');
          locationDropdown.innerHTML = '<option value="" disabled selected>Select Location</option>';
          if (data.locations && data.locations.length > 0) {
            data.locations.forEach(location => {
              locationDropdown.innerHTML += `
                <option value="${location.id}">
                  ${location.street_ward}, ${location.district}, ${location.region}, ${location.country}
                </option>`;
            });
          } else {
            locationDropdown.innerHTML += '<option value="" disabled>No locations available</option>';
          }
        } else if (tabId === 'eventTab') {
          const venueDropdown = document.querySelector('#eventTab select[name="event_venue_id"]');
          const serviceDropdown = document.querySelector('#eventTab select[name="event_service_id"]');
          venueDropdown.innerHTML = '<option value="" disabled selected>Select Venue</option>';
          serviceDropdown.innerHTML = '<option value="" disabled selected>Select Service (Optional)</option>';
          if (data.venues && data.venues.length > 0) {
            data.venues.forEach(venue => {
              venueDropdown.innerHTML += `<option value="${venue.id}">${venue.name}</option>`;
            });
          } else {
            venueDropdown.innerHTML += '<option value="" disabled>No venues available</option>';
          }
          if (data.services && data.services.length > 0) {
            data.services.forEach(service => {
              serviceDropdown.innerHTML += `<option value="${service.id}">${service.name}</option>`;
            });
          } else {
            serviceDropdown.innerHTML += '<option value="" disabled>No services available</option>';
          }
        }
      })
      .catch(error => console.error(`Error fetching dropdown data for ${tabId}:`, error));
  }
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
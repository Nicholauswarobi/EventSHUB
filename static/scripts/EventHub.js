const track = document.getElementById('carouselTrack');
    const cards = document.querySelectorAll('.venue-card');
    let currentIndex = 2; // Start with the center card
    let autoSlideInterval;

    function updateCarousel() {
      cards.forEach((card, index) => {
        card.classList.remove('active', 'left', 'right', 'behind');
        if (index === currentIndex) {
          card.classList.add('active');
        } else if (index === (currentIndex - 1 + cards.length) % cards.length) {
          card.classList.add('left');
        } else if (index === (currentIndex + 1) % cards.length) {
          card.classList.add('right');
        } else {
          card.classList.add('behind');
        }
      });
    }

    function nextSlide() {
      currentIndex = (currentIndex + 1) % cards.length;
      updateCarousel();
    }

    function startAutoSlide() {
      autoSlideInterval = setInterval(nextSlide, 3000); // Auto-slide every 3 seconds
    }

    function stopAutoSlide() {
      clearInterval(autoSlideInterval);
    }

    // Start auto-slide on page load
    startAutoSlide();

    // Add event listeners to stop and resume auto-slide on hover
    cards.forEach((card) => {
      card.addEventListener('mouseenter', stopAutoSlide); // Stop sliding when pointer is over an image
      card.addEventListener('mouseleave', startAutoSlide); // Resume sliding when pointer leaves the image
    });

    updateCarousel();

    const profileImage = document.getElementById('profileImage');
    const dropdownMenu = document.getElementById('dropdownMenu');

    // Toggle dropdown visibility on profile image click
    profileImage.addEventListener('click', () => {
      const isVisible = dropdownMenu.style.display === 'block';
      dropdownMenu.style.display = isVisible ? 'none' : 'block';
    });

    // Close the dropdown when clicking outside of it
    document.addEventListener('click', (event) => {
      if (!profileImage.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.style.display = 'none';
      }
    });




// Redirect to login page
function redirectToLogin() {
  window.location.href = '/?form=login'; // Redirect to the root route with the login form
}

// Redirect to registration page
function redirectToRegister() {
  window.location.href = '/?form=register'; // Redirect to the root route with the registration form
}

// Simulate user sign-out
function signOut() {
  document.getElementById('signInButton').style.display = 'inline-block';
  document.getElementById('signUpButton').style.display = 'inline-block';
  document.getElementById('signOutButton').style.display = 'none';
  document.getElementById('profileDropdown').style.display = 'none';
}
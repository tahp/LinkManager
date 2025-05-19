// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const hamburgerButton = document.querySelector('.hamburger-menu');
    const mainNav = document.getElementById('mainNav');
    const navIcon = hamburgerButton.querySelector('i'); // Get the icon element

    if (hamburgerButton && mainNav) {
        hamburgerButton.addEventListener('click', function() {
            const isExpanded = mainNav.classList.toggle('active');
            hamburgerButton.setAttribute('aria-expanded', isExpanded);

            // Change icon based on state
            if (isExpanded) {
                navIcon.classList.remove('fa-bars');
                navIcon.classList.add('fa-times'); // Change to 'X' icon
            } else {
                navIcon.classList.remove('fa-times');
                navIcon.classList.add('fa-bars');   // Change back to hamburger icon
            }
        });

        // Optional: Close menu when a link is clicked (for SPA-like behavior or single-page feel)
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (mainNav.classList.contains('active')) {
                    mainNav.classList.remove('active');
                    hamburgerButton.setAttribute('aria-expanded', 'false');
                    navIcon.classList.remove('fa-times');
                    navIcon.classList.add('fa-bars');
                }
            });
        });

        // Optional: Close menu if clicking outside of it
        document.addEventListener('click', function(event) {
            const isClickInsideNav = mainNav.contains(event.target);
            const isClickOnHamburger = hamburgerButton.contains(event.target);

            if (!isClickInsideNav && !isClickOnHamburger && mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                hamburgerButton.setAttribute('aria-expanded', 'false');
                navIcon.classList.remove('fa-times');
                navIcon.classList.add('fa-bars');
            }
        });
    }
});


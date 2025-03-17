// Company profile functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeCompanyProfilePage();
});

function initializeCompanyProfilePage() {
    // Only run on company profile page
    if (!document.querySelector('.company-profile')) return;
    
    // Portfolio gallery
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    if (portfolioItems.length > 0) {
        portfolioItems.forEach(item => {
            item.addEventListener('click', function() {
                // Get project details
                const projectId = this.getAttribute('data-project-id');
                const projectTitle = this.querySelector('.project-title').textContent;
                const projectDescription = this.querySelector('.project-description').textContent;
                const projectImage = this.querySelector('img').getAttribute('src');
                
                // Populate modal
                const modal = document.getElementById('portfolio-modal');
                modal.querySelector('.modal-title').textContent = projectTitle;
                modal.querySelector('.modal-body-text').textContent = projectDescription;
                
                // Show the modal
                const portfolioModal = new bootstrap.Modal(modal);
                portfolioModal.show();
            });
        });
    }
    
    // Contact form validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const nameField = document.getElementById('contact-name');
            const emailField = document.getElementById('contact-email');
            const messageField = document.getElementById('contact-message');
            
            let isValid = true;
            
            if (!nameField.value.trim()) {
                isValid = false;
                nameField.classList.add('is-invalid');
            } else {
                nameField.classList.remove('is-invalid');
            }
            
            if (!emailField.value.trim() || !isValidEmail(emailField.value)) {
                isValid = false;
                emailField.classList.add('is-invalid');
            } else {
                emailField.classList.remove('is-invalid');
            }
            
            if (!messageField.value.trim()) {
                isValid = false;
                messageField.classList.add('is-invalid');
            } else {
                messageField.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                e.stopPropagation();
                displayErrorMessage('Please correct the errors in the form');
            }
        });
    }
    
    // Service selection functionality
    const serviceCards = document.querySelectorAll('.service-card');
    if (serviceCards.length > 0) {
        serviceCards.forEach(card => {
            card.addEventListener('click', function() {
                // Toggle selected class
                this.classList.toggle('selected');
                
                // Update the hidden input with selected services
                updateSelectedServices();
            });
        });
    }
}

// Helper function to validate email format
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Update selected services input
function updateSelectedServices() {
    const selectedServices = [];
    const serviceCards = document.querySelectorAll('.service-card.selected');
    
    serviceCards.forEach(card => {
        selectedServices.push(card.getAttribute('data-service-id'));
    });
    
    // Update hidden input
    const servicesInput = document.getElementById('selected-services');
    if (servicesInput) {
        servicesInput.value = selectedServices.join(',');
    }
}

// Edit profile functionality
function initializeProfileEdit() {
    const editForm = document.getElementById('profile-edit-form');
    if (!editForm) return;
    
    // Handle form submission
    editForm.addEventListener('submit', function(e) {
        // Validation is handled by Flask-WTF on the server
        // This is just for client-side validation if needed
        const nameField = document.getElementById('name');
        const descriptionField = document.getElementById('description');
        
        let isValid = true;
        
        if (!nameField.value.trim()) {
            isValid = false;
            nameField.classList.add('is-invalid');
        }
        
        if (!descriptionField.value.trim()) {
            isValid = false;
            descriptionField.classList.add('is-invalid');
        }
        
        if (!isValid) {
            e.preventDefault();
            e.stopPropagation();
            displayErrorMessage('Please correct the errors in the form');
        }
    });
}

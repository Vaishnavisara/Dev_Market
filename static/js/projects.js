// Projects page functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeProjectsPage();
});

function initializeProjectsPage() {
    // Only run on projects page
    if (!document.querySelector('.projects-container')) return;
    
    // Project filters
    const filterButtons = document.querySelectorAll('.project-filter');
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get filter value
                const filter = this.getAttribute('data-filter');
                
                // Filter projects
                const projectCards = document.querySelectorAll('.project-card');
                projectCards.forEach(card => {
                    if (filter === 'all') {
                        card.style.display = 'block';
                    } else {
                        const status = card.getAttribute('data-status');
                        if (status === filter) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    }
                });
            });
        });
    }
    
    // Project search
    const searchInput = document.getElementById('project-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            const projectCards = document.querySelectorAll('.project-card');
            projectCards.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Budget range filter
    const budgetRange = document.getElementById('budget-range');
    const budgetDisplay = document.getElementById('budget-display');
    
    if (budgetRange && budgetDisplay) {
        budgetRange.addEventListener('input', function() {
            const value = this.value;
            budgetDisplay.textContent = formatCurrency(value);
            
            // Filter projects by budget
            const projectCards = document.querySelectorAll('.project-card');
            projectCards.forEach(card => {
                const budget = parseInt(card.getAttribute('data-budget'));
                if (budget <= value) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Project creation form validation
    const projectForm = document.getElementById('project-form');
    if (projectForm) {
        projectForm.addEventListener('submit', function(e) {
            // Form validation is handled server-side with Flask-WTF
            // This is just for additional client-side validation if needed
            const titleField = document.getElementById('title');
            const descriptionField = document.getElementById('description');
            const budgetField = document.getElementById('budget');
            
            let isValid = true;
            
            if (!titleField.value.trim()) {
                isValid = false;
                // Mark field as invalid
                titleField.classList.add('is-invalid');
            }
            
            if (!descriptionField.value.trim() || descriptionField.value.length < 20) {
                isValid = false;
                // Mark field as invalid
                descriptionField.classList.add('is-invalid');
            }
            
            if (!budgetField.value || parseFloat(budgetField.value) <= 0) {
                isValid = false;
                // Mark field as invalid
                budgetField.classList.add('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                e.stopPropagation();
                displayErrorMessage('Please correct the errors in the form');
            }
        });
    }
}

// Apply to project functionality
function applyToProject(projectId) {
    // This would typically be an AJAX request in a real application
    // Here we'll just redirect to the project detail page
    window.location.href = `/projects/${projectId}`;
}

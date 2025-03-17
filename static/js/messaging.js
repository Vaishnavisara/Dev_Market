// Messaging functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeMessagesPage();
});

function initializeMessagesPage() {
    // Only run on messages page
    if (!document.querySelector('.messages-container')) return;
    
    // Toggle between sent and received messages
    const messagesTabs = document.querySelectorAll('.messages-tab');
    const messagesContent = document.querySelectorAll('.messages-content');
    
    messagesTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            messagesTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all content
            messagesContent.forEach(content => content.classList.add('d-none'));
            
            // Show the corresponding content
            const target = this.getAttribute('data-target');
            document.querySelector(target).classList.remove('d-none');
        });
    });
    
    // Message form handling
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            // Validation is handled by Flask, so we don't need to prevent the default
            // This is just for potential future client-side validation
            const recipientField = document.getElementById('recipient');
            const contentField = document.getElementById('content');
            
            if (!recipientField.value.trim()) {
                e.preventDefault();
                displayErrorMessage('Please enter a recipient username');
                return false;
            }
            
            if (!contentField.value.trim()) {
                e.preventDefault();
                displayErrorMessage('Please enter a message');
                return false;
            }
        });
    }
    
    // Initialize message reply functionality
    const replyButtons = document.querySelectorAll('.reply-button');
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const username = this.getAttribute('data-username');
            const recipientField = document.getElementById('recipient');
            
            if (recipientField) {
                recipientField.value = username;
                // Focus on the message content field
                document.getElementById('content').focus();
                
                // Scroll to the form
                document.getElementById('message-form').scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Mark messages as read when viewed
    const unreadMessages = document.querySelectorAll('.message.unread');
    if (unreadMessages.length > 0) {
        // In a real application, you'd make an AJAX call to mark messages as read
        console.log('Would mark messages as read here');
    }
}

// Format timestamp for messages
function formatMessageTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    
    // If the message is from today, just show the time
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // If the message is from this year, show month and day
    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    
    // Otherwise show full date
    return date.toLocaleDateString();
}

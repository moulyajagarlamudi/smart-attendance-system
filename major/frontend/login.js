// Simple login functionality for the admin login page
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const captchaLabel = document.getElementById('captchaLabel');
    const captchaInput = document.getElementById('captchaInput');

    // Generate captcha
    function generateCaptcha() {
        const num1 = Math.floor(Math.random() * 10) + 1;
        const num2 = Math.floor(Math.random() * 10) + 1;
        const answer = num1 + num2;
        captchaLabel.textContent = `Captcha: ${num1} + ${num2} = ?`;
        captchaInput.setAttribute('data-answer', answer);
    }

    // Initialize captcha
    generateCaptcha();

    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const role = document.getElementById('role').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const captchaAnswer = captchaInput.value;
        const correctAnswer = captchaInput.getAttribute('data-answer');

        // Validate captcha
        if (captchaAnswer !== correctAnswer) {
            showError('Incorrect captcha answer. Please try again.');
            generateCaptcha();
            captchaInput.value = '';
            return;
        }

        // Simple validation
        if (!role || !username || !password) {
            showError('Please fill in all fields.');
            return;
        }

        // Redirect based on role
        switch(role) {
            case 'admin':
                window.location.href = 'admin_dashboard.html';
                break;
            case 'hod':
                window.location.href = 'hod_dashboard.html';
                break;
            case 'dean':
                window.location.href = 'dean_dashboard.html';
                break;
            default:
                showError('Invalid role selected.');
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 3000);
    }
}); 
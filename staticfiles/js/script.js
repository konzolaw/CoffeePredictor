const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const signUpLink = document.getElementById('signUpLink');
const signInLink = document.getElementById('signInLink');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

signUpLink.addEventListener('click', (e) => {
    e.preventDefault();
    container.classList.add("right-panel-active");
});

signInLink.addEventListener('click', (e) => {
    e.preventDefault();
    container.classList.remove("right-panel-active");
});

document.getElementById("farm-form").addEventListener("submit", function (e) {
  e.preventDefault();
  alert("Prediction request submitted!");
});

document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.messages .message');
    messages.forEach(message => {
        const popup = document.createElement('div');
        popup.className = 'popup-message';
        popup.textContent = message.textContent;
        document.body.appendChild(popup);

        // Remove the popup after 10 seconds
        setTimeout(() => {
            popup.remove();
        }, 10000);
    });
});

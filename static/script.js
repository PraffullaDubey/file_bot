function appendMessage(message, sender = 'bot') {
    const chat = document.getElementById('chat');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender;
    messageDiv.textContent = message;
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;
    appendMessage("You: " + message, 'user');

    fetch('/message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.response, 'bot');
        input.value = '';
    });
}

function sendQuickCommand(command) {
    fetch('/message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: command})
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.response, 'bot');
    });
}

// Greet immediately when page loads
window.onload = function() {
    fetch('/message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: ''})
    })
    .then(response => response.json())
    .then(data => {
        appendMessage(data.response, 'bot');
    });
};

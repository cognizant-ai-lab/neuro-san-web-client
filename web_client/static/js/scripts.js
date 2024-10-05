document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messages = document.getElementById('messages');
    const agentLogs = document.getElementById('agent-logs');
    const loadingIndicator = document.getElementById('loading-indicator');

    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    socket.on('agent_log', function(data) {
        agentLogs.textContent += data.log + '\n';
        agentLogs.scrollTop = agentLogs.scrollHeight;
    });

    socket.on('agent_response', function(data) {
        console.log('Received agent response:', data);
        appendMessage('agent-response', data.message);
        // Hide loading indicator if you have one
        loadingIndicator.style.display = 'none';
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            socket.emit('user_input', {'message': message});
            appendMessage('user-message', message);
            userInput.value = '';
            // Show loading indicator
            loadingIndicator.style.display = 'block';
        }
    }

    // Function to render text with newlines properly
    function renderTextWithNewlines(text) {
        // Replace \n with <br> for new lines
        return text.replace(/\\n/g, '<br>');
    }

     function appendMessage(type, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (type === 'agent-response') {
            // Render the message as HTML using Marked.js and sanitize it with DOMPurify
            const rawHTML = marked.parse(renderTextWithNewlines(message));
            const sanitizedHTML = DOMPurify.sanitize(rawHTML);
            messageContent.innerHTML = sanitizedHTML;
        } else {
            messageContent.textContent = message;
        }

        messageElement.appendChild(messageContent);
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;
    }

});

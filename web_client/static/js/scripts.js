document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messages = document.getElementById('messages');
    const agentLogs = document.getElementById('agent-logs');
    const loadingIndicator = document.getElementById('loading-indicator');
    const configForm = document.querySelector('#configForm form');
    const agentNameInput = configForm.querySelector('input[name="agent_name"]');
    const hostInput = configForm.querySelector('input[name="host"]');
    const portInput = configForm.querySelector('input[name="port"]');

    sendButton.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function highlightAgentInGraph(agentName) {
        const iframe = document.getElementById('diagram-frame');
        if (iframe) {
//            console.log(`Sending message to iframe: ${agentName}`);  // Log the agent name before sending
            iframe.contentWindow.postMessage({ agentName: agentName }, '*');  // Do NOT modify the agentName here
        }
    }

    socket.on('agent_log', function(data) {
        agentLogs.textContent += data.log + '\n';
        agentLogs.scrollTop = agentLogs.scrollHeight;

        // Extract the full agent name before "CALLED" or "RETURNED" using a more precise regex
        const log = data.log;
        const agentRegex = /([A-Za-z_]+) (?:CALLED|RETURNED)/;  // Regex to match agent names before "CALLED" or "RETURNED"
        const match = log.match(agentRegex);

        if (match && match[1]) {
            const agentName = match[1].toLowerCase();  // Only lowercase the agent name
//            console.log(`Extracted agent name: ${agentName}`);  // Debugging log to check the extracted agent name
            highlightAgentInGraph(agentName);  // Send the agent name to be highlighted
        }
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

    const detailsElement = document.querySelector('details');
    const diagramFrame = document.getElementById('diagram-frame');
    let centered = false;  // Flag to track if the diagram has been centered

    // Listen for the toggle event when details is opened
    detailsElement.addEventListener('toggle', function() {
        if (this.open && !centered) {
            // Trigger re-centering logic after details is opened, but only if not centered already
            triggerResizeEvent();
            centered = true;  // Set flag to true to prevent further centering
        }
    });

    function triggerResizeEvent() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));  // Trigger a resize event after details opens
        }, 100);  // Delay ensures that the content is fully rendered before triggering the resize
    }

    // On iframe load, also trigger re-centering if details is already open
    diagramFrame.onload = function() {
        if (detailsElement.open && !centered) {
            triggerResizeEvent();
            centered = true;  // Set flag to true to prevent further centering
        }
    };

    function loadDiagram(agentNetworkName) {
        centered = false;  // Reset the flag when loading a new diagram
        if (agentNetworkName) {
            diagramFrame.src = `/static/${agentNetworkName}.html`;
        } else {
            diagramFrame.src = '';  // Clear iframe
        }
    }
    // On form submission, load the respective diagram
    configForm.addEventListener('submit', (event) => {
        const agentNetworkName = agentNameInput.value.trim();
        loadDiagram(agentNetworkName);  // Load the corresponding diagram
    });

    // Optionally, you can load the diagram when the page loads, based on the current agent_name
    const initialAgentName = agentNameInput.value.trim();
    loadDiagram(initialAgentName);  // Load the initial diagram if there is an agent network name

});

window.addEventListener('resize', function() {
    const diagramFrame = document.getElementById('diagram-frame');
    // Trigger resizing or reloading the content if needed
    diagramFrame.contentWindow.location.reload();  // Reloads the diagram when window is resized
});

function resizeDiagramFrame() {
    const diagramFrame = document.getElementById('diagram-frame');
    if (diagramFrame) {
        diagramFrame.contentWindow.location.reload();  // Trigger a reload to adjust layout
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const diagramDetails = document.querySelector('details[open]'); // If it's open on page load
    if (diagramDetails) {
        resizeDiagramFrame();  // Resize on load if the diagram is visible
    }
});

const detailsElements = document.querySelectorAll('details');
detailsElements.forEach((details) => {
    details.addEventListener('toggle', function() {
        if (details.open) {
            resizeDiagramFrame();  // Resize when the diagram becomes visible
        }
    });
});



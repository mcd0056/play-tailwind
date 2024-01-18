// Function to stream a message in the chat screen, simulating typing
function streamMessage(message, className) {
    if (!message) {
        console.error('Error: Message is undefined or null');
        return; // Do not proceed if the message is not valid
    }

    const chatScreen = document.getElementById('chat-screen');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${className}`;
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';

    const avatarSrc = className === 'user-message' ? "/static/icons/user-avatar.png" : "/static/icons/bot-avatar.png";
    const avatarAlt = className === 'user-message' ? "User" : "Bot";
    const avatar = document.createElement('img');
    avatar.src = avatarSrc;
    avatar.alt = avatarAlt;
    avatar.className = "avatar";

    if (className === 'user-message') {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageBubble);
    } else {
        messageDiv.appendChild(messageBubble);
        messageDiv.appendChild(avatar);
    }

    chatScreen.appendChild(messageDiv);
    

    // Ensure the DOM has been updated before starting the typing effect
    setTimeout(() => typeMessage(message, messageBubble), 0);
    scrollToBottom();
}

// Function to simulate the typing effect
function typeMessage(message, element) {
    let i = 0;
    const typingSpeed = 2; // Set the typing speed (in milliseconds)

    function typing() {
        if (i < message.length) {
            element.textContent += message.charAt(i);
            i++;
            scrollToBottom();
            setTimeout(typing, typingSpeed);
        }
    }
    typing();
}

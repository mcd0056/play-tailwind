const chatMessages = document.querySelector('.chat-messages');
const chatMessagesContent = document.querySelector('.chat-messages-content');
const chatForm = document.querySelector('.chat-form');

function init() {
  const lastEl = chatMessagesContent.lastElementChild;
  chatMessages.scrollTo(0, lastEl.offsetTop);
}

function onChatSubmit(evt) {
  evt.preventDefault();
  const inputField = document.querySelector('.chat-form-input');
  const userMessage = inputField.value;

  // Send message to server and handle response
  fetch('YOUR_API_ENDPOINT', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage })
  })
  .then(response => response.json())
  .then(data => {
      // Append user message and bot response to chat
      appendMessage(userMessage, 'right');
      appendMessage(data.botResponse, 'left');
  })
  .catch(error => console.error('Error:', error));

  // Clear input field
  inputField.value = '';
}

function appendMessage(message, side) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('chat-message', `-${side}`);
  messageElement.innerHTML = `
      <div class="chat-message-text">${message}</div>
  `;
  chatMessagesContent.appendChild(messageElement);
  chatMessages.scrollTo(0, chatMessages.scrollHeight);
}


init();

chatForm.addEventListener('submit', onChatSubmit);
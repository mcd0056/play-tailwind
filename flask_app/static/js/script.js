
// When the page is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    fetchUsername();
    setupInitialChatbotView();
    
    var modal = document.getElementById("persona-modal");
    var btn = document.querySelector(".chatbot-persona .icon-button");
    var span = document.getElementsByClassName("close")[0];

    btn.onclick = function() { modal.style.display = "block"; }
    span.onclick = function() { modal.style.display = "none"; }
    window.onclick = function(event) {
        if (event.target == modal) { modal.style.display = "none"; }
    }

    // Send button event listener
    document.getElementById('send-button').addEventListener('click', function() {
        const inputElement = document.getElementById('chat-input');
        const message = inputElement.value.trim();
        if (message) {
            inputElement.value = ''; 
            displayMessage(message, 'user-message');
            fetchChatbotResponse(message);
        }
    });

    
});




// Function to Load Conversations
function loadConversations() {
    fetch('/get-conversations')
        .then(response => response.json())
        .then(conversations => {
            const conversationsContainer = document.getElementById('saved-conversations');
            conversationsContainer.innerHTML = ''; 

            conversations.forEach(conv => {
                const convElement = document.createElement('div');
                convElement.className = 'conversation-item';
                convElement.innerHTML = `
                    <div class="conversation-snippet">
                        <p>Message: ${conv.message}</p>
                        <p>Response: ${conv.response}</p>
                    </div>
                    <button onclick="deleteConversation(${conv.id})" class="icon-button delete-conversation">
                        <img src="/static/icons/delete.png" alt="Delete">
                    </button>
                `;
                conversationsContainer.appendChild(convElement);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to Delete a Conversation
function deleteConversation(convId) {
    fetch('/delete-conversation/' + convId, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Conversation deleted successfully');
                loadConversations(); 
            } else {
                console.error('Failed to delete conversation');
            }
        })
        .catch(error => console.error('Error:', error));
}

// Function to Fetch Username
function fetchUsername() {
    fetch('/get-username')
        .then(response => response.json())
        .then(data => {
            document.getElementById('user-name').textContent = data.email;
        })
        .catch(error => console.error('Error:', error));
}

// Function for Chatbot Response
function fetchChatbotResponse(message) {
    const selectedBotId = document.getElementById('chatbot-select').value;
    const chatbot = chatbotsData.find(bot => bot.id === selectedBotId);

    if (chatbot && chatbot.id === 'chatbot-vision') {
        sendVisionChatbotRequest(message);
    } else if (chatbot && chatbot.id === 'chatbot-2') {
        sendGPT3Request(message);
    } else if (chatbot && chatbot.id === 'chatbot-4') {
        sendGPT4Request(message);
    }
    else if (chatbot && chatbot.id === 'chatbot-7') {
        sendGPT16kRequest(message);    
    } else {
        const endpoint = chatbot ? chatbot.endpoint : '/chatbot-response';

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if(data && typeof data.response === 'string') {
                const responseText = data.response;
                streamMessage(responseText, 'bot-message');
            } else {
                console.error('Error: Response data is not in expected format', data);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Function to Send Request to GPT-4 Backend
function sendGPT4Request(message) {
    const promptType = document.getElementById('system-prompt-select').value;
    const promptText = document.getElementById('system-prompt-select').options[document.getElementById('system-prompt-select').selectedIndex].text;
    
    fetch('/gpt4', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_type: promptType, user_message: message, system_prompt: promptText })
    })
    .then(response => response.json())
    .then(data => {
        if (data && typeof data.response === 'string') {
            const responseText = data.response;
            streamMessage(responseText, 'bot-message');
        } else {
            console.error('Error: Response data is not in expected format', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to Send Request to GPT-3.5 Turbo Backend
function sendGPT3Request(message) {
    const promptType = document.getElementById('system-prompt-select').value;
    const promptText = document.getElementById('system-prompt-select').options[document.getElementById('system-prompt-select').selectedIndex].text;

    // Convert settings to their appropriate types
    const requestBody = {
        prompt_type: promptType,
        user_message: message,
        system_prompt: promptText,
        max_tokens: parseInt(maxTokens, 10),        // Convert to integer
        presence_penalty: parseFloat(presencePenalty),  // Convert to float
        temperature: parseFloat(temperature),    // Convert to float
        top_p: parseFloat(topP)                  // Convert to float
    };

    fetch('/chat_three', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data && typeof data.response === 'string') {
            const responseText = data.response;
            streamMessage(responseText, 'bot-message');
        } else {
            console.error('Error: Response data is not in expected format', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Funtion for Chat gpt3_5_1106 
function sendGPT3_5_turbo_1106Request(message) {
    const promptType = document.getElementById('system-prompt-select').value;
    const promptText = document.getElementById('system-prompt-select').options[document.getElementById('system-prompt-select').selectedIndex].text;

    // Convert settings to their appropriate types
    const requestBody = {
        prompt_type: promptType,
        user_message: message,
        system_prompt: promptText,
        max_tokens: parseInt(maxTokens, 10),        // Convert to integer
        presence_penalty: parseFloat(presencePenalty),  // Convert to float
        temperature: parseFloat(temperature),    // Convert to float
        top_p: parseFloat(topP)                  // Convert to float
    };

    fetch('/gpt3_5_1106', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data && typeof data.response === 'string') {
            const responseText = data.response;
            streamMessage(responseText, 'bot-message');
        } else {
            console.error('Error: Response data is not in expected format', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to Send Request to GPT-3.5 16K
function sendGPT16kRequest(message) {
    const promptType = document.getElementById('system-prompt-select').value;
    const promptText = document.getElementById('system-prompt-select').options[document.getElementById('system-prompt-select').selectedIndex].text;

    // Convert settings to their appropriate types
    const requestBody = {
        prompt_type: promptType,
        user_message: message,
        system_prompt: promptText,
        max_tokens: parseInt(maxTokens, 10),        // Convert to integer
        presence_penalty: parseFloat(presencePenalty),  // Convert to float
        temperature: parseFloat(temperature),    // Convert to float
        top_p: parseFloat(topP)                  // Convert to float
    };

    fetch('/gpt16k', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        if (data && typeof data.response === 'string') {
            const responseText = data.response;
            streamMessage(responseText, 'bot-message');
        } else {
            console.error('Error: Response data is not in expected format', data);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to Send Request to Vision Chatbot
function sendVisionChatbotRequest(message) {
    if (!window.uploadedFile) {
        console.error('No file uploaded for Vision Chatbot');
        return;
    }

    let formData = new FormData();
    formData.append('file', window.uploadedFile);
    formData.append('prompt', message);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received data:', data); // Debugging: Log the entire response

        // Check if the response has choices and a message
        if (data.choices && data.choices.length > 0 && 'message' in data.choices[0]) {
            const chatbotResponseText = data.choices[0].message.content;
            console.log('Chatbot response text:', chatbotResponseText); 
            streamMessage(chatbotResponseText, 'bot-message');
        } else {
            console.error('Unexpected response format', data);
        }
    })
    .catch(error => {
        console.error('Error during upload', error);
    });
}

function displayMessage(message, className) {
    const chatScreen = document.getElementById('chat-screen');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${className}`;

    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    messageBubble.textContent = message;

    // Create an avatar element
    const avatar = document.createElement('img');
    avatar.className = "avatar";

    if (className === 'user-message') {
        // Set user avatar and order
        avatar.src = "/static/icons/user-avatar.png";
        avatar.alt = "User";
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageBubble);
    } else {
        // Set bot avatar and order
        avatar.src = "/static/icons/bot-avatar.png";
        avatar.alt = "Bot";
        messageDiv.appendChild(messageBubble);
        messageDiv.appendChild(avatar);
    }

    chatScreen.appendChild(messageDiv);
    scrollToBottom();
}

// Function to scroll to the bottom of the chat screen
function scrollToBottom() {
    const chatScreen = document.getElementById('chat-screen');
    chatScreen.scrollTop = chatScreen.scrollHeight;
}

document.getElementById('chatbot-select').addEventListener('change', function() {
    const selectedBotId = this.value;
    const selectedBotData = chatbotsData.find(bot => bot.id === selectedBotId);

    if (selectedBotData) {
        updateChatContainer(selectedBotData);
    }
});

function updateChatContainer(botData) {
    const chatScreen = document.getElementById('chat-screen');
    const imagePreviewContainer = document.getElementById('image-preview-container');

    // Clear chat screen but preserve image preview container
    chatScreen.innerHTML = '';
    chatScreen.appendChild(imagePreviewContainer);

    // Add bot data to chat screen
    const botInfoDiv = document.createElement('div');
    botInfoDiv.className = 'chatbot-info';
    botInfoDiv.innerHTML = `
        <img src="${botData.photo}" alt="${botData.title}" class="chatbot-photo">
        <h2>${botData.title}</h2>
        <p>${botData.description}</p>
    `;
    chatScreen.appendChild(botInfoDiv);

    const welcomeMessageDiv = document.createElement('div');
    welcomeMessageDiv.className = 'welcome-message-frame';
    welcomeMessageDiv.innerHTML = botData.welcomeMessage;
    chatScreen.appendChild(welcomeMessageDiv);
}

// Function to start a new chat
function startNewChat() {
    // Clear the chat screen and input field
    document.getElementById('chat-screen').innerHTML = '';
    document.getElementById('chat-input').value = '';
}

// Allowed file extensions
const ALLOWED_EXTENSIONS = new Set(['png', 'jpg', 'jpeg', 'gif']);

// Function to handle file upload and display the image in chat
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && allowedFile(file.name)) {
        window.uploadedFile = file;

        const reader = new FileReader();
        reader.onload = function(e) {
            const chatScreen = document.getElementById('chat-screen');

            // Hide bot info
            const botInfo = document.querySelector('.chatbot-info');
            if (botInfo) {
                botInfo.style.display = 'none';
            }

            // Create or get the image preview container
            let imgPreviewContainer = document.getElementById('image-preview-container');
            if (!imgPreviewContainer) {
                imgPreviewContainer = document.createElement('div');
                imgPreviewContainer.id = 'image-preview-container';
                chatScreen.insertBefore(imgPreviewContainer, chatScreen.firstChild);
            }

            // Clear previous content and add new image and label
            imgPreviewContainer.innerHTML = `
                <div class="image-frame">
                    <img src="${e.target.result}" alt="Uploaded Image">
                    <div class="image-label">Uploaded Image</div>
                </div>
            `;

            scrollToBottom();
        };
        reader.readAsDataURL(file);
    }
}

// Function to check if the file is allowed
function allowedFile(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ALLOWED_EXTENSIONS.has(ext);
}

document.querySelector('.file-upload-button input[type="file"]').addEventListener('change', handleFileUpload);

function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    var collapseButton = document.getElementById('toggle-sidebar'); // Button to collapse the sidebar
    var expandButton = document.getElementById('toggle-sidebar-expand'); // Button to expand the sidebar

    sidebar.classList.toggle('collapsed');

    // If the sidebar is collapsed, hide the collapse button and show the expand button
    if (sidebar.classList.contains('collapsed')) {
        collapseButton.style.display = 'none';
        expandButton.style.display = 'block';
    } else {
        collapseButton.style.display = 'block';
        expandButton.style.display = 'none';
    }
}

// Add to your existing JavaScript file
function toggleRightSidebar() {
    var rightSidebar = document.getElementById('right-sidebar');
    rightSidebar.classList.toggle('open');
}



// DALLE 3 Generate IMAGE
function generateImage() {
    var prompt = document.getElementById('dalle-prompt').value;
    var size = "1024x1024"; // Set this based on your UI or requirements
    var quality = "standard"; // Set this based on your UI or requirements
    var n = 1; // Number of images to generate

    fetch('/generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt, size: size, quality: quality, n: n })
    })
    .then(response => response.json())
    .then(data => {
        if (data && data.message === 'Image saved successfully') {
            console.log('Image generated and saved successfully');
            fetchLatestGeneratedImage(); // Fetch and display the latest generated image
        } else if (data && data.error) {
            console.error('Error:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function fetchLatestGeneratedImage() {
    fetch('/fetch-user-images')
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                const latestImage = data.images[data.images.length - 1]; // Assuming the latest image is the last one in the array
                displayGeneratedImage(`data:image/jpeg;base64,${latestImage.image_data}`);
            } else {
                console.log('No images found for user');
            }
        })
        .catch(error => console.error('Error fetching images:', error));
}

function displayGeneratedImage(imageData) {
    var outputContainer = document.getElementById('dalle-output');
    outputContainer.innerHTML = ''; // Clear previous images

    var img = document.createElement('img');
    img.src = imageData;
    img.alt = 'Generated Image';
    img.className = 'generated-image'; // Add a class for styling if needed

    outputContainer.appendChild(img);
}

document.getElementById('generate-image').addEventListener('click', generateImage);



function handleDelete(imageId) {
    fetch(`/delete-image/${imageId}`, { 
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Image deleted successfully');
            // Remove the image container from the DOM
            const imageContainer = document.getElementById(`image-container-${imageId}`);
            if(imageContainer) {
                imageContainer.remove();
            }
        } else {
            console.error('Failed to delete image:', data.error);
        }
    })
    .catch(error => console.error('Error deleting image:', error));
}

function handleDownload(imageData, imageName) {
    const link = document.createElement('a');
    link.href = imageData;
    link.download = imageName || 'download.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function fetchAndDisplayImages() {
    fetch('/fetch-user-images')
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                const imageGrid = document.querySelector('.image-grid');
                imageGrid.innerHTML = ''; // Clear existing items

                data.images.forEach((image, index) => {
                    const imageContainer = document.createElement('div');
                    imageContainer.className = 'image-container';
                    imageContainer.id = `image-container-${index}`; // Unique ID for the container

                    const img = document.createElement('img');
                    img.src = `data:image/jpeg;base64,${image.image_data}`;
                    img.alt = image.prompt;

                    const iconsContainer = document.createElement('div');
                    iconsContainer.className = 'image-action-icons';

                    const imageId = image.id; // Make sure this is the actual ID from the database
                    imageContainer.dataset.imageId = imageId; // Store the image ID in a data attribute

                    const deleteButton = document.createElement('button');
                    deleteButton.className = 'image-action-icon delete-icon';
                    deleteButton.innerHTML = `<img src="/static/icons/trash.png" alt="Delete">`;
                    deleteButton.onclick = () => handleDelete(imageId);

                    const downloadButton = document.createElement('button');
                    downloadButton.className = 'image-action-icon download-icon';
                    downloadButton.innerHTML = `<img src="/static/icons/download.png" alt="Download">`;
                    downloadButton.onclick = () => handleDownload(`data:image/jpeg;base64,${image.image_data}`, `image-${index}.png`);

                    iconsContainer.appendChild(deleteButton);
                    iconsContainer.appendChild(downloadButton);

                    imageContainer.appendChild(img);
                    imageContainer.appendChild(iconsContainer);

                    imageGrid.appendChild(imageContainer);
                });
            } else {
                console.log('No images found for user');
            }
        })
        .catch(error => console.error('Error fetching images:', error));
}





document.addEventListener('DOMContentLoaded', function() {
    fetchPrompts();

    function fetchPrompts() {
        fetch('/get-prompts-data')
            .then(response => response.json())
            .then(data => populateDropdown(data))
            .catch(error => console.error('Error:', error));
    }

    function populateDropdown(prompts) {
        const dropdown = document.getElementById('system-prompt-select');
        prompts.forEach(prompt => {
            let option = document.createElement('option');
            option.value = prompt.act;
            option.text = prompt.prompt;
            dropdown.appendChild(option);
        });
    }
});


function setupInitialChatbotView() {
    // Assuming the first chatbot in your chatbotsData array is the default
    const defaultChatbotData = chatbotsData[0];
    updateChatContainer(defaultChatbotData);
}


document.getElementById('system-prompt-select').addEventListener('change', function() {
    const selectedPromptText = this.options[this.selectedIndex].text;
    displayPromptInChat(selectedPromptText);
});

function displayPromptInChat(promptText) {
    const chatScreen = document.getElementById('chat-screen');
    const existingPrompt = chatScreen.querySelector('.system-prompt-display');

    // Remove existing prompt if it exists
    if (existingPrompt) {
        chatScreen.removeChild(existingPrompt);
    }

    const promptDiv = document.createElement('div');
    promptDiv.className = 'chat-message system-prompt-display'; // Class for styling and identification
    promptDiv.textContent = promptText;

    chatScreen.appendChild(promptDiv);
    scrollToBottom();
}

let currentAssistantId = null; // Global variable to store the current assistant's ID
let currentAssistantName = null; // Global variable to store the current assistant's name

document.addEventListener('DOMContentLoaded', function() {
    fetchAssistants();

    function fetchAssistants() {
        fetch('/list-assistants')
            .then(response => response.json())
            .then(assistantsData => {
                displayAssistants(assistantsData);
            })
            .catch(error => console.error('Error fetching assistants:', error));
    }

    function displayAssistants(assistantsData) {
        const grid = document.querySelector('.assistants-grid');
        grid.innerHTML = ''; // Clear existing content
    
        assistantsData.forEach(assistant => {
            const assistantDiv = document.createElement('div');
            assistantDiv.className = 'assistant-item';
            assistantDiv.innerHTML = `
                <div class="assistant-info">
                    <h2 class="assistant-name">${assistant.name}</h2>
                    <p class="assistant-model">${assistant.model || 'No description'}</p>
                    <p class="assistant-created-at">Created at: ${new Date(assistant.created_at * 1000).toLocaleDateString()}</p>
                    <button class="use-assistant-btn" onclick="useAssistant('${assistant.id}', '${assistant.name}', '${assistant.instructions}', 'static/path_to_assistant_image.jpg')">Use</button>
                </div>
            `;
            grid.appendChild(assistantDiv);
        });
    }

    window.useAssistant = function(assistantId, assistantName) {
        console.log('Using assistant with ID:', assistantId);
        currentAssistantId = assistantId; // Store the assistant ID in the global variable
    
        // Define the static image URL and welcome message
        const staticImageUrl = '/static/icons/chat.png'; // Update with the correct path
        const welcomeMessage = 'Welcome to the Assistant Chat!'; // Customize as needed
    
        // Populate assistant details in the chat container
        const assistantChatScreen = document.getElementById('assistant-chat-screen');
        assistantChatScreen.innerHTML = `
            <div class="assistant-details">
                <img src="${staticImageUrl}" alt="Assistant Image" class="assistant-image">
                <h2>${assistantName}</h2>
                <p>ID: ${assistantId}</p>
            </div>
            <div class="welcome-message">${welcomeMessage}</div>
            <!-- Chat messages will be appended here -->
        `;
    
        // Show assistant chat container and hide other containers
        setContainerVisibility('assistants-container', false);
        setContainerVisibility('assistant-chat-container', true);
    };
});


function showToast(message) {
    var toast = document.getElementById("toast");
    toast.className = "show";
    toast.innerHTML = message;
    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
}

function saveApiKey() {
    var apiKey = document.getElementById('api-key').value;
    if (!apiKey) {
        showToast('Please enter the API key.');
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/update-api-key', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            showToast('API Key updated successfully!');
        } else if (this.readyState === XMLHttpRequest.DONE) {
            showToast('Failed to update API Key. Error: ' + this.responseText);
        }
    };
    xhr.send(JSON.stringify({ api_key: apiKey }));
}

function openSettingsModal() {
    document.getElementById('openai-settings-modal').style.display = 'block';
}

function closeSettingsModal() {
    document.getElementById('openai-settings-modal').style.display = 'none';
    document.getElementById('')
}

function saveSettings() {
    // Add logic to save other settings here
    closeSettingsModal();
}

document.getElementById('settings-butt').addEventListener('click', openSettingsModal);

document.getElementById('logout-butt').addEventListener('click', function() {
    window.location.href = '/login'; // Redirect to the logout endpoint
});

// Declare variables to store settings
let maxTokens, presencePenalty, temperature, topP;

function saveSettings() {
    // Retrieve and store the values from the sliders
    maxTokens = document.getElementById('max-tokens').value;
    presencePenalty = document.getElementById('presence-penalty').value;
    temperature = document.getElementById('temperature').value;
    topP = document.getElementById('top-p').value;

    // Add logic to save other settings here

    closeSettingsModal();
}

document.addEventListener('DOMContentLoaded', function() {
    var chatInput = document.getElementById('chat-input');
    var sendButton = document.getElementById('send-button');
    

    chatInput.addEventListener('keydown', function(event) {
        // Check if the Enter key is pressed
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action (new line)
            sendButton.click();
            
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var chatInput = document.getElementById('assistant-chat-input');
    var sendButton = document.getElementById('assistant-send-button');
    

    chatInput.addEventListener('keydown', function(event) {
        // Check if the Enter key is pressed
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action (new line)
            sendButton.click();
            
        }
    });
});


function sendAssistantMessage() {
    const messageInput = document.getElementById('assistant-chat-input');
    const message = messageInput.value.trim();
    if (message) {
        messageInput.value = '';
        displayAssistantMessage(message, 'user-message');
        fetchAssistantResponse(message);
    }
}

function displayAssistantMessage(message, className) {
    const chatScreen = document.getElementById('assistant-chat-screen');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${className}`;

    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    messageBubble.textContent = message;

    const avatar = document.createElement('img');
    avatar.className = "avatar";

    if (className === 'user-message') {
        avatar.src = "/static/icons/user-avatar.png";
        avatar.alt = "User";
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageBubble);
    } else {
        avatar.src = "/static/icons/bot-avatar.png";
        avatar.alt = "Bot";
        messageDiv.appendChild(messageBubble);
        messageDiv.appendChild(avatar);
    }

    chatScreen.appendChild(messageDiv);
    chatScreen.scrollTop = chatScreen.scrollHeight;
}


function fetchAssistantResponse(message) {
    // Use the global variable 'currentAssistantId' to get the assistant ID
    const assistantId = currentAssistantId;
    
    if (!assistantId) {
        console.error('Error: No assistant ID found');
        return;
    }

    fetch('/webchat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assistant_id: assistantId, message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data && typeof data.response === 'string') {
            displayAssistantMessage(data.response, 'bot-message');
        } else {
            console.error('Error: Response data is not in expected format', data);
        }
    })
    .catch(error => console.error('Error:', error));
}


document.getElementById('assistant-send-button').addEventListener('click', sendAssistantMessage);
document.getElementById('assistant-chat-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendAssistantMessage();
    }
});
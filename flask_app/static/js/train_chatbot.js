document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('train-chatbot-form').addEventListener('submit', function(event) {
        event.preventDefault();
        trainChatbot();
    });

    document.getElementById('training-files').addEventListener('change', function() {
        displayUploadedFiles();
    });

    // Close modal event listener
    var personaModalCloseButton = document.getElementById('persona-modal-close');
    if (personaModalCloseButton) {
        personaModalCloseButton.addEventListener('click', closePersonaModal);
    }
});

function closePersonaModal() {
    document.getElementById('persona-modal').style.display = 'none';
}

function trainChatbot() {
    var formElement = document.getElementById('train-chatbot-form');
    var formData = new FormData(formElement);

    var selectedTools = [];
    document.querySelectorAll('input[name="tools_list"]:checked').forEach(function(checkbox) {
        selectedTools.push(checkbox.value);
    });
    formData.set('selected_tools', selectedTools.join(','));

    fetch('/create_assistant', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
    console.log('Assistant created:', data);
    var chatbotSelect = document.getElementById('chatbot-select');
    var newOption = new Option(document.getElementById('chatbot-name').value, data.assistant_id);
    chatbotSelect.add(newOption);
    showToast('Assistant created successfully.'); // Display the toast
    })
    .catch(error => {
        console.error('Error creating assistant:', error);
    });
}

function displayUploadedFiles() {
    var input = document.getElementById('training-files');
    var fileListContainer = document.getElementById('file-list');
    fileListContainer.innerHTML = '';

    for (var i = 0; i < input.files.length; i++) {
        var fileDiv = document.createElement('div');
        fileDiv.textContent = input.files[i].name;
        fileListContainer.appendChild(fileDiv);
    }
}

function showToast(message, duration = 3000) {
    var toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Make the toast visible
    setTimeout(function() {
        toast.classList.add('visible');
    }, 100);

    // Hide and remove the toast after 'duration'
    setTimeout(function() {
        toast.classList.remove('visible');
        setTimeout(function() {
            document.body.removeChild(toast);
        }, 300); // corresponds to the transition duration
    }, duration);
}


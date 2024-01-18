document.addEventListener('DOMContentLoaded', function () {
    // Initialize the UI with only the chat container visible
    initializeUI();
    
    // Add event listeners to the navigation icons
    document.querySelector('.gallery-icon').addEventListener('click', function() {
        toggleOnlyOneSection('gallery');
    });

    document.querySelector(".chat-icon").addEventListener("click", function() {
        toggleOnlyOneSection('chat');
    });

    document.querySelector('.bucket-icon').addEventListener('click', function() {
        toggleOnlyOneSection('savedImages');
    });

    document.querySelector('.assistants-icon').addEventListener('click', function() {
        toggleOnlyOneSection('assistants');
    });

    document.querySelector(".draw-icon").addEventListener("click", function() {
        toggleOnlyOneSection('draw');
    });
});

function initializeUI() {
    // Set the initial visibility of all containers
    setContainerVisibility('main-chat-container', true);
    setContainerVisibility('draw-container', false);
    setContainerVisibility('saved-images-container', false);
    setContainerVisibility('assistants-container', false);
}

function setContainerVisibility(containerId, isVisible) {
    var container = document.getElementById(containerId);
    container.style.display = isVisible ? 'block' : 'none';
}

function toggleOnlyOneSection(section) {
    // Hide all sections
    setContainerVisibility('main-chat-container', false);
    setContainerVisibility('draw-container', false);
    setContainerVisibility('saved-images-container', false);
    setContainerVisibility('assistants-container', false);
    setContainerVisibility('assistant-chat-container', false);  // Add this line

    // Show only the selected section
    switch (section) {
        case 'chat':
            setContainerVisibility('main-chat-container', true);
            break;
        case 'draw':
            setContainerVisibility('draw-container', true);
            break;
        case 'savedImages':
            setContainerVisibility('saved-images-container', true);
            fetchAndDisplayImages();
            break;
        case 'assistants':
            setContainerVisibility('assistants-container', true);
            break;
        case 'gallery':
            toggleRightSidebar();
            break;
    }
}
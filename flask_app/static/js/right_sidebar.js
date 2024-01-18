// Search Functionality
function searchGPTs() {
    const searchText = document.querySelector('.right-sidebar .search-container input').value.toLowerCase();
    const items = document.querySelectorAll('.right-sidebar .items-grid .item');
    items.forEach(item => {
        const title = item.querySelector('h3').textContent.toLowerCase();
        if (title.includes(searchText)) {
            item.style.display = ''; // Show matching items
        } else {
            item.style.display = 'none'; // Hide non-matching items
        }
    });
}

// Attach event listeners to the search button and input field
document.getElementById('search-button').addEventListener('click', searchGPTs);
document.querySelector('.right-sidebar .search-container input').addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        searchGPTs();
    }
});


// Category Filtering with Keywords
// Category Filtering with Updated Categories
function filterByCategory(category) {
    const items = document.querySelectorAll('.right-sidebar .items-grid .item');
    items.forEach(item => {
        const description = item.querySelector('.item-info p').textContent.toLowerCase();
        let matchesCategory = false;

        // Define keyword sets for each category
        // Update these keywords based on your data and categories
        const textKeywords = ['text', 'write', 'nlp']; // Example keywords for 'Text'
        const imageKeywords = ['image', 'photo', 'picture']; // Example keywords for 'Images'

        // Check if description matches any keyword in the chosen category
        if (category === 'Text') {
            matchesCategory = textKeywords.some(keyword => description.includes(keyword));
        } else if (category === 'Images') {
            matchesCategory = imageKeywords.some(keyword => description.includes(keyword));
        } else if (category === 'All') {
            matchesCategory = true; // Show all items
        }

        // Toggle item visibility based on category match
        item.style.display = matchesCategory ? '' : 'none';
    });
}

// Add event listeners to category buttons
document.querySelectorAll('.right-sidebar .sidebar-categories .category').forEach(button => {
    button.addEventListener('click', function() {
        filterByCategory(this.textContent);
    });
});


// Close Functionality
function closeSidebar() {
    document.getElementById('right-sidebar').classList.remove('open');
    
    // Show the main chat container when the sidebar is closed
    showMainChatContainer();
}

// Function to show the main chat container
function showMainChatContainer() {
    var mainChatContainer = document.getElementById('main-chat-container');
    mainChatContainer.style.display = 'block';

    // Optionally hide other containers if they should not be visible when the chat is shown
    setContainerVisibility('draw-container', false);
    setContainerVisibility('saved-images-container', false);
    setContainerVisibility('assistants-container', false);
}

// Attach event listener to close button
document.querySelector('.right-sidebar .close').addEventListener('click', closeSidebar);

// Utility function to set container visibility, used in showMainChatContainer and other parts of your script
function setContainerVisibility(containerId, isVisible) {
    var container = document.getElementById(containerId);
    container.style.display = isVisible ? 'block' : 'none';
}
// Document Ready function to initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Existing initializations...
    setupInitialChatbotView();

    // Additional initializations
    document.getElementById('search-button').addEventListener('click', searchGPTs);
    document.querySelector('.right-sidebar .search-container input').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            searchGPTs();
        }
    });

    document.querySelectorAll('.right-sidebar .sidebar-categories .category').forEach(button => {
        button.addEventListener('click', function() {
            filterByCategory(this.textContent);
        });
    });

    document.querySelector('.right-sidebar .close').addEventListener('click', closeSidebar);
});

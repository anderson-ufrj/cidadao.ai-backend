// Cidadão.AI - Main JavaScript

// Theme toggle functionality
function toggleTheme() {
    console.log('Toggle theme called');
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    console.log('Switching from', currentTheme, 'to', newTheme);
    
    // Apply theme to document root
    document.documentElement.setAttribute('data-theme', newTheme);
    document.body.setAttribute('data-theme', newTheme);
    
    // Apply to all containers
    const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
    containers.forEach(container => {
        container.setAttribute('data-theme', newTheme);
    });
    
    // Save theme preference
    localStorage.setItem('theme', newTheme);
    
    // Update toggle text
    const toggles = document.querySelectorAll('.theme-toggle');
    toggles.forEach(toggle => {
        toggle.innerHTML = newTheme === 'light' ? '<span>🌙</span> Modo Escuro' : '<span>☀️</span> Modo Claro';
    });
}

// Set initial theme
function initTheme() {
    console.log('Init theme called');
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log('Saved theme:', savedTheme);
    
    // Apply to all relevant elements
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.body.setAttribute('data-theme', savedTheme);
    
    // Apply to all containers
    const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
    containers.forEach(container => {
        container.setAttribute('data-theme', savedTheme);
    });
    
    // Update toggle buttons
    const toggles = document.querySelectorAll('.theme-toggle');
    console.log('Found toggles:', toggles.length);
    toggles.forEach(toggle => {
        toggle.innerHTML = savedTheme === 'light' ? '<span>🌙</span> Modo Escuro' : '<span>☀️</span> Modo Claro';
        toggle.addEventListener('click', toggleTheme);
    });
}

// Remove Gradio footer elements - VERSÃO SEGURA
function removeGradioFooter() {
    // Remove apenas links específicos do Gradio
    const allLinks = document.querySelectorAll('a');
    allLinks.forEach(link => {
        if (link.href?.includes('gradio.app') || 
            link.textContent.includes('Built with Gradio')) {
            link.style.display = 'none';
        }
    });
}

// Initialize when DOM is ready
function initializeApp() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
    
    // Also try to initialize after a short delay for Gradio
    setTimeout(initTheme, 100);
    setTimeout(initTheme, 500);
    setTimeout(initTheme, 1000);
    setTimeout(initTheme, 2000);
    
    // Remove Gradio footer elements multiple times
    setTimeout(removeGradioFooter, 500);
    setTimeout(removeGradioFooter, 1000);
    setTimeout(removeGradioFooter, 2000);
    setTimeout(removeGradioFooter, 3000);
}

// Credits modal functionality
function showCreditsModal() {
    const modal = document.getElementById('creditsModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function hideCreditsModal() {
    const modal = document.getElementById('creditsModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside
function handleModalClick(event) {
    if (event.target.classList.contains('modal-overlay')) {
        hideCreditsModal();
    }
}

// Help button functionality - formato balão
function toggleHelpModal() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        const isOpen = modal.classList.contains('open');
        if (isOpen) {
            modal.classList.remove('open');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        } else {
            modal.style.display = 'block';
            // Force reflow to ensure the element is rendered
            modal.offsetHeight;
            modal.classList.add('open');
        }
    }
}

function hideHelpModal() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.classList.remove('open');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Close help modal when clicking outside
function handleHelpModalClick(event) {
    // Only close if clicking on the modal itself, not its content
    if (event.target.classList.contains('help-modal')) {
        hideHelpModal();
    }
}

// Navigation functions
function navigateToTab(tabName) {
    const tabs = document.querySelectorAll('.gradio-container .tabs button');
    tabs.forEach((tab, index) => {
        if (tab.textContent.includes(tabName)) {
            tab.click();
        }
    });
}

function navigateToAdvanced() {
    navigateToTab('Consulta Avançada');
}

function navigateToChat() {
    navigateToTab('Pergunte ao Modelo');
}

// Global functions accessible from anywhere
window.toggleTheme = toggleTheme;
window.initTheme = initTheme;
window.showCreditsModal = showCreditsModal;
window.hideCreditsModal = hideCreditsModal;
window.handleModalClick = handleModalClick;
window.toggleHelpModal = toggleHelpModal;
window.hideHelpModal = hideHelpModal;
window.handleHelpModalClick = handleHelpModalClick;
window.navigateToAdvanced = navigateToAdvanced;
window.navigateToChat = navigateToChat;
window.removeGradioFooter = removeGradioFooter;

// Initialize app when script loads
console.log('Cidadão.AI JavaScript loaded');
initializeApp();
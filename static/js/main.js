// Cidadão.AI - Main JavaScript

// Theme toggle functionality - VERSÃO ROBUSTA COM LOGS
function toggleTheme() {
    console.log('🌙 Toggle theme called');
    const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    console.log('🔄 Switching from', currentTheme, 'to', newTheme);
    
    if (newTheme === 'dark') {
        console.log('🌙 Applying dark mode...');
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
        
        // Apply to all containers
        const containers = document.querySelectorAll('.gradio-container, .header, .landing-page, .gr-app');
        console.log('🎯 Found containers:', containers.length);
        containers.forEach(container => {
            container.classList.add('dark-mode');
            console.log('✅ Dark mode applied to:', container.className);
        });
        
        // Force style application
        document.body.style.backgroundColor = '#0F172A';
        document.body.style.color = '#F1F5F9';
        
    } else {
        console.log('☀️ Applying light mode...');
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark-mode');
        
        const containers = document.querySelectorAll('.gradio-container, .header, .landing-page, .gr-app');
        containers.forEach(container => {
            container.classList.remove('dark-mode');
        });
        
        // Force style application
        document.body.style.backgroundColor = '#FFFFFF';
        document.body.style.color = '#0F172A';
    }
    
    // Save theme preference
    localStorage.setItem('theme', newTheme);
    console.log('💾 Theme saved:', newTheme);
    
    // Update toggle text
    updateToggleButtons(newTheme);
}

// Apply theme to all elements
function applyTheme(theme) {
    console.log('Applying theme:', theme);
    
    // Apply to document root
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    
    // Apply to all containers
    const containers = document.querySelectorAll('.gradio-container, .header, .landing-page, .gr-app');
    containers.forEach(container => {
        container.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            container.classList.add('dark-mode');
        } else {
            container.classList.remove('dark-mode');
        }
    });
    
    // Apply to all Gradio elements
    const gradioElements = document.querySelectorAll('[class*="gr-"], .gradio-container *');
    gradioElements.forEach(element => {
        element.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            element.classList.add('dark-mode');
        } else {
            element.classList.remove('dark-mode');
        }
    });
    
    // Force background color update
    if (theme === 'dark') {
        document.body.style.backgroundColor = '#0F172A';
        document.body.style.color = '#F1F5F9';
    } else {
        document.body.style.backgroundColor = '#FFFFFF';
        document.body.style.color = '#0F172A';
    }
}

// Update toggle buttons
function updateToggleButtons(theme) {
    const toggles = document.querySelectorAll('.theme-toggle');
    toggles.forEach(toggle => {
        toggle.innerHTML = theme === 'light' ? '<span>🌙</span> Modo Escuro' : '<span>☀️</span> Modo Claro';
    });
}

// Set initial theme - MODO CLARO COMO PADRÃO
function initTheme() {
    console.log('Init theme called');
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log('Saved theme:', savedTheme);
    
    // Garantir que iniciamos sempre no modo claro por padrão
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
        const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
        containers.forEach(container => container.classList.add('dark-mode'));
    } else {
        // Garantir que as classes de modo escuro sejam removidas
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark-mode');
        const containers = document.querySelectorAll('.gradio-container, .header, .landing-page');
        containers.forEach(container => container.classList.remove('dark-mode'));
    }
    
    // Update toggle buttons
    updateToggleButtons(savedTheme);
    
    // Add event listeners to toggle buttons
    const toggles = document.querySelectorAll('.theme-toggle');
    console.log('Found toggles:', toggles.length);
    toggles.forEach(toggle => {
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

// Monitor theme changes continuously
function monitorThemeChanges() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Apply theme to any new elements
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        applyThemeToElement(node, savedTheme);
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Apply theme to a specific element
function applyThemeToElement(element, theme) {
    element.setAttribute('data-theme', theme);
    if (theme === 'dark') {
        element.classList.add('dark-mode');
    } else {
        element.classList.remove('dark-mode');
    }
    
    // Apply to children as well
    const children = element.querySelectorAll('*');
    children.forEach(child => {
        child.setAttribute('data-theme', theme);
        if (theme === 'dark') {
            child.classList.add('dark-mode');
        } else {
            child.classList.remove('dark-mode');
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
    
    // Monitor theme changes continuously
    setTimeout(monitorThemeChanges, 1000);
    
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
    console.log('🧭 Navigating to tab:', tabName);
    
    // Tentar múltiplos seletores para encontrar as abas do Gradio 5.0
    const selectors = [
        // Gradio 5.0 specific selectors
        '.tabs button[role="tab"]',
        'button[role="tab"]',
        '.tab-nav button',
        '.gradio-tabs button',
        // Legacy selectors
        '.gradio-container .tab-nav button',
        '.gradio-container [role="tab"]',
        '.gradio-container .tabs button',
        '.gradio-container button[role="tab"]',
        '.gr-tab-nav button',
        // More generic selectors
        'button.tab-nav-button',
        '.tabs .tab-nav-button',
        'div.tabs button'
    ];
    
    for (const selector of selectors) {
        const tabs = document.querySelectorAll(selector);
        if (tabs.length > 0) {
            console.log(`🔍 Found ${tabs.length} tabs with selector: ${selector}`);
            
            for (const tab of tabs) {
                const tabText = tab.textContent || tab.innerText || '';
                console.log('📝 Tab text:', tabText);
                if (tabText.includes(tabName)) {
                    console.log('✅ Found matching tab, clicking...');
                    // Force click with multiple methods
                    try {
                        tab.click();
                        // Dispatch click event as backup
                        const clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        tab.dispatchEvent(clickEvent);
                    } catch (e) {
                        console.error('Error clicking tab:', e);
                    }
                    return true;
                }
            }
        }
    }
    
    console.log('❌ No matching tab found for:', tabName);
    return false;
}

function navigateToAdvanced() {
    console.log('🎯 Navigate to Advanced called');
    
    // Tentar imediatamente
    if (navigateToTab('Consulta Avançada') || navigateToTab('🔍 Consulta Avançada') || navigateToTab('Avançada')) {
        return;
    }
    
    // Se não encontrou, aguardar o Gradio carregar
    console.log('⏳ Waiting for Gradio to load...');
    let attempts = 0;
    const maxAttempts = 10;
    
    const tryNavigate = () => {
        attempts++;
        console.log(`🔄 Attempt ${attempts}/${maxAttempts}`);
        
        if (navigateToTab('Consulta Avançada') || navigateToTab('🔍 Consulta Avançada') || navigateToTab('Avançada')) {
            console.log('✅ Navigation successful!');
            return;
        }
        
        if (attempts < maxAttempts) {
            setTimeout(tryNavigate, 500);
        } else {
            console.log('❌ Navigation failed after all attempts');
        }
    };
    
    setTimeout(tryNavigate, 500);
}

function navigateToChat() {
    console.log('💬 Navigate to Chat called');
    
    // Tentar imediatamente
    if (navigateToTab('Pergunte ao Modelo') || navigateToTab('💬 Pergunte ao Modelo') || navigateToTab('Modelo')) {
        return;
    }
    
    // Se não encontrou, aguardar o Gradio carregar
    console.log('⏳ Waiting for Gradio to load...');
    let attempts = 0;
    const maxAttempts = 10;
    
    const tryNavigate = () => {
        attempts++;
        console.log(`🔄 Attempt ${attempts}/${maxAttempts}`);
        
        if (navigateToTab('Pergunte ao Modelo') || navigateToTab('💬 Pergunte ao Modelo') || navigateToTab('Modelo')) {
            console.log('✅ Navigation successful!');
            return;
        }
        
        if (attempts < maxAttempts) {
            setTimeout(tryNavigate, 500);
        } else {
            console.log('❌ Navigation failed after all attempts');
        }
    };
    
    setTimeout(tryNavigate, 500);
}

// Debug function to inspect tab structure
function debugTabs() {
    console.log('🔍 DEBUGGING TABS STRUCTURE');
    
    const allButtons = document.querySelectorAll('button');
    console.log(`Found ${allButtons.length} buttons total`);
    
    allButtons.forEach((button, index) => {
        if (button.textContent.includes('Consulta') || button.textContent.includes('Pergunte') || button.textContent.includes('Cidadão')) {
            console.log(`Button ${index}:`, {
                text: button.textContent,
                classes: button.className,
                role: button.getAttribute('role'),
                parent: button.parentElement?.className
            });
        }
    });
    
    // Tentar encontrar container das abas
    const gradioContainer = document.querySelector('.gradio-container');
    if (gradioContainer) {
        console.log('Gradio container found');
        const tabs = gradioContainer.querySelectorAll('[role="tab"], .tab, .tab-nav button, button');
        console.log(`Found ${tabs.length} potential tabs in gradio container`);
    }
}

// Global functions accessible from anywhere
window.toggleTheme = toggleTheme;
window.initTheme = initTheme;
window.applyTheme = applyTheme;
window.updateToggleButtons = updateToggleButtons;
window.monitorThemeChanges = monitorThemeChanges;
window.applyThemeToElement = applyThemeToElement;
window.showCreditsModal = showCreditsModal;
window.hideCreditsModal = hideCreditsModal;
window.handleModalClick = handleModalClick;
window.toggleHelpModal = toggleHelpModal;
window.hideHelpModal = hideHelpModal;
window.handleHelpModalClick = handleHelpModalClick;
window.navigateToAdvanced = navigateToAdvanced;
window.navigateToChat = navigateToChat;
window.removeGradioFooter = removeGradioFooter;
window.debugTabs = debugTabs;

// Initialize app when script loads
console.log('🚀 Cidadão.AI JavaScript loaded');
console.log('🔍 SHERLOCK: Checking if functions are accessible...');
console.log('🔍 toggleTheme exists?', typeof toggleTheme);
console.log('🔍 initTheme exists?', typeof initTheme);

// Try to initialize immediately
try {
    initializeApp();
    console.log('✅ SHERLOCK: initializeApp() executed successfully');
} catch (error) {
    console.error('❌ SHERLOCK: Error in initializeApp():', error);
}

// Add a manual test function
window.testDarkMode = function() {
    console.log('🧪 SHERLOCK: Manual test function called');
    document.body.style.backgroundColor = '#0F172A';
    document.body.style.color = '#F1F5F9';
    console.log('🧪 SHERLOCK: Manual dark mode applied');
};

// Enhanced event listener with multiple attempts
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 SHERLOCK: DOM loaded, searching for buttons...');
    
    // Function to attach event listeners
    function attachEventListeners() {
        const buttons = document.querySelectorAll('.theme-toggle');
        console.log('🎯 SHERLOCK: Found theme toggle buttons:', buttons.length);
        
        buttons.forEach((button, index) => {
            console.log(`🎯 SHERLOCK: Button ${index}:`, button);
            console.log(`🎯 SHERLOCK: Button ${index} onclick:`, button.onclick);
            
            // Remove existing onclick to avoid conflicts
            button.removeAttribute('onclick');
            
            // Add direct event listener as primary method
            button.addEventListener('click', function(e) {
                console.log('🎯 SHERLOCK: Direct click event fired!');
                e.preventDefault();
                e.stopPropagation();
                toggleTheme();
            });
            
            // Also set onclick as backup
            button.onclick = function(e) {
                console.log('🎯 SHERLOCK: Onclick backup fired!');
                e.preventDefault();
                e.stopPropagation();
                toggleTheme();
            };
        });
    }
    
    // Try multiple times with different delays
    setTimeout(attachEventListeners, 100);
    setTimeout(attachEventListeners, 500);
    setTimeout(attachEventListeners, 1000);
    setTimeout(attachEventListeners, 2000);
    setTimeout(attachEventListeners, 3000);
    
    // Also use MutationObserver to catch dynamically added buttons
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && (node.classList.contains('theme-toggle') || node.querySelector('.theme-toggle'))) {
                        console.log('🎯 SHERLOCK: New theme toggle button detected!');
                        setTimeout(attachEventListeners, 100);
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
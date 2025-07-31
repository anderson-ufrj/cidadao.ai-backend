// GitHub Pages Configuration
// Este arquivo configura detecções específicas para GitHub Pages

// Base path detection for subdirectory deployment
function getBasePath() {
    // Se estiver em GitHub Pages com repo name
    if (window.location.hostname.includes('github.io') && 
        window.location.pathname.includes('/cidadao.ai-backend/')) {
        return '/cidadao.ai-backend/docs';
    }
    // Deploy direto ou localhost
    return '';
}

// GitHub Pages environment detection
function isGitHubPages() {
    return window.location.hostname.includes('github.io');
}

// Export for use in main.js
window.GitHubPagesConfig = {
    getBasePath,
    isGitHubPages
};
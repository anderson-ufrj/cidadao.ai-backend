/* Cidadao.AI Custom JavaScript */

// Add copy button feedback
document.addEventListener("DOMContentLoaded", function() {
  // Enhance code copy buttons
  const copyButtons = document.querySelectorAll(".md-clipboard");
  copyButtons.forEach(button => {
    button.addEventListener("click", function() {
      const originalTitle = this.getAttribute("title");
      this.setAttribute("title", "Copied!");
      setTimeout(() => {
        this.setAttribute("title", originalTitle);
      }, 2000);
    });
  });

  // Add external link icons
  const links = document.querySelectorAll("a[href^='http']");
  links.forEach(link => {
    if (!link.hostname.includes(window.location.hostname)) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    }
  });
});

// Analytics event tracking (if analytics enabled)
function trackEvent(category, action, label) {
  if (typeof gtag !== "undefined") {
    gtag("event", action, {
      event_category: category,
      event_label: label
    });
  }
}

// Track documentation navigation
document.addEventListener("DOMContentLoaded", function() {
  const navLinks = document.querySelectorAll(".md-nav__link");
  navLinks.forEach(link => {
    link.addEventListener("click", function() {
      trackEvent("Navigation", "click", this.textContent.trim());
    });
  });
});

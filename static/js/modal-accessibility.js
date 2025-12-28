// Gallery Modal Accessibility Enhancement
(function () {
  'use strict';

  let lastFocusedElement = null;

  // Open modal
  window.openGalleryModal = function (modalId) {
    const modal = document.getElementById('gallery-modal');
    if (!modal) return;

    // Store currently focused element
    lastFocusedElement = document.activeElement;

    // Show modal
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');

    // Get focusable elements
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    // Add focus trap
    modal.addEventListener('keydown', trapFocus);

    // Close on ESC
    modal.addEventListener('keydown', handleEscape);
  };

  // Close modal
  window.closeGalleryModal = function (event) {
    // Only close if clicking backdrop, not content
    if (event && event.target !== event.currentTarget) return;

    const modal = document.getElementById('gallery-modal');
    if (!modal) return;

    // Hide modal
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');

    // Remove event listeners
    modal.removeEventListener('keydown', trapFocus);
    modal.removeEventListener('keydown', handleEscape);

    // Return focus to trigger element
    if (lastFocusedElement) {
      lastFocusedElement.focus();
      lastFocusedElement = null;
    }
  };

  function trapFocus(e) {
    if (e.key !== 'Tab') return;

    const modal = document.getElementById('gallery-modal');
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  }

  function handleEscape(e) {
    if (e.key === 'Escape') {
      closeGalleryModal();
    }
  }
})();
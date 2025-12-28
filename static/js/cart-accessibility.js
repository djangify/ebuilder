// Announce cart updates to screen readers
(function () {
  'use strict';

  window.announceToScreenReader = function (message) {
    const announcer = document.getElementById('a11y-announcer');
    if (!announcer) return;

    // Clear previous message
    announcer.textContent = '';

    // Announce new message after brief delay (ensures screen readers notice change)
    setTimeout(() => {
      announcer.textContent = message;
    }, 100);

    // Clear after 3 seconds
    setTimeout(() => {
      announcer.textContent = '';
    }, 3000);
  };

  // Listen for cart events
  document.addEventListener('htmx:afterSwap', function (event) {
    // Check if this was a cart action
    if (event.detail.pathInfo.requestPath.includes('/cart/')) {
      // Extract product name from response if possible
      const productName = event.detail.xhr.responseText.match(/data-product-name="([^"]+)"/);
      if (productName) {
        announceToScreenReader(`${productName[1]} added to cart`);
      }
    }
  });
})();

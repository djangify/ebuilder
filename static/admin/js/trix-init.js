// Trix initialization for Django Admin
// Configure Trix BEFORE it initializes
document.addEventListener('trix-before-initialize', function () {
  // Add H2 heading
  Trix.config.blockAttributes.heading2 = {
    tagName: 'h2',
    terminal: true,
    breakOnReturn: true,
    group: false
  };

  // Add H3 heading
  Trix.config.blockAttributes.heading3 = {
    tagName: 'h3',
    terminal: true,
    breakOnReturn: true,
    group: false
  };
});

document.addEventListener('DOMContentLoaded', function () {
  addCustomToolbarButtons();
  initTrixEditors();
});

// Handle Django admin inline formsets (dynamically added forms)
document.addEventListener('formset:added', function (event) {
  setTimeout(function () {
    addCustomToolbarButtons(event.target);
    initTrixEditors(event.target);
  }, 100);
});

function addCustomToolbarButtons(container) {
  const root = container || document;

  root.querySelectorAll('trix-toolbar').forEach(function (toolbar) {
    // Skip if already customized
    if (toolbar.dataset.customized) return;
    toolbar.dataset.customized = 'true';

    const blockTools = toolbar.querySelector('.trix-button-group--block-tools');
    const fileTools = toolbar.querySelector('.trix-button-group--file-tools');

    // Add H2 and H3 buttons
    if (blockTools) {
      const h2Button = document.createElement('button');
      h2Button.type = 'button';
      h2Button.className = 'trix-button';
      h2Button.dataset.trixAttribute = 'heading2';
      h2Button.textContent = 'H2';
      h2Button.title = 'Heading 2';

      const h3Button = document.createElement('button');
      h3Button.type = 'button';
      h3Button.className = 'trix-button';
      h3Button.dataset.trixAttribute = 'heading3';
      h3Button.textContent = 'H3';
      h3Button.title = 'Heading 3';

      const h1Button = blockTools.querySelector('[data-trix-attribute="heading1"]');
      if (h1Button) {
        h1Button.after(h2Button, h3Button);
      } else {
        blockTools.prepend(h3Button);
        blockTools.prepend(h2Button);
      }
    }

    // Add Image URL button (replace or add to file tools)
    if (fileTools) {
      // Hide the default attach button
      const attachButton = fileTools.querySelector('[data-trix-action="attachFiles"]');
      if (attachButton) {
        attachButton.style.display = 'none';
      }

      // Create Image URL button
      const imageButton = document.createElement('button');
      imageButton.type = 'button';
      imageButton.className = 'trix-button trix-button--icon';
      imageButton.dataset.customAction = 'insertImageUrl';
      imageButton.title = 'Insert Image URL';
      imageButton.innerHTML = '🖼️';
      imageButton.style.cssText = 'font-size: 16px; min-width: 36px;';

      imageButton.addEventListener('click', function (e) {
        e.preventDefault();
        const editor = toolbar.nextElementSibling;
        if (editor && editor.tagName === 'TRIX-EDITOR') {
          insertImageFromUrl(editor.editor);
        }
      });

      fileTools.appendChild(imageButton);
    }
  });
}

function insertImageFromUrl(editor) {
  const url = prompt('Enter image URL:');
  if (!url) return;

  // Validate URL
  if (!url.match(/^https?:\/\/.+\.(jpg|jpeg|png|gif|webp|svg)(\?.*)?$/i) &&
    !url.match(/^https?:\/\/.+/i)) {
    // Allow any URL but warn if it doesn't look like an image
    if (!confirm('This URL may not be an image. Insert anyway?')) {
      return;
    }
  }

  // Optional: prompt for alt text
  const altText = prompt('Enter alt text (optional):', '') || 'Image';

  // Create attachment with the image URL
  const attachment = new Trix.Attachment({
    content: `<img src="${url}" alt="${altText}" style="max-width: 100%; height: auto;">`,
    contentType: 'image'
  });

  editor.insertAttachment(attachment);
}

function initTrixEditors(container) {
  const root = container || document;
  root.querySelectorAll('textarea[data-trix="true"]').forEach(function (textarea) {
    // Skip if already initialized
    if (textarea.nextElementSibling && textarea.nextElementSibling.tagName === 'TRIX-EDITOR') {
      return;
    }

    // Ensure unique ID
    if (!textarea.id) {
      textarea.id = 'trix-textarea-' + Math.random().toString(36).substr(2, 9);
    }

    // Create trix-editor element
    const trixEditor = document.createElement('trix-editor');
    trixEditor.setAttribute('input', textarea.id);
    trixEditor.classList.add('trix-content');

    // Insert after textarea
    textarea.parentNode.insertBefore(trixEditor, textarea.nextSibling);
  });
}

// Disable file uploads (drag/drop and paste) but allow our URL images
document.addEventListener('trix-file-accept', function (e) {
  e.preventDefault();
});

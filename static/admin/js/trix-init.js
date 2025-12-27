// Trix initialization for Django Admin with Auto-Save
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
  initAutoSave();
});

// Handle Django admin inline formsets (dynamically added forms)
document.addEventListener('formset:added', function (event) {
  setTimeout(function () {
    addCustomToolbarButtons(event.target);
    initTrixEditors(event.target);
    initAutoSave(event.target);
  }, 100);
});

// ============================================================
// AUTO-SAVE FUNCTIONALITY
// ============================================================

const AUTOSAVE_INTERVAL = 30000; // 30 seconds
const AUTOSAVE_PREFIX = 'ebuilder_draft_';

function getStorageKey(textarea) {
  // Create a unique key based on URL path and field name/id
  const path = window.location.pathname;
  const fieldId = textarea.id || textarea.name || 'content';
  return AUTOSAVE_PREFIX + btoa(path + '_' + fieldId).replace(/[^a-zA-Z0-9]/g, '');
}

function initAutoSave(container) {
  const root = container || document;

  root.querySelectorAll('textarea[data-trix="true"]').forEach(function (textarea) {
    const storageKey = getStorageKey(textarea);
    const trixEditor = textarea.nextElementSibling;

    if (!trixEditor || trixEditor.tagName !== 'TRIX-EDITOR') {
      return;
    }

    // Skip if already has auto-save initialized
    if (textarea.dataset.autosaveInit) {
      return;
    }
    textarea.dataset.autosaveInit = 'true';

    // Restore draft on load (only for new/empty content)
    restoreDraft(textarea, trixEditor, storageKey);

    // Set up periodic auto-save
    let autoSaveTimer = setInterval(function () {
      saveDraft(textarea, storageKey);
    }, AUTOSAVE_INTERVAL);

    // Also save on content change (debounced)
    let changeTimer = null;
    trixEditor.addEventListener('trix-change', function () {
      clearTimeout(changeTimer);
      changeTimer = setTimeout(function () {
        saveDraft(textarea, storageKey);
      }, 2000); // Save 2 seconds after user stops typing
    });

    // Clear draft on successful form submission
    const form = textarea.closest('form');
    if (form) {
      form.addEventListener('submit', function () {
        clearDraft(storageKey);
        clearInterval(autoSaveTimer);
      });
    }

    // Add auto-save indicator
    addAutoSaveIndicator(trixEditor);
  });
}

function saveDraft(textarea, storageKey) {
  const content = textarea.value;

  // Don't save empty content
  if (!content || content.trim() === '' || content === '<div></div>') {
    return;
  }

  try {
    const draftData = {
      content: content,
      timestamp: Date.now(),
      url: window.location.href
    };
    localStorage.setItem(storageKey, JSON.stringify(draftData));
    showAutoSaveIndicator(textarea, 'saved');
  } catch (e) {
    console.warn('Auto-save failed:', e);
    showAutoSaveIndicator(textarea, 'error');
  }
}

function restoreDraft(textarea, trixEditor, storageKey) {
  try {
    const saved = localStorage.getItem(storageKey);
    if (!saved) return;

    const draftData = JSON.parse(saved);
    const currentContent = textarea.value;

    // Only restore if:
    // 1. Current content is empty (new post) OR
    // 2. Draft is newer and different from current content
    const isCurrentEmpty = !currentContent || currentContent.trim() === '' || currentContent === '<div></div>';
    const isDraftDifferent = draftData.content !== currentContent;
    const isDraftRecent = (Date.now() - draftData.timestamp) < (24 * 60 * 60 * 1000); // Less than 24 hours old

    if (isCurrentEmpty && draftData.content && isDraftRecent) {
      // Auto-restore for empty forms
      trixEditor.editor.loadHTML(draftData.content);
      showDraftRestoredNotice(trixEditor, draftData.timestamp);
    } else if (isDraftDifferent && isDraftRecent && draftData.content) {
      // Offer to restore for forms with existing content
      showDraftAvailableNotice(trixEditor, draftData, storageKey);
    }
  } catch (e) {
    console.warn('Draft restore failed:', e);
  }
}

function clearDraft(storageKey) {
  try {
    localStorage.removeItem(storageKey);
  } catch (e) {
    console.warn('Draft clear failed:', e);
  }
}

function addAutoSaveIndicator(trixEditor) {
  // Add indicator element after the toolbar
  const toolbar = trixEditor.previousElementSibling;
  if (toolbar && toolbar.tagName === 'TRIX-TOOLBAR') {
    const existingIndicator = toolbar.querySelector('.autosave-indicator');
    if (existingIndicator) return;

    const indicator = document.createElement('span');
    indicator.className = 'autosave-indicator';
    indicator.style.cssText = `
      margin-left: 10px;
      font-size: 11px;
      color: #666;
      opacity: 0;
      transition: opacity 0.3s ease;
    `;
    toolbar.appendChild(indicator);
  }
}

function showAutoSaveIndicator(textarea, status) {
  const trixEditor = textarea.nextElementSibling;
  if (!trixEditor) return;

  const toolbar = trixEditor.previousElementSibling;
  if (!toolbar) return;

  const indicator = toolbar.querySelector('.autosave-indicator');
  if (!indicator) return;

  if (status === 'saved') {
    indicator.textContent = '✓ Draft saved';
    indicator.style.color = '#28a745';
  } else if (status === 'error') {
    indicator.textContent = '⚠ Save failed';
    indicator.style.color = '#dc3545';
  }

  indicator.style.opacity = '1';

  // Fade out after 3 seconds
  setTimeout(function () {
    indicator.style.opacity = '0';
  }, 3000);
}

function showDraftRestoredNotice(trixEditor, timestamp) {
  const time = new Date(timestamp).toLocaleString();
  const notice = document.createElement('div');
  notice.className = 'draft-notice';
  notice.style.cssText = `
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 8px 12px;
    margin-bottom: 10px;
    border-radius: 4px;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  `;
  notice.innerHTML = `
    <span>📝 Draft restored from ${time}</span>
    <button type="button" class="dismiss-notice" style="
      background: none;
      border: none;
      color: #155724;
      cursor: pointer;
      font-size: 16px;
      padding: 0 5px;
    ">×</button>
  `;

  trixEditor.parentNode.insertBefore(notice, trixEditor);

  notice.querySelector('.dismiss-notice').addEventListener('click', function () {
    notice.remove();
  });

  // Auto-dismiss after 10 seconds
  setTimeout(function () {
    if (notice.parentNode) {
      notice.style.opacity = '0';
      notice.style.transition = 'opacity 0.3s ease';
      setTimeout(() => notice.remove(), 300);
    }
  }, 10000);
}

function showDraftAvailableNotice(trixEditor, draftData, storageKey) {
  const time = new Date(draftData.timestamp).toLocaleString();
  const notice = document.createElement('div');
  notice.className = 'draft-notice';
  notice.style.cssText = `
    background: #fff3cd;
    border: 1px solid #ffc107;
    color: #856404;
    padding: 8px 12px;
    margin-bottom: 10px;
    border-radius: 4px;
    font-size: 13px;
  `;
  notice.innerHTML = `
    <span>📝 A draft from ${time} is available.</span>
    <button type="button" class="restore-draft" style="
      background: #ffc107;
      border: none;
      color: #856404;
      cursor: pointer;
      padding: 4px 10px;
      border-radius: 3px;
      margin-left: 10px;
      font-size: 12px;
    ">Restore Draft</button>
    <button type="button" class="discard-draft" style="
      background: none;
      border: 1px solid #856404;
      color: #856404;
      cursor: pointer;
      padding: 4px 10px;
      border-radius: 3px;
      margin-left: 5px;
      font-size: 12px;
    ">Discard</button>
  `;

  trixEditor.parentNode.insertBefore(notice, trixEditor);

  notice.querySelector('.restore-draft').addEventListener('click', function () {
    trixEditor.editor.loadHTML(draftData.content);
    notice.remove();
    showDraftRestoredNotice(trixEditor, draftData.timestamp);
  });

  notice.querySelector('.discard-draft').addEventListener('click', function () {
    clearDraft(storageKey);
    notice.remove();
  });
}

// ============================================================
// TOOLBAR CUSTOMIZATION
// ============================================================

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

// ============================================================
// TRIX EDITOR INITIALIZATION
// ============================================================

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

// ============================================================
// CLEANUP OLD DRAFTS (runs once per session)
// ============================================================

(function cleanupOldDrafts() {
  const ONE_WEEK = 7 * 24 * 60 * 60 * 1000;
  const now = Date.now();

  try {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && key.startsWith(AUTOSAVE_PREFIX)) {
        try {
          const data = JSON.parse(localStorage.getItem(key));
          if (data.timestamp && (now - data.timestamp) > ONE_WEEK) {
            localStorage.removeItem(key);
          }
        } catch (e) {
          // Invalid data, remove it
          localStorage.removeItem(key);
        }
      }
    }
  } catch (e) {
    console.warn('Draft cleanup failed:', e);
  }
})();
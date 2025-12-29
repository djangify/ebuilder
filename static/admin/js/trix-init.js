// ============================================================
// TRIX EDITOR CONFIGURATION FOR DJANGO ADMIN
// With H2, H3 headings, Image URL insertion, and Auto-Save
// Fixed for Django inline formsets and timing issues
// ============================================================

// Load Trix CSS dynamically
(function loadTrixCSS() {
  const cssFiles = [
    '/static/admin/css/trix.css',
    '/static/admin/css/trix-admin.css'
  ];

  cssFiles.forEach(function (href) {
    if (!document.querySelector('link[href="' + href + '"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.type = 'text/css';
      link.href = href;
      document.head.appendChild(link);
    }
  });
})();

// ============================================================
// TRIX CONFIGURATION - MUST RUN BEFORE TRIX INITIALIZES
// ============================================================

// Configure Trix immediately when this script loads
// This function will be called multiple times to ensure it runs
function configureTrixHeadings() {
  if (typeof Trix === 'undefined') return false;

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

  return true;
}

// Try to configure immediately
configureTrixHeadings();

// Also listen for trix-before-initialize (catches first load)
document.addEventListener('trix-before-initialize', function () {
  configureTrixHeadings();
});

// ============================================================
// TOOLBAR CUSTOMIZATION - ADD H2, H3, IMAGE BUTTONS
// ============================================================

function addCustomToolbarButtons(container) {
  const root = container || document;

  root.querySelectorAll('trix-toolbar').forEach(function (toolbar) {
    // Skip if already customized
    if (toolbar.dataset.customized === 'true') return;
    toolbar.dataset.customized = 'true';

    const blockTools = toolbar.querySelector('.trix-button-group--block-tools');
    const fileTools = toolbar.querySelector('.trix-button-group--file-tools');

    // Add H2 and H3 buttons
    if (blockTools) {
      // Check if H2 already exists
      if (!blockTools.querySelector('[data-trix-attribute="heading2"]')) {
        const h2Button = document.createElement('button');
        h2Button.type = 'button';
        h2Button.className = 'trix-button';
        h2Button.dataset.trixAttribute = 'heading2';
        h2Button.textContent = 'H2';
        h2Button.title = 'Heading 2';
        h2Button.tabIndex = -1;

        const h3Button = document.createElement('button');
        h3Button.type = 'button';
        h3Button.className = 'trix-button';
        h3Button.dataset.trixAttribute = 'heading3';
        h3Button.textContent = 'H3';
        h3Button.title = 'Heading 3';
        h3Button.tabIndex = -1;

        const h1Button = blockTools.querySelector('[data-trix-attribute="heading1"]');
        if (h1Button) {
          h1Button.after(h2Button, h3Button);
        } else {
          blockTools.prepend(h3Button);
          blockTools.prepend(h2Button);
        }
      }
    }

    // Add Image URL button
    if (fileTools) {
      // Check if image button already exists
      if (!fileTools.querySelector('[data-custom-action="insertImageUrl"]')) {
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
        imageButton.style.cssText = 'font-size: 16px; min-width: 36px; text-indent: 0;';
        imageButton.tabIndex = -1;

        imageButton.addEventListener('click', function (e) {
          e.preventDefault();
          const editor = toolbar.nextElementSibling;
          if (editor && editor.tagName === 'TRIX-EDITOR') {
            insertImageFromUrl(editor.editor);
          }
        });

        fileTools.appendChild(imageButton);
      }
    }
  });
}

function insertImageFromUrl(editor) {
  const url = prompt('Enter image URL:');
  if (!url) return;

  // Validate URL
  if (!url.match(/^https?:\/\/.+\.(jpg|jpeg|png|gif|webp|svg)(\?.*)?$/i) &&
    !url.match(/^https?:\/\/.+/i)) {
    if (!confirm('This URL may not be an image. Insert anyway?')) {
      return;
    }
  }

  const altText = prompt('Enter alt text (optional):', '') || 'Image';

  const attachment = new Trix.Attachment({
    content: `<img src="${url}" alt="${altText}" style="max-width: 100%; height: auto;">`,
    contentType: 'image'
  });

  editor.insertAttachment(attachment);
}

// ============================================================
// WATCH FOR NEW TRIX EDITORS (handles dynamic loading)
// ============================================================

// Listen for each individual editor initialization
document.addEventListener('trix-initialize', function (event) {
  // Ensure config is set
  configureTrixHeadings();

  // Find the toolbar for this editor and customize it
  const editor = event.target;
  const toolbar = editor.toolbarElement;

  if (toolbar) {
    // Reset customized flag to allow re-customization
    toolbar.dataset.customized = 'false';
    addCustomToolbarButtons(toolbar.parentElement || document);
  }

  // Initialize auto-save for this editor
  const textarea = document.getElementById(editor.getAttribute('input'));
  if (textarea) {
    initAutoSaveForTextarea(textarea, editor);
  }
});

// ============================================================
// MAIN INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
  // Configure Trix (in case it loaded after us)
  configureTrixHeadings();

  // Clean template forms FIRST
  cleanTemplateRows();

  // Add buttons to any existing toolbars
  addCustomToolbarButtons();

  // Initialize editors
  initTrixEditors();

  // Initialize auto-save
  initAutoSave();

  // Set up inline formset handlers
  setupInlineFormsetHandlers();

  // Retry button addition after a short delay (catches late-loading toolbars)
  setTimeout(function () {
    addCustomToolbarButtons();
  }, 500);
});

// ============================================================
// DJANGO INLINE FORMSET HANDLING
// ============================================================

function cleanTemplateRows() {
  const emptyForms = document.querySelectorAll('.empty-form, [id*="-empty"], [id*="__prefix__"]');
  emptyForms.forEach(function (form) {
    const editors = form.querySelectorAll('trix-editor');
    editors.forEach(function (editor) {
      editor.remove();
    });
    const toolbars = form.querySelectorAll('trix-toolbar');
    toolbars.forEach(function (toolbar) {
      toolbar.remove();
    });
    const textareas = form.querySelectorAll('textarea[data-trix="true"]');
    textareas.forEach(function (textarea) {
      textarea.style.display = '';
      textarea.removeAttribute('data-autosave-init');
    });
  });
}

function setupInlineFormsetHandlers() {
  // Handle Django's formset:added event (Django 4.1+)
  document.addEventListener('formset:added', function (event) {
    const newRow = event.target;

    // Clean any accidentally cloned Trix elements
    newRow.querySelectorAll('trix-editor').forEach(e => e.remove());
    newRow.querySelectorAll('trix-toolbar').forEach(t => t.remove());

    // Reset textarea state
    newRow.querySelectorAll('textarea[data-trix="true"]').forEach(function (textarea) {
      textarea.style.display = '';
      textarea.removeAttribute('data-autosave-init');
      if (textarea.id && textarea.id.includes('__prefix__')) {
        textarea.id = textarea.id.replace('__prefix__', Date.now().toString());
      }
    });

    // Initialize after a short delay
    setTimeout(function () {
      configureTrixHeadings();
      initTrixEditors(newRow);
      addCustomToolbarButtons(newRow);
      initAutoSave(newRow);
    }, 100);
  });

  // Fallback: Watch for "Add another" clicks
  document.addEventListener('click', function (e) {
    const addRow = e.target.closest('.add-row a, .inline-group .add-row a');
    if (addRow) {
      cleanTemplateRows();

      setTimeout(function () {
        document.querySelectorAll('textarea[data-trix="true"]').forEach(function (textarea) {
          if (textarea.name && textarea.name.includes('__prefix__')) return;
          if (textarea.nextElementSibling && textarea.nextElementSibling.tagName === 'TRIX-EDITOR') return;
          initTrixOnTextarea(textarea);
        });
        configureTrixHeadings();
        addCustomToolbarButtons();
        initAutoSave();
      }, 150);
    }
  });
}

// ============================================================
// TRIX EDITOR INITIALIZATION
// ============================================================

function initTrixOnTextarea(textarea) {
  if (textarea.name && textarea.name.includes('__prefix__')) return;
  if (textarea.nextElementSibling && textarea.nextElementSibling.tagName === 'TRIX-EDITOR') return;

  if (!textarea.id) {
    textarea.id = 'trix-textarea-' + Math.random().toString(36).substr(2, 9);
  }

  const trixEditor = document.createElement('trix-editor');
  trixEditor.setAttribute('input', textarea.id);
  trixEditor.classList.add('trix-content');
  textarea.parentNode.insertBefore(trixEditor, textarea.nextSibling);
  textarea.style.display = 'none';
}

function initTrixEditors(container) {
  const root = container || document;
  root.querySelectorAll('textarea[data-trix="true"]').forEach(initTrixOnTextarea);
}

// Disable file uploads (drag/drop and paste)
document.addEventListener('trix-file-accept', function (e) {
  e.preventDefault();
});

// ============================================================
// AUTO-SAVE FUNCTIONALITY
// ============================================================

const AUTOSAVE_INTERVAL = 30000;
const AUTOSAVE_PREFIX = 'ebuilder_draft_';

function getStorageKey(textarea) {
  const path = window.location.pathname;
  const fieldId = textarea.id || textarea.name || 'content';
  return AUTOSAVE_PREFIX + btoa(path + '_' + fieldId).replace(/[^a-zA-Z0-9]/g, '');
}

function initAutoSaveForTextarea(textarea, trixEditor) {
  if (textarea.name && textarea.name.includes('__prefix__')) return;
  if (textarea.dataset.autosaveInit) return;

  textarea.dataset.autosaveInit = 'true';
  const storageKey = getStorageKey(textarea);

  // Restore draft
  restoreDraft(textarea, trixEditor, storageKey);

  // Periodic auto-save
  setInterval(function () {
    saveDraft(textarea, storageKey);
  }, AUTOSAVE_INTERVAL);

  // Save on change (debounced)
  let changeTimer = null;
  trixEditor.addEventListener('trix-change', function () {
    clearTimeout(changeTimer);
    changeTimer = setTimeout(function () {
      saveDraft(textarea, storageKey);
    }, 2000);
  });

  // Clear draft on form submit
  const form = textarea.closest('form');
  if (form && !form.dataset.autosaveFormInit) {
    form.dataset.autosaveFormInit = 'true';
    form.addEventListener('submit', function () {
      form.querySelectorAll('textarea[data-trix="true"]').forEach(function (ta) {
        clearDraft(getStorageKey(ta));
      });
    });
  }

  addAutoSaveIndicator(trixEditor);
}

function initAutoSave(container) {
  const root = container || document;
  root.querySelectorAll('textarea[data-trix="true"]').forEach(function (textarea) {
    if (textarea.name && textarea.name.includes('__prefix__')) return;

    const trixEditor = textarea.nextElementSibling;
    if (!trixEditor || trixEditor.tagName !== 'TRIX-EDITOR') return;

    initAutoSaveForTextarea(textarea, trixEditor);
  });
}

function saveDraft(textarea, storageKey) {
  const content = textarea.value;
  if (!content || content.trim() === '' || content === '<div></div>') return;

  try {
    localStorage.setItem(storageKey, JSON.stringify({
      content: content,
      timestamp: Date.now(),
      url: window.location.href
    }));
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
    const isCurrentEmpty = !currentContent || currentContent.trim() === '' || currentContent === '<div></div>';
    const isDraftDifferent = draftData.content !== currentContent;

    if (isCurrentEmpty && draftData.content) {
      trixEditor.editor.loadHTML(draftData.content);
      showDraftRestoredNotice(trixEditor, draftData.timestamp);
    } else if (isDraftDifferent && draftData.timestamp) {
      const draftAge = Date.now() - draftData.timestamp;
      const oneHour = 60 * 60 * 1000;
      if (draftAge < oneHour) {
        showDraftAvailableNotice(trixEditor, draftData, storageKey);
      }
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
  if (trixEditor.parentNode.querySelector('.autosave-indicator')) return;

  const indicator = document.createElement('div');
  indicator.className = 'autosave-indicator';
  indicator.style.cssText = `
    font-size: 11px;
    color: #888;
    text-align: right;
    padding: 2px 5px;
    opacity: 0;
    transition: opacity 0.3s ease;
  `;
  trixEditor.parentNode.insertBefore(indicator, trixEditor.nextSibling);
}

function showAutoSaveIndicator(textarea, status) {
  const trixEditor = textarea.nextElementSibling;
  if (!trixEditor) return;

  const indicator = trixEditor.parentNode.querySelector('.autosave-indicator');
  if (!indicator) return;

  indicator.textContent = status === 'saved' ? '✓ Draft saved' : '⚠ Save failed';
  indicator.style.color = status === 'saved' ? '#28a745' : '#dc3545';
  indicator.style.opacity = '1';

  setTimeout(function () {
    indicator.style.opacity = '0';
  }, 2000);
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
  notice.querySelector('.dismiss-notice').addEventListener('click', () => notice.remove());

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
          localStorage.removeItem(key);
        }
      }
    }
  } catch (e) {
    console.warn('Draft cleanup failed:', e);
  }
})();

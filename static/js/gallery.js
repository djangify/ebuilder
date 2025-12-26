document.addEventListener("keydown", function (e) {
  const modal = document.getElementById("gallery-modal");
  if (!modal || modal.classList.contains("hidden")) return;

  if (e.key === "Escape") {
    closeGallery();
  }

  if (e.key === "ArrowLeft") {
    const prev = modal.querySelector("[aria-label='Previous image']");
    if (prev) prev.click();
  }

  if (e.key === "ArrowRight") {
    const next = modal.querySelector("[aria-label='Next image']");
    if (next) next.click();
  }
});

function openGallery() {
  const modal = document.getElementById("gallery-modal");
  modal.classList.remove("hidden");
  modal.focus();
}

function closeGallery() {
  const modal = document.getElementById("gallery-modal");
  modal.classList.add("hidden");
  modal.innerHTML = "";
}

function closeGalleryModal(e) {
  if (e.target === e.currentTarget) {
    closeGallery();
  }
}
document.body.addEventListener("htmx:afterSwap", function (e) {
  if (e.target.id === "gallery-modal") {
    openGallery();
  }
});

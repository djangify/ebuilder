document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.querySelector(".hamburger");
  const nav = document.querySelector(".nav");
  const navLinks = document.querySelectorAll(".nav--link");

  // Only add handlers if hamburger exists
  if (hamburger && nav) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("close");
      nav.classList.toggle("open");

      if (nav.classList.contains("open")) {
        nav.style.position = "fixed";
        nav.style.top = "60px"; // Adjust header height if needed
      } else {
        setTimeout(() => {
          nav.style.position = "";
          nav.style.top = "";
        }, 300);
      }
    });

    // Close menu when a link is clicked
    navLinks.forEach(link => {
      link.addEventListener("click", () => {
        hamburger.classList.remove("close");
        nav.classList.remove("open");

        setTimeout(() => {
          nav.style.position = "";
          nav.style.top = "";
        }, 300);
      });
    });
  }
});

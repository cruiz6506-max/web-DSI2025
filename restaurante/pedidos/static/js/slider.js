let currentSlide = 0;

function showSlide(index) {
  const slides = document.querySelector(".slides");
  const totalSlides = document.querySelectorAll(".slide").length;

  // Loop back to the beginning or end
  if (index >= totalSlides) {
    currentSlide = 0;
  } else if (index < 0) {
    currentSlide = totalSlides - 1;
  } else {
    currentSlide = index;
  }

  // Move to the current slide
  slides.style.transform = `translateX(${-currentSlide * 100}%)`;
}

function moveSlide(step) {
  showSlide(currentSlide + step);
}

// Initialize the slider
showSlide(currentSlide);

document.addEventListener('DOMContentLoaded', function () {
  const carousel = document.querySelector('.testimonial-carousel');
  if (!carousel) return;

  const slides = carousel.querySelectorAll('.testimonial-slide');
  const prevButton = carousel.querySelector('.prev-button');
  const nextButton = carousel.querySelector('.next-button');
  const indicators = carousel.querySelectorAll('.carousel-indicator');

  let currentSlide = 0;

  function updateSlide(index) {
    slides.forEach(slide => {
      slide.style.opacity = '0';
      slide.style.display = 'none';
    });

    indicators.forEach(indicator => {
      indicator.classList.remove('bg-blue-600');
      indicator.classList.add('bg-gray-300');
    });

    slides[index].style.display = 'block';
    setTimeout(() => {
      slides[index].style.opacity = '1';
    }, 10);

    indicators[index].classList.remove('bg-gray-300');
    indicators[index].classList.add('bg-blue-600');
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    updateSlide(currentSlide);
  }

  function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    updateSlide(currentSlide);
  }

  prevButton.addEventListener('click', prevSlide);
  nextButton.addEventListener('click', nextSlide);

  indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
      currentSlide = index;
      updateSlide(currentSlide);
    });
  });

  // Initialize first slide
  updateSlide(0);
});

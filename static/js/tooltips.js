document.addEventListener('DOMContentLoaded', function () {
  const progressBars = document.querySelectorAll('[data-tooltip]');

  progressBars.forEach(bar => {
    bar.addEventListener('mouseenter', (e) => {
      const tooltip = document.createElement('div');
      tooltip.className = 'absolute bg-gray-900 text-white px-2 py-1 rounded text-sm -top-8 left-1/2 transform -translate-x-1/2 z-50';
      tooltip.textContent = e.target.dataset.tooltip;
      e.target.appendChild(tooltip);
    });

    bar.addEventListener('mouseleave', (e) => {
      const tooltip = e.target.querySelector('div');
      if (tooltip) {
        tooltip.remove();
      }
    });
  });
});

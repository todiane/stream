document.addEventListener('DOMContentLoaded', function () {
  const reasonSelect = document.querySelector('#id_reason');
  const parentDetails = document.querySelector('#parent-details');

  function toggleParentDetails() {
    if (reasonSelect && parentDetails) {  // Add null check
      if (reasonSelect.value === 'tuition') {
        parentDetails.classList.remove('hidden');
      } else {
        parentDetails.classList.add('hidden');
      }
    }
  }

  if (reasonSelect) {
    reasonSelect.addEventListener('change', toggleParentDetails);
    toggleParentDetails();  // Run on initial load
  }
});

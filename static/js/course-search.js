document.addEventListener('DOMContentLoaded', function () {
  const searchBar = document.getElementById('search-bar');
  const courseList = document.getElementById('course-list');

  searchBar.addEventListener('input', function (e) {
    const query = e.target.value.trim();

    fetch(`?query=${encodeURIComponent(query)}`, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.results.length > 0) {
          let html = '<div class="grid gap-8 lg:grid-cols-3 max-w-7xl mx-auto px-4">';
          data.results.forEach(item => {
            // Choose background color based on type
            const bgColor = item.type === 'lesson' ? 'bg-slate-50' : 'bg-white';

            html += `
              <div class="max-w-sm mx-auto ${bgColor} rounded-lg shadow dark:bg-gray-800">
                <div class="p-5 text-center">
                  <h2 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
                    <a href="${item.path}">${item.title}</a>
                  </h2>
                  <div class="flex justify-center items-center gap-2">
                    <span class="text-sm text-gray-500">${item.type === 'lesson' ? 'Lesson' : 'Course'}</span>
                    <a href="${item.path}" class="text-blue-600 hover:underline">
                      ${item.type === 'lesson' ? 'View Lesson' : 'View Course'}
                    </a>
                  </div>
                </div>
              </div>
            `;
          });
          html += '</div>';
          courseList.innerHTML = html;
        } else {
          courseList.innerHTML = '<p class="text-center">No results found</p>';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        courseList.innerHTML = '<p class="text-center text-red-500">An error occurred while searching</p>';
      });
  });
});

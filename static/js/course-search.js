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
          data.results.forEach(course => {
            html += `
                      <div class="max-w-sm mx-auto bg-white rounded-lg shadow dark:bg-gray-800">
                          <div class="p-5 text-center">
                              <h2 class="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
                                  <a href="${course.path}">${course.title}</a>
                              </h2>
                              <div class="flex justify-center items-center">
                                  <a href="${course.path}" class="text-blue-600 hover:underline">View Course</a>
                              </div>
                          </div>
                      </div>
                  `;
          });
          html += '</div>';
          courseList.innerHTML = html;
        } else {
          courseList.innerHTML = '<p class="text-center">No courses found</p>';
        }
      });
  });
});

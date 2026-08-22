const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');

if (menuToggle && sidebar) {
  menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
}

document.querySelectorAll('.sidebar .nav-item').forEach((item) => {
  item.addEventListener('click', () => sidebar?.classList.remove('open'));
});

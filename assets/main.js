const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      menuButton.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
      menuButton.focus();
    }
  });
}

const projectFilters = [...document.querySelectorAll('[data-project-filter]')];
if (projectFilters.length) {
  const projects = [...document.querySelectorAll('#project-list [data-project-category]')];
  const status = document.querySelector('#project-count');
  projectFilters.forEach((button) => {
    button.addEventListener('click', () => {
      const category = button.dataset.projectFilter;
      projectFilters.forEach((filter) => filter.setAttribute('aria-pressed', String(filter === button)));
      let count = 0;
      projects.forEach((project) => {
        const matches = category === 'all' || project.dataset.projectCategory === category;
        project.hidden = !matches;
        if (matches) count++;
      });
      status.textContent = `${count} ${count === 1 ? 'project' : 'projects'}`;
    });
  });
}

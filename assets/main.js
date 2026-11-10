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

const search = document.querySelector('#story-search');
if (search) {
  const stories = [...document.querySelectorAll('#stories .post-card')];
  search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    stories.forEach((story) => {
      const matches = story.textContent.toLocaleLowerCase().includes(query);
      story.hidden = !matches;
      if (matches) count++;
    });
    document.querySelector('#search-empty').hidden = count !== 0;
    document.querySelector('#search-status').textContent = `${count} ${count === 1 ? 'story' : 'stories'} found`;
  });
}


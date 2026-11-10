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

// Videos load only on request. The ordinary YouTube links also work without JS.
document.querySelectorAll('[data-video]').forEach((poster) => {
  poster.addEventListener('click', (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const videoId = poster.dataset.video;
    if (!/^[a-zA-Z0-9_-]{11}$/.test(videoId)) return;
    const frame = document.createElement('iframe');
    frame.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`;
    frame.title = poster.getAttribute('aria-label').replace(/^Play /, '');
    frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.className = 'video-frame';
    frame.tabIndex = 0;
    poster.replaceWith(frame);
    frame.focus();
  });
});

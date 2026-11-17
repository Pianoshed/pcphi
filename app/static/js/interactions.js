(() => {
  // staggered reveal for cards, tiles and rows; containers marked data-reveal fade as one
  const auto = '.card,.theme,.goal,.goal-row,.stat,.roles .panel,.figures>div,.figs figure,.pathway,.panel.vision,.panel.mission,.formcard';
  document.querySelectorAll(auto).forEach(e => {
    if (e.closest('[data-reveal]') || e.closest('.adm')) return;
    e.classList.add('rv');
    const sib = [...e.parentElement.children].filter(c => c.classList.contains('rv'));
    e.style.setProperty('--d', Math.min(sib.indexOf(e), 6) * 70 + 'ms');
  });
  const els = document.querySelectorAll('[data-reveal],.rv');
  if (!('IntersectionObserver' in window)) return els.forEach(e => e.classList.add('in'));
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .08, rootMargin: '0px 0px -30px 0px' });
  els.forEach(e => io.observe(e));
})();

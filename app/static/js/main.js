(() => {
  const d = document, nav = d.getElementById('nav'), btn = d.querySelector('.menu-btn'), hdr = d.querySelector('.site-header');
  d.documentElement.classList.remove('no-js');
  const solid = () => hdr && hdr.classList.toggle('solid', scrollY > 20 || (nav && nav.classList.contains('open')));
  const closeAll = () => { nav && nav.classList.remove('open'); btn && btn.setAttribute('aria-expanded', 'false');
    d.querySelectorAll('.dd.open').forEach(x => { x.classList.remove('open'); x.querySelector('.dd-btn').setAttribute('aria-expanded', 'false'); }); solid(); };
  solid(); addEventListener('scroll', solid, { passive: true });
  btn && btn.addEventListener('click', () => { const o = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', o); btn.setAttribute('aria-label', o ? 'Close menu' : 'Open menu'); solid(); });
  d.querySelectorAll('.dd').forEach(dd => { const b = dd.querySelector('.dd-btn');
    b.addEventListener('click', e => { e.stopPropagation(); const o = !dd.classList.contains('open');
      d.querySelectorAll('.dd.open').forEach(x => x !== dd && x.classList.remove('open')); dd.classList.toggle('open', o); b.setAttribute('aria-expanded', o); }); });
  d.addEventListener('click', e => { if (!e.target.closest('.nav')) closeAll(); else d.querySelectorAll('.dd.open').forEach(x => !x.contains(e.target) && x.classList.remove('open')); });
  d.addEventListener('keydown', e => e.key === 'Escape' && closeAll());
  d.querySelectorAll('.toast').forEach(t => { t.querySelector('button').onclick = () => t.remove(); setTimeout(() => t.remove(), 8000); });
  d.querySelectorAll('form[data-loading]').forEach(f => f.addEventListener('submit', () => {
    const b = f.querySelector('button[type=submit]'); if (!f.checkValidity() || !b) return;
    b.dataset.t = b.textContent; b.textContent = 'Sending…'; b.disabled = true; b.setAttribute('aria-busy', 'true'); }));
  addEventListener('pageshow', () => d.querySelectorAll('button[data-t]').forEach(b => { b.textContent = b.dataset.t; b.disabled = false; b.removeAttribute('aria-busy'); }));
  d.addEventListener('submit', e => { const b = e.target.querySelector('[data-confirm]'); if (b && !confirm(b.dataset.confirm)) e.preventDefault(); });
})();

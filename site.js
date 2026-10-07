/* Commons Home Services: motion, navigation and the booking form. No libraries. */
(() => {
  const C = window.COMMONS || {};
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* header shadow + mobile booking dock after the hero scrolls away */
  const header = $('.site-header');
  const dock = $('.dock');
  const onScroll = () => {
    header && header.classList.toggle('scrolled', scrollY > 8);
    dock && dock.classList.toggle('show', scrollY > 420);
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* mobile menu + services dropdown */
  const menuBtn = $('.menu-btn'), nav = $('#nav');
  menuBtn && menuBtn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open);
  });
  $$('.nav-drop > button').forEach(b => b.addEventListener('click', () => {
    const open = b.parentElement.classList.toggle('open');
    b.setAttribute('aria-expanded', open);
  }));
  document.addEventListener('click', e => {
    $$('.nav-drop.open').forEach(d => { if (!d.contains(e.target)) { d.classList.remove('open'); d.firstElementChild.setAttribute('aria-expanded', false); } });
  });

  /* reveal on scroll, staggered within each section */
  const reveals = $$('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    reveals.forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.filter(e => e.isIntersecting).forEach((e, i) => {
        e.target.style.transitionDelay = `${Math.min(i * 80, 400)}ms`;
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => io.observe(el));
  }

  /* hero photo slideshow */
  const slides = $$('.hero-bg img');
  if (slides.length > 1 && !reduced) {
    let i = 0;
    setInterval(() => {
      slides[i].classList.remove('on');
      i = (i + 1) % slides.length;
      slides[i].classList.add('on');
    }, 6000);
  }

  /* photo carousels: swipe/scroll-snap, arrows, dots, autoplay while visible */
  $$('.carousel').forEach(car => {
    const track = $('.track', car), items = $$('.slide', track), dots = $('.dots', car);
    if (!items.length) return;
    const step = () => items[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 16);
    const maxScroll = () => track.scrollWidth - track.clientWidth - 4;
    const go = dir => {
      if (dir > 0 && track.scrollLeft >= maxScroll()) track.scrollTo({ left: 0 });
      else if (dir < 0 && track.scrollLeft <= 4) track.scrollTo({ left: track.scrollWidth });
      else track.scrollBy({ left: dir * step() });
    };
    $('.next', car).addEventListener('click', () => go(1));
    $('.prev', car).addEventListener('click', () => go(-1));
    const dotEls = items.map((_, n) => {
      const d = document.createElement('button');
      d.setAttribute('aria-label', `Photo ${n + 1}`);
      d.addEventListener('click', () => track.scrollTo({ left: n * step() }));
      dots.appendChild(d);
      return d;
    });
    const mark = () => {
      const n = Math.round(track.scrollLeft / step());
      dotEls.forEach((d, k) => d.classList.toggle('on', k === Math.min(n, dotEls.length - 1)));
    };
    track.addEventListener('scroll', () => requestAnimationFrame(mark), { passive: true });
    mark();
    const fits = () => car.classList.toggle('fits', track.scrollWidth <= track.clientWidth + 4);
    addEventListener('resize', fits); fits();
    if (reduced) return;
    let timer = null, visible = false, held = false;
    const tick = () => { if (visible && !held && !document.hidden && !car.classList.contains('fits')) go(1); };
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0.4 }).observe(car);
    ['pointerenter', 'focusin', 'touchstart'].forEach(ev => car.addEventListener(ev, () => { held = true; }, { passive: true }));
    ['pointerleave', 'focusout'].forEach(ev => car.addEventListener(ev, () => { held = false; }));
    timer = setInterval(tick, 4500);
  });

  /* booking form */
  const pad = n => String(n).padStart(2, '0');
  const tomorrow = () => { const d = new Date(); d.setDate(d.getDate() + 1); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; };
  const hourLabel = h => `${((h + 11) % 12) + 1}:00 ${h < 12 ? 'AM' : 'PM'}`;
  const prettyDate = v => new Date(v + 'T12:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  const params = new URLSearchParams(location.search);
  const svcFromUrl = params.get('service');
  const SERVICE_NAMES = {
    'junk-removal': 'Junk Removal & Hauling', 'yard-work': 'Yard Work & Cleanup', 'moving-help': 'Moving Help',
    'gutter-cleaning': 'Gutter Cleaning', 'pressure-washing': 'Pressure Washing', 'holiday-lights': 'Holiday Light Installation'
  };

  $$('.book-form').forEach(form => {
    const [first, last] = C.booking_hours || [8, 18];
    const time = form.elements.time;
    for (let h = first; h <= last; h++) time.add(new Option(hourLabel(h), hourLabel(h)));
    form.elements.date.min = tomorrow();
    if (svcFromUrl && SERVICE_NAMES[svcFromUrl] && !form.elements.service.value) form.elements.service.value = SERVICE_NAMES[svcFromUrl];
    const status = $('.form-status', form);
    const fail = msg => { status.className = 'form-status err'; status.innerHTML = `${msg} Please email <a href="mailto:${C.email}">${C.email}</a> and we'll book you in.`; };

    form.addEventListener('input', e => e.target.classList.remove('invalid'));
    form.addEventListener('submit', async e => {
      e.preventDefault();
      status.className = 'form-status'; status.textContent = '';
      const required = ['date', 'time', 'job', 'name', 'phone', 'address'].map(n => form.elements[n]);
      const missing = required.filter(el => !el.value.trim());
      required.forEach(el => el.classList.toggle('invalid', missing.includes(el)));
      if (missing.length) { status.className = 'form-status err'; status.textContent = 'Please fill in the highlighted fields.'; missing[0].focus(); return; }
      if (form.elements.date.value < form.elements.date.min) { form.elements.date.classList.add('invalid'); status.className = 'form-status err'; status.textContent = 'Please pick tomorrow or later.'; return; }
      if (form.elements.botcheck.checked) return;
      if (!C.web3forms_key) { console.error('Commons booking: CONFIG web3forms_key is empty, form cannot send.'); fail('Online booking is not connected yet.'); return; }

      const v = n => form.elements[n].value.trim();
      const when = `${prettyDate(v('date'))} at ${v('time')}`;
      const btn = $('button[type=submit]', form);
      btn.disabled = true; const label = btn.innerHTML; btn.textContent = 'Sending…';
      try {
        const res = await fetch('https://api.web3forms.com/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            access_key: C.web3forms_key,
            subject: `Booking request: ${when}${v('service') ? ' · ' + v('service') : ''}`,
            from_name: 'Commons website',
            'Requested time': when, Service: v('service') || 'Not specified', Job: v('job'),
            Name: v('name'), Phone: v('phone'), Address: v('address'), Page: location.pathname
          })
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.success) throw new Error(data.message || `HTTP ${res.status}`);
        form.classList.add('sent');
        status.className = 'form-status ok';
        status.innerHTML = '';
        const strong = document.createElement('strong');
        strong.textContent = `Request sent for ${when}.`;
        status.append(strong, document.createElement('br'), `We'll call you at ${v('phone')} to confirm.`);
      } catch (err) {
        console.error('Commons booking failed:', err);
        fail('Your request did not go through.');
      } finally {
        btn.disabled = false; btn.innerHTML = label;
      }
    });
  });

  /* crew application: same Web3Forms inbox as bookings. ?src= says which flyer or post sent them. */
  $$('.crew-form').forEach(form => {
    const minAge = +form.elements.age.min || 16;
    const status = $('.form-status', form);
    const fail = msg => { status.className = 'form-status err'; status.innerHTML = `${msg} Please email <a href="mailto:${C.email}">${C.email}</a> with your name, age, school and phone.`; };

    form.addEventListener('input', e => e.target.classList.remove('invalid'));
    form.addEventListener('submit', async e => {
      e.preventDefault();
      status.className = 'form-status'; status.textContent = '';
      const required = ['name', 'age', 'school', 'town', 'phone', 'license', 'when'].map(n => form.elements[n]);
      const missing = required.filter(el => !el.value.trim());
      required.forEach(el => el.classList.toggle('invalid', missing.includes(el)));
      if (missing.length) { status.className = 'form-status err'; status.textContent = 'Please fill in the highlighted fields.'; missing[0].focus(); return; }
      if (+form.elements.age.value < minAge) { form.elements.age.classList.add('invalid'); status.className = 'form-status err'; status.textContent = `Commons hires students ${minAge} and up.`; return; }
      if (form.elements.botcheck.checked) return;
      if (!C.web3forms_key) { console.error('Commons crew form: CONFIG web3forms_key is empty, form cannot send.'); fail('Applications are not connected yet.'); return; }

      const v = n => form.elements[n].value.trim();
      const btn = $('button[type=submit]', form);
      btn.disabled = true; const label = btn.innerHTML; btn.textContent = 'Sending…';
      try {
        const res = await fetch('https://api.web3forms.com/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            access_key: C.web3forms_key,
            subject: `Crew application: ${v('name')}, ${v('age')}, ${v('school')}`,
            from_name: 'Commons website',
            Name: v('name'), Age: v('age'), School: v('school'), Town: v('town'), Phone: v('phone'),
            "Driver's license": v('license'), 'Can work': v('when'), Note: v('note') || 'None',
            Source: params.get('src') || 'direct', Page: location.pathname
          })
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.success) throw new Error(data.message || `HTTP ${res.status}`);
        form.classList.add('sent');
        status.className = 'form-status ok';
        status.innerHTML = '';
        const strong = document.createElement('strong');
        strong.textContent = 'Thank you for your application.';
        status.append(strong, document.createElement('br'), `Will will call or text you at ${v('phone')}.`);
      } catch (err) {
        console.error('Commons crew application failed:', err);
        fail('Your application did not go through.');
      } finally {
        btn.disabled = false; btn.innerHTML = label;
      }
    });
  });

  /* reviews link not live yet: say so instead of jumping nowhere */
  $$('[data-pending="reviews"]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault();
    a.textContent = 'Google reviews are coming soon';
  }));
})();

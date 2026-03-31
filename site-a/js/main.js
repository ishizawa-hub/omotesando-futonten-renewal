/* ================================================================
   OMOTESANDO FUTONTEN - Main JavaScript
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* --- Header scroll effect --- */
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  /* --- Hamburger / Mobile Menu --- */
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      mobileMenu.classList.toggle('active');
      hamburger.classList.toggle('active');
    });
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        hamburger.classList.remove('active');
      });
    });
  }

  /* --- FAQ Accordion --- */
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const answer = item.querySelector('.faq-answer');
      const isActive = item.classList.contains('active');

      // Close all siblings in same category
      const category = item.closest('.faq-category');
      if (category) {
        category.querySelectorAll('.faq-item.active').forEach(open => {
          if (open !== item) {
            open.classList.remove('active');
            open.querySelector('.faq-answer').style.maxHeight = null;
          }
        });
      }

      // Toggle current
      item.classList.toggle('active', !isActive);
      answer.style.maxHeight = isActive ? null : answer.scrollHeight + 'px';
    });
  });

  /* --- FAQ Search / Filter --- */
  const faqSearch = document.getElementById('faq-search');
  const faqStatus = document.getElementById('faq-search-status');
  if (faqSearch) {
    faqSearch.addEventListener('input', () => {
      const query = faqSearch.value.trim().toLowerCase();
      const categories = document.querySelectorAll('.faq-category');
      let totalVisible = 0;

      categories.forEach(cat => {
        const items = cat.querySelectorAll('.faq-item');
        let catVisible = 0;

        items.forEach(item => {
          const question = item.querySelector('.faq-question').textContent.toLowerCase();
          const answer = item.querySelector('.faq-answer-inner').textContent.toLowerCase();
          const match = !query || question.includes(query) || answer.includes(query);

          item.style.display = match ? '' : 'none';
          if (match) catVisible++;
        });

        cat.style.display = catVisible > 0 ? '' : 'none';
        totalVisible += catVisible;
      });

      if (faqStatus) {
        if (query) {
          faqStatus.style.display = 'block';
          faqStatus.textContent = totalVisible > 0
            ? totalVisible + '\u4EF6\u306E\u8CEA\u554F\u304C\u898B\u3064\u304B\u308A\u307E\u3057\u305F'
            : '\u8A72\u5F53\u3059\u308B\u8CEA\u554F\u304C\u898B\u3064\u304B\u308A\u307E\u305B\u3093\u3067\u3057\u305F';
        } else {
          faqStatus.style.display = 'none';
        }
      }
    });
  }

  /* --- Tabs (Contact page, Product detail, etc.) --- */
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      const tabContainer = btn.closest('section') || btn.closest('.tabs').parentElement;
      if (!tabContainer) return;

      // Deactivate all tabs and content in this context
      tabContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      tabContainer.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      // Activate selected
      btn.classList.add('active');
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');
    });
  });

  /* --- Scroll fade-in animation --- */
  const fadeEls = document.querySelectorAll('.fade-in, .stagger');
  if (fadeEls.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    fadeEls.forEach(el => observer.observe(el));
  }

  /* --- Newsletter form (prevent default) --- */
  document.querySelectorAll('.newsletter-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      if (input && input.value) {
        const btn = form.querySelector('button');
        btn.textContent = '\u5B8C\u4E86';
        btn.style.background = 'var(--color-success)';
        input.value = '';
        setTimeout(() => {
          btn.textContent = '\u767B\u9332';
          btn.style.background = '';
        }, 2000);
      }
    });
  });

  /* --- Contact form submission (prevent default, show feedback) --- */
  document.querySelectorAll('#form-general, #form-corporate, #form-gift').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      // Basic validation
      const requiredFields = form.querySelectorAll('[required]');
      let valid = true;
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          field.style.borderColor = 'var(--color-danger)';
          valid = false;
        } else {
          field.style.borderColor = '';
        }
      });

      if (!valid) return;

      // Show success message
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = '\u9001\u4FE1\u3057\u307E\u3057\u305F';
      btn.style.background = 'var(--color-success)';
      btn.disabled = true;

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.disabled = false;
        form.reset();
      }, 3000);
    });
  });

  /* --- Smooth scroll for anchor links --- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});

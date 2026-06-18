/* EngineSwap Autos — main.js */

const CART_KEY = 'esa_cart';

/* ══════════════════════════════════════════════════════
   CART STORAGE HELPERS
   ══════════════════════════════════════════════════════ */
function getCart()           { return JSON.parse(localStorage.getItem(CART_KEY) || '[]'); }
function saveCart(cart)      { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }
function cartTotal(cart)     { return cart.reduce((s, i) => s + i.price * i.qty, 0); }
function cartCount(cart)     { return cart.reduce((s, i) => s + i.qty, 0); }

/* ══════════════════════════════════════════════════════
   ADD TO CART — core function + event delegation
   ══════════════════════════════════════════════════════ */
function addToCart(slug, name, price, image, year, fuel) {
  const cart = getCart();
  const ex   = cart.find(i => i.slug === slug);
  if (ex) { ex.qty += 1; }
  else     { cart.push({ slug, name, price: parseFloat(price), image, year: parseInt(year) || 0, fuel, qty: 1 }); }
  saveCart(cart);
  updateBadges(cart);
  renderCartDrawer(cart);
  openCart();
  showToast(name + ' added to cart');
}

// Event delegation — works for all .btn-cart-sm buttons anywhere in the DOM
document.addEventListener('click', function(e) {
  const btn = e.target.closest('.btn-cart-sm');
  if (!btn || btn.disabled) return;
  e.stopPropagation();
  addToCart(
    btn.dataset.slug,
    btn.dataset.name,
    btn.dataset.price,
    btn.dataset.image,
    btn.dataset.year,
    btn.dataset.fuel
  );
});

/* ══════════════════════════════════════════════════════
   CART DRAWER OPEN / CLOSE
   ══════════════════════════════════════════════════════ */
function openCart() {
  renderCartDrawer(getCart());
  document.getElementById('cart-drawer').classList.add('open');
  document.getElementById('cart-overlay-bg').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeCart() {
  document.getElementById('cart-drawer').classList.remove('open');
  document.getElementById('cart-overlay-bg').classList.remove('show');
  document.body.style.overflow = '';
}

/* ══════════════════════════════════════════════════════
   RENDER CART DRAWER
   ══════════════════════════════════════════════════════ */
function renderCartDrawer(cart) {
  const itemsEl   = document.getElementById('cart-drawer-items');
  const emptyEl   = document.getElementById('cart-empty-msg');
  const footEl    = document.getElementById('cart-drawer-foot');
  const subtotalEl= document.getElementById('cart-subtotal');
  const shippingEl= document.getElementById('cart-shipping');
  const shipNoteEl= document.getElementById('cart-ship-note');
  const totalEl   = document.getElementById('cart-total');

  if (!itemsEl) return;

  if (!cart.length) {
    itemsEl.innerHTML = '';
    if (emptyEl) { emptyEl.style.display = 'block'; itemsEl.appendChild(emptyEl); }
    if (footEl) footEl.style.display = 'none';
    return;
  }

  if (emptyEl) { emptyEl.style.display = 'none'; }
  if (footEl) footEl.style.display = 'block';

  const subtotal = cartTotal(cart);
  const shipping = subtotal >= 5000 ? 0 : (subtotal > 0 ? 500 : 0);
  const total    = subtotal + shipping;

  // Build items HTML
  itemsEl.innerHTML = cart.map(item => `
    <div class="cart-item">
      <img class="cart-item-img"
           src="${escHtml(item.image)}"
           alt="${escHtml(item.name)}"
           onerror="this.src='https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=200&q=50'">
      <div class="cart-item-info">
        <div class="cart-item-name">${escHtml(item.name)}</div>
        <div class="cart-item-sub">${item.year} &bull; ${escHtml(item.fuel)}</div>
        <div class="qty-row">
          <button class="qty-btn" onclick="changeQty('${item.slug}', -1)">&#8722;</button>
          <span class="qty-num">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty('${item.slug}', 1)">+</button>
        </div>
        <div class="cart-item-price">$${(item.price * item.qty).toLocaleString()}</div>
      </div>
      <button class="cart-remove-btn" onclick="removeFromCart('${item.slug}')" title="Remove">&#x2715;</button>
    </div>
  `).join('');

  // Totals
  if (subtotalEl) subtotalEl.textContent = '$' + subtotal.toLocaleString();
  if (shippingEl) shippingEl.textContent = shipping === 0 ? 'FREE' : '$' + shipping.toLocaleString();
  if (shipNoteEl) {
    shipNoteEl.textContent = shipping === 0
      ? 'Free shipping applied to your order'
      : 'Add $' + (5000 - subtotal).toLocaleString() + ' more for free shipping';
    shipNoteEl.style.color = shipping === 0 ? '#28a745' : '#e87722';
  }
  if (totalEl) totalEl.textContent = '$' + total.toLocaleString();
}

/* ══════════════════════════════════════════════════════
   QTY / REMOVE
   ══════════════════════════════════════════════════════ */
function changeQty(slug, delta) {
  const cart = getCart();
  const item = cart.find(i => i.slug === slug);
  if (!item) return;
  item.qty = Math.max(1, item.qty + delta);
  saveCart(cart);
  updateBadges(cart);
  renderCartDrawer(cart);
}

function removeFromCart(slug) {
  const cart = getCart().filter(i => i.slug !== slug);
  saveCart(cart);
  updateBadges(cart);
  renderCartDrawer(cart);
}

/* ══════════════════════════════════════════════════════
   CART BADGE
   ══════════════════════════════════════════════════════ */
function updateBadges(cart) {
  const count = cartCount(cart);
  document.querySelectorAll('.cart-count-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
}

/* ══════════════════════════════════════════════════════
   TOAST
   ══════════════════════════════════════════════════════ */
function showToast(msg) {
  let el = document.getElementById('site-toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 3000);
}

/* ══════════════════════════════════════════════════════
   ESCAPE HTML
   ══════════════════════════════════════════════════════ */
function escHtml(str) {
  return String(str || '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ══════════════════════════════════════════════════════
   DOM READY — init
   ══════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {

  /* 1. Cart badge on every page */
  updateBadges(getCart());

  /* 2. Active category nav link */
  const path      = window.location.pathname;
  const urlParams = new URLSearchParams(window.location.search);
  const catParam  = urlParams.get('category') || '';

  document.querySelectorAll('.cat-nav-link').forEach(link => {
    const href     = link.getAttribute('href') || '';
    const lp       = new URLSearchParams(href.split('?')[1] || '');
    const lCat     = lp.get('category') || '';
    const lPath    = href.split('?')[0];

    if (lPath === '/products' && lCat === '' && path === '/products' && catParam === '') {
      link.classList.add('active');
    } else if (lCat && lCat === catParam) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });

  /* 3. Navbar search */
  const searchForm = document.getElementById('nav-search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', function (e) {
      const q = (document.getElementById('nav-search-input').value || '').trim();
      if (!q) e.preventDefault();
    });
  }

  /* 4. Products page live filter */
  const filterSearch = document.getElementById('filter-search');
  const filterCat    = document.getElementById('filter-category');
  const cards        = document.querySelectorAll('.product-card[data-name]');
  const resultEl     = document.getElementById('result-count');

  if ((filterSearch || filterCat) && cards.length) {
    if (filterSearch && urlParams.get('q'))        filterSearch.value = urlParams.get('q');
    if (filterCat    && urlParams.get('category')) filterCat.value    = urlParams.get('category');

    function applyFilters() {
      const q   = filterSearch ? filterSearch.value.toLowerCase().trim() : '';
      const cat = filterCat    ? filterCat.value.toLowerCase().trim()    : '';
      let visible = 0;
      cards.forEach(card => {
        const matchQ   = !q   || (card.dataset.name||'').includes(q) || (card.dataset.brand||'').includes(q);
        const matchCat = !cat || (card.dataset.category||'') === cat;
        card.style.display = (matchQ && matchCat) ? '' : 'none';
        if (matchQ && matchCat) visible++;
      });
      // count hidden per user preference
    }

    applyFilters();
    if (filterSearch) filterSearch.addEventListener('keyup', applyFilters);
    if (filterCat)    filterCat.addEventListener('change', applyFilters);
  }

  /* 5. Mobile hamburger */
  const hamburger  = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu-panel');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
  }

  /* 6. Navbar cart icon opens drawer */
  const navCartBtn = document.querySelector('.btn-cart');
  if (navCartBtn) {
    navCartBtn.addEventListener('click', function(e) {
      e.preventDefault();
      openCart();
    });
  }
});

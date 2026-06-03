/* CryptoPulse archive templates. Each fn returns INNER markup; the shared
   engine wraps it in the <a href>. Helpers: window.__AA_HELP.esc / .fallback /
   .siteCat. cardClass/secClass set the wrapper anchor's class. */
window.AA = {
  cardClass: 'cpx-row',
  secClass: 'cpx-sec-item',
  perPage: 24,
  card: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<img class="cpx-row-thumb" loading="lazy" alt="" src="' + img +
      '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'">' +
      '<div class="cpx-row-main"><span class="cpx-row-cat">' + H.esc(p.category || H.siteCat) + '</span>' +
      '<h3 class="cpx-row-h">' + H.esc(p.title || 'Untitled') + '</h3>' +
      '<p class="cpx-row-desc">' + H.esc(p.meta_description || '') + '</p></div>' +
      '<span class="cpx-row-date">' + H.esc(p.date_iso || '') + '</span>';
  },
  lead: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<img class="cpx-lead-img" loading="lazy" alt="" src="' + img +
      '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'">' +
      '<div class="cpx-lead-body"><span class="cpx-row-cat">' + H.esc(p.category || H.siteCat) + '</span>' +
      '<h2 class="cpx-lead-h">' + H.esc(p.title || 'Untitled') + '</h2>' +
      '<p class="cpx-lead-desc">' + H.esc(p.meta_description || '') + '</p>' +
      '<span class="cpx-row-date">' + H.esc(p.date_iso || '') + '</span></div>';
  },
  sec: function (p) {
    var H = window.__AA_HELP;
    return '<span class="cpx-sec-date">' + H.esc(p.date_iso || '') + '</span>' +
      '<h3 class="cpx-sec-h">' + H.esc(p.title || 'Untitled') + '</h3>';
  }
};

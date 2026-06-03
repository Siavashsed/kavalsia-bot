/* Dalmend Home archive templates - "Editorial Lookbook".
   Refined interiors/architecture magazine: serif display headlines, big lead
   image, asymmetric featured block, airy 3-up grid. Each fn returns INNER
   markup only; the shared engine wraps it in the <a href>. Helpers:
   window.__AA_HELP.esc / .fallback / .siteCat. */
window.AA = {
  cardClass: 'dh-card',
  secClass: 'dh-edit-item',
  perPage: 24,
  card: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<figure class="dh-card-figure">' +
      '<img class="dh-card-img" loading="lazy" alt="" src="' + img +
      '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'">' +
      '</figure>' +
      '<div class="dh-card-body">' +
      '<span class="dh-card-cat">' + H.esc(p.category || H.siteCat) + '</span>' +
      '<h3 class="dh-card-h">' + H.esc(p.title || 'Untitled') + '</h3>' +
      '<p class="dh-card-desc">' + H.esc(p.meta_description || '') + '</p>' +
      '<span class="dh-card-foot">' + H.esc(p.author || '') +
      (p.author && p.date_iso ? '<span class="dh-dot"></span>' : '') +
      H.esc(p.date_iso || '') + '</span>' +
      '</div>';
  },
  lead: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<figure class="dh-lead-figure">' +
      '<img class="dh-lead-img" loading="lazy" alt="" src="' + img +
      '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'">' +
      '</figure>' +
      '<div class="dh-lead-body">' +
      '<span class="dh-lead-cat">' + H.esc(p.category || H.siteCat) + '</span>' +
      '<h2 class="dh-lead-h">' + H.esc(p.title || 'Untitled') + '</h2>' +
      '<p class="dh-lead-desc">' + H.esc(p.meta_description || '') + '</p>' +
      '<span class="dh-lead-foot">' +
      (p.author ? 'Words by ' + H.esc(p.author) : 'From the archive') +
      (p.date_iso ? '<span class="dh-dot"></span>' + H.esc(p.date_iso) : '') +
      '</span>' +
      '</div>';
  },
  sec: function (p) {
    var H = window.__AA_HELP;
    return '<span class="dh-edit-num" aria-hidden="true"></span>' +
      '<div class="dh-edit-text">' +
      '<span class="dh-edit-cat">' + H.esc(p.category || H.siteCat) + '</span>' +
      '<h3 class="dh-edit-h">' + H.esc(p.title || 'Untitled') + '</h3>' +
      '<span class="dh-edit-date">' + H.esc(p.date_iso || '') + '</span>' +
      '</div>';
  }
};

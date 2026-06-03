/* MochaPoo Pets archive templates - "warm rounded magazine".
   Each fn returns INNER markup only; the shared engine wraps it in the <a href>
   and sets #aa-lead's href + innerHTML. Helpers: window.__AA_HELP.esc /
   .fallback / .siteCat. cardClass / secClass set the wrapper anchor's class. */
window.AA = {
  cardClass: 'mp-card',
  secClass: 'mp-sec',
  perPage: 24,
  card: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<div class="mp-card-media">' +
      '<img class="mp-card-img" src="' + img + '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'" loading="lazy" alt="">' +
      '<span class="mp-card-cat">' + H.esc(p.category || H.siteCat) + '</span></div>' +
      '<div class="mp-card-body">' +
      '<h3 class="mp-card-h">' + H.esc(p.title || 'Untitled') + '</h3>' +
      '<p class="mp-card-desc">' + H.esc(p.meta_description || '') + '</p>' +
      '<div class="mp-card-foot"><span class="mp-card-date">' + H.esc(p.date_iso || '') + '</span>' +
      '<span class="mp-card-by">' + H.esc(p.author || '') + '</span></div></div>';
  },
  lead: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<div class="mp-lead-media">' +
      '<img class="mp-lead-img" src="' + img + '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'" loading="lazy" alt="">' +
      '<span class="mp-card-cat mp-lead-cat">' + H.esc(p.category || H.siteCat) + '</span></div>' +
      '<div class="mp-lead-body">' +
      '<h2 class="mp-lead-h">' + H.esc(p.title || 'Untitled') + '</h2>' +
      '<p class="mp-lead-desc">' + H.esc(p.meta_description || '') + '</p>' +
      '<div class="mp-card-foot"><span class="mp-card-date">' + H.esc(p.date_iso || '') + '</span>' +
      '<span class="mp-card-by">' + H.esc(p.author || '') + '</span></div></div>';
  },
  sec: function (p) {
    var H = window.__AA_HELP, img = H.esc(p.image || H.fallback);
    return '<img class="mp-sec-thumb" src="' + img + '" onerror="this.onerror=null;this.src=\'' + H.fallback + '\'" loading="lazy" alt="">' +
      '<div class="mp-sec-main"><h3 class="mp-sec-h">' + H.esc(p.title || 'Untitled') + '</h3>' +
      '<span class="mp-sec-date">' + H.esc(p.date_iso || '') + '</span></div>';
  }
};

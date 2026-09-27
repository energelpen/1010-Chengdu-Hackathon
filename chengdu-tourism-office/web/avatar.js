/* Generated fictional portraits. Speech stays in the browser. */
(function () {
  "use strict";

  const states = new Set(["idle", "thinking", "listening", "speaking"]);
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  function hash(value) {
    return Array.from(String(value)).reduce((total, ch) => ((total * 31 + ch.charCodeAt(0)) >>> 0), 7);
  }
  function markup(person, options) {
    person = person || { id: "atlas", name: "Atlas" };
    options = options || {};
    const personId = String(person.id || "atlas");
    const presets = ["atlas","director","sales_manager","sales_exec","account_exec","product_manager","itinerary_specialist","supplier_manager","ops_manager","transport_coordinator","finance_manager"];
    const portrait = presets.includes(person.portrait) ? person.portrait : presets.includes(personId) ? personId : presets[1 + hash(personId) % (presets.length - 1)];
    const portraitSize = ["small","medium","large"].includes(options.size) ? options.size : "medium";
    return `<span class="atlas-avatar atlas-avatar--${portraitSize} generated-avatar" data-avatar-id="${escape(personId)}" data-state="idle" role="img" aria-label="${escape(person.name || "Atlas")}, fictional AI colleague"><img src="/portraits/${portrait}.png" alt="" loading="lazy"><span class="avatar-signal"></span></span>`;
  }
  function setState(personId, state) {
    const nextState = states.has(state) ? state : "idle";
    document.querySelectorAll(".atlas-avatar[data-avatar-id]").forEach((node) => {
      if (node.getAttribute("data-avatar-id") === String(personId)) node.dataset.state = nextState;
    });
  }
  function stop() {
    document.querySelectorAll(".atlas-avatar[data-avatar-id]").forEach((node) => { node.dataset.state = "idle"; });
  }
  window.AtlasAvatar = Object.freeze({ markup, setState, stop });
})();

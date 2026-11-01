/* Exploración opcional: el informe y los requisitos siguen legibles sin JavaScript. */
(() => {
  "use strict";
  if (!document.body.classList.contains("pagina-prueba")) return;
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const activeAnimations = new Map();
  const canAnimate = typeof Element.prototype.animate === "function";
  const animate = (element, delay = 0) => {
    if (!canAnimate || motion.matches || document.hidden || element.contains(document.activeElement)) return;
    activeAnimations.get(element)?.cancel();
    const animation = element.animate(
      [{ opacity: .25, transform: "translateY(12px)" }, { opacity: 1, transform: "translateY(0)" }],
      { duration: 420, delay, easing: "cubic-bezier(.2,.7,.2,1)", fill: "backwards" }
    );
    activeAnimations.set(element, animation);
    const release = () => {
      if (activeAnimations.get(element) === animation) activeAnimations.delete(element);
    };
    animation.finished.then(release, release);
  };
  const cancelAnimations = () => {
    activeAnimations.forEach((animation) => animation.cancel());
    activeAnimations.clear();
  };

  const selector = document.querySelector(".prueba-selector");
  const buttons = [...selector.querySelectorAll("[data-campo]")];
  const fields = [...document.querySelectorAll("[data-informe-campo]")];
  const note = document.querySelector("[data-informe-nota]");
  const paper = document.querySelector(".prueba-papel");
  const mobileReport = window.matchMedia("(max-width: 760px)");
  // En móvil, la explicación debe aparecer junto al control que se acaba de tocar.
  const placeNote = () => (mobileReport.matches ? selector : paper).append(note);
  placeNote();
  mobileReport.addEventListener("change", placeNote);
  const explanations = {
    concepto: "El concepto y su código permiten identificar cada glosa dentro del Manual Único de Devoluciones, Glosas y Respuestas.",
    caracter: "El carácter permite distinguir una glosa definitiva, una condicional o una observación durante la revisión.",
    valor: "El informe vincula el valor de cada glosa con su concepto para facilitar la comparación con la revisión de tu equipo.",
    soporte: "La cita del soporte conecta la glosa con la evidencia documental que revisa el auditor médico."
  };
  const selectField = (button, animated = true) => {
    const selected = button.dataset.campo;
    buttons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    fields.forEach((field) => {
      const active = field.dataset.informeCampo === selected;
      field.classList.toggle("is-active", active);
      if (active && animated) animate(field);
    });
    note.textContent = explanations[selected];
    if (animated && mobileReport.matches) {
      selector.scrollIntoView({ block: "nearest", behavior: motion.matches ? "instant" : "smooth" });
    }
  };
  buttons.forEach((button, index) => {
    button.addEventListener("click", () => selectField(button));
    button.addEventListener("keydown", (event) => {
      const row = mobileReport.matches ? 2 : 1;
      const direction = { ArrowDown: row, ArrowRight: 1, ArrowUp: -row, ArrowLeft: -1 }[event.key];
      if (!direction) return;
      event.preventDefault();
      const next = buttons[(index + direction + buttons.length) % buttons.length];
      next.focus();
      selectField(next);
    });
  });
  selectField(buttons[0], false);
  selector.hidden = false;

  // Apariciones únicas, sin ocultar contenido mediante CSS ni animar la portada.
  // La lista de requisitos ya usa la animación compartida de site.js.
  let observer;
  const seen = new WeakSet();
  const targets = [...document.querySelectorAll("[data-prueba-entrada]")];
  const observe = () => {
    observer?.disconnect();
    cancelAnimations();
    if (motion.matches || !canAnimate || document.hidden || !("IntersectionObserver" in window)) return;
    observer = new IntersectionObserver((entries) => {
      let delay = 0;
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (seen.has(entry.target)) return;
        seen.add(entry.target);
        if (entry.boundingClientRect.top < 0) return;
        animate(entry.target, delay);
        delay = Math.min(delay + 90, 270);
      });
    }, { threshold: 0, rootMargin: "0px 0px -40px 0px" });
    targets.forEach((target) => {
      if (target.getBoundingClientRect().top < window.innerHeight) seen.add(target);
      if (!seen.has(target)) observer.observe(target);
    });
  };
  document.addEventListener("focusin", (event) => {
    targets.forEach((target) => {
      if (!target.contains(event.target)) return;
      seen.add(target);
      observer?.unobserve(target);
      activeAnimations.get(target)?.cancel();
    });
  });
  window.addEventListener("pageshow", () => requestAnimationFrame(observe));
  window.addEventListener("hashchange", observe);
  window.addEventListener("pagehide", () => { observer?.disconnect(); cancelAnimations(); });
  window.addEventListener("beforeprint", () => { observer?.disconnect(); cancelAnimations(); });
  window.addEventListener("afterprint", observe);
  document.addEventListener("visibilitychange", observe);
  motion.addEventListener("change", observe);
})();

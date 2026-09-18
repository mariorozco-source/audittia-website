/* Mejora progresiva: sin dependencias, seguimiento ni almacenamiento local. */
(() => {
  "use strict";
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const activeAnimations = new Set();
  const canAnimate = typeof Element.prototype.animate === "function";
  const ease = "cubic-bezier(.2,.7,.2,1)";

  // Sólo opacity/transform: sin alterar el flujo de lectura ni ocultar contenido
  // mediante CSS. Una animación cancelada vuelve al estado visible de base.
  const reveal = (element, { delay = 0, duration = 440, distance = 12 } = {}) => {
    if (!element || !canAnimate || motion.matches || element.contains(document.activeElement)) return;
    const animation = element.animate(
      [
        { opacity: 0.55, transform: `translateY(${distance}px)` },
        { opacity: 1, transform: "translateY(0)" }
      ],
      { duration, delay, easing: ease }
    );
    activeAnimations.add(animation);
    animation.finished.then(
      () => activeAnimations.delete(animation),
      () => activeAnimations.delete(animation)
    );
  };

  const menu = document.querySelector(".menu-movil");
  if (menu) {
    const summary = menu.querySelector("summary");
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.open) {
        menu.open = false;
        summary.focus();
      }
    });
    document.addEventListener("click", (event) => {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => { menu.open = false; });
    });
    menu.addEventListener("toggle", () => {
      if (menu.open) reveal(menu.querySelector("nav"), { duration: 180, distance: -5 });
    });
    const desktop = window.matchMedia("(min-width: 1101px)");
    desktop.addEventListener("change", () => {
      if (desktop.matches) menu.open = false;
    });
  }

  document.querySelectorAll(".preguntas details").forEach((detail) => {
    detail.addEventListener("toggle", () => {
      if (detail.open) reveal(detail.querySelector(".pregunta__respuesta"), { duration: 220, distance: -4 });
    });
  });

  let observer;
  if (!motion.matches && canAnimate) {
    // Una entrada breve del hero, sólo al entrar desde arriba. No interfiere
    // con enlaces a secciones ni restaura desplazamientos del navegador.
    if (!window.location.hash && window.scrollY < 20 && document.visibilityState === "visible") {
      const heroItems = document.querySelectorAll(
        ".hero__contenido > *, .hero-pagina__interior > :first-child > :not(.migas), .hero--interior > .contenedor > :not(.migas)"
      );
      heroItems.forEach((element, index) => reveal(element, {
        delay: Math.min(index * 35, 140), duration: 480, distance: 10
      }));
      const visual = document.querySelector(".hero__visual, .hero-pagina__interior > :last-child");
      if (visual) reveal(visual, { delay: 70, duration: 580, distance: 14 });
    }

    // Cada bloque aparece una sola vez. Retraso acotado entre hermanos;
    // sin parallax, zoom de fotografías ni animaciones infinitas.
    if ("IntersectionObserver" in window) {
      const stagger = new WeakMap();
      observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          observer.unobserve(entry.target);
          reveal(entry.target, { delay: stagger.get(entry.target) || 0 });
        });
      }, { threshold: 0.1 });
      document.querySelectorAll(
        ".acceso, .encabezado-seccion, .encabezado-horizontal, .flujo-resumen li, .foto-editorial, .tarjetas-entidad article, .contacto, .paso, .hallazgo, .perfil-ampliado, .bloque-datos, .tarjetas-roles article, .miembro, .principios-editoriales article, .tarjetas-recursos article, .glosario__termino, .tarjeta-documento"
      ).forEach((element) => {
        if (element.getBoundingClientRect().top <= window.innerHeight) return;
        const index = Array.prototype.indexOf.call(element.parentElement.children, element);
        stagger.set(element, Math.min(index % 3, 2) * 45);
        observer.observe(element);
      });
    }
  }

  motion.addEventListener("change", () => {
    if (!motion.matches) return;
    observer?.disconnect();
    activeAnimations.forEach((animation) => animation.cancel());
    activeAnimations.clear();
  });
})();

/* Mejora progresiva: sin dependencias, seguimiento ni almacenamiento local. */
(() => {
  "use strict";
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const activeAnimations = new Map();
  const canAnimate = typeof Element.prototype.animate === "function";
  const ease = "cubic-bezier(.2,.7,.2,1)";

  document.querySelectorAll("video[data-video-ambiental]").forEach((video) => {
    if (!("IntersectionObserver" in window)) return;
    const fallback = video.parentElement.querySelector("[data-video-fallback]");
    let visible = false;
    let failed = false;
    let restartTimer;
    const clearRestart = () => {
      window.clearTimeout(restartTimer);
      restartTimer = undefined;
    };
    const canPlay = () => visible && !document.hidden && !failed && !motion.matches;
    const play = () => {
      video.play().then(() => {
        if (!canPlay()) video.pause();
      }).catch(() => { /* Si se bloquea autoplay, permanece la portada. */ });
    };
    const syncPlayback = () => {
      video.hidden = failed || motion.matches;
      fallback.hidden = !video.hidden;
      if (!canPlay()) {
        clearRestart();
        video.pause();
        return;
      }
      if (video.ended) {
        // Mantener el último fotograma durante cinco segundos, sin recargar el MP4.
        if (restartTimer !== undefined) return;
        restartTimer = window.setTimeout(() => {
          restartTimer = undefined;
          if (!canPlay()) return;
          video.currentTime = 0;
          play();
        }, 5000);
      } else play();
    };
    const videoObserver = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting && entry.intersectionRatio >= 0.2;
      syncPlayback();
    }, { threshold: [0, 0.2] });
    videoObserver.observe(video.parentElement);
    video.addEventListener("ended", syncPlayback);
    const showFallback = () => {
      failed = true;
      syncPlayback();
      videoObserver.disconnect();
    };
    video.addEventListener("error", showFallback);
    video.querySelector("source").addEventListener("error", showFallback);
    document.addEventListener("visibilitychange", syncPlayback);
    window.addEventListener("pagehide", () => { clearRestart(); video.pause(); });
    window.addEventListener("pageshow", syncPlayback);
    motion.addEventListener("change", syncPlayback);
    syncPlayback();
  });

  // Sólo opacity/transform: sin alterar el flujo de lectura ni ocultar contenido
  // mediante CSS. Una animación cancelada vuelve al estado visible de base.
  const reveal = (element, { duration = 480, distance = 18, delay = 0, opacity = 0 } = {}) => {
    if (!element) return;
    element.classList.remove("motion-pending");
    if (!canAnimate || motion.matches || document.hidden || element.contains(document.activeElement)) return;
    activeAnimations.get(element)?.cancel();
    const animation = element.animate(
      [
        { opacity, transform: `translateY(${distance}px)` },
        { opacity: 1, transform: "translateY(0)" }
      ],
      { duration, delay, easing: ease, fill: "backwards" }
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
  document.addEventListener("focusin", (event) => {
    // Un enlace enfocado nunca espera a que termine una secuencia visual.
    targets.forEach((element) => {
      if (!element.contains(event.target)) return;
      element.classList.remove("motion-pending");
      seen.add(element);
      observer?.unobserve(element);
    });
    activeAnimations.forEach((animation, element) => {
      if (element.contains(event.target)) animation.cancel();
    });
  });

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
      if (menu.open) reveal(menu.querySelector("nav"), { duration: 160, distance: 0, opacity: 0.85 });
      else activeAnimations.get(menu.querySelector("nav"))?.cancel();
    });
    const desktop = window.matchMedia("(min-width: 1101px)");
    desktop.addEventListener("change", () => {
      if (desktop.matches) menu.open = false;
    });
  }

  document.querySelectorAll(".preguntas details").forEach((detail) => {
    detail.addEventListener("toggle", () => {
      const answer = detail.querySelector(".pregunta__respuesta");
      if (detail.open) reveal(answer, { duration: 180, distance: 0, opacity: 0.85 });
      else activeAnimations.get(answer)?.cancel();
    });
  });

  // La cabecera y el primer viewport se muestran inmediatamente en cada ruta.
  // Los bloques editoriales entran juntos, sin animar padres e hijos a la vez.
  const selector = ".acceso, .encabezado-seccion, .encabezado-horizontal, .metodo-resumen > div, .flujo-resumen li, .foto-editorial, .editorial-personas > div, .preguntas-inicio > div, .tarjetas-entidad article, .contacto, .paso, .hallazgo, .perfil-ampliado, .bloque-datos, .tarjetas-roles article, .miembro, .principios-editoriales article, .tarjetas-recursos article, .glosario__termino, .tarjeta-documento, .franja-mision__interior, .bloque-editorial__texto, .mosaico-beneficios article, .historia-metodo__cabecera, .historia-metodo li, .aviso-importante, .comparacion-seguridad, .lista-numerada, .preguntas, .orbita-documental, .proteccion-ejemplo";
  const targets = [...document.querySelectorAll(selector)].filter((element) =>
    !element.closest(".hero, .hero-pagina, .hero--interior") && !element.parentElement.closest(selector)
  );
  const seen = new WeakSet();
  const pending = new Set();
  const clearPending = () => {
    pending.forEach((element) => element.classList.remove("motion-pending"));
    pending.clear();
  };
  let observer;
  let lastScrollY = window.scrollY;
  let scrollingDown = false;
  window.addEventListener("scroll", () => {
    scrollingDown = window.scrollY > lastScrollY;
    lastScrollY = window.scrollY;
  }, { passive: true });

  const observeBlocks = () => {
    observer?.disconnect();
    cancelAnimations();
    clearPending();
    lastScrollY = window.scrollY;
    scrollingDown = false;
    if (motion.matches || !canAnimate || !("IntersectionObserver" in window) || document.hidden) return;
    const nextStart = new WeakMap();
    observer = new IntersectionObserver((entries) => {
      // Orden DOM incluso si varios pasos entran en el viewport en el mismo frame.
      entries.sort((a, b) => targets.indexOf(a.target) - targets.indexOf(b.target));
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        if (seen.has(entry.target)) return;
        seen.add(entry.target);
        pending.delete(entry.target);
        entry.target.classList.remove("motion-pending");
        // Una vez visto, no se repite al subir o volver sobre el mismo bloque.
        if (!scrollingDown || entry.boundingClientRect.top < 0) return;
        const parent = entry.target.parentElement;
        const isProcess = parent.matches(".flujo-resumen, .pasos, .historia-metodo ol");
        const isGroup = isProcess || parent.matches(".accesos__rejilla, .tarjetas-entidad, .cuadricula-tarjetas, .bloques-datos, .tarjetas-roles, .equipo, .principios-editoriales, .tarjetas-recursos, .mosaico-beneficios, .glosario");
        const now = performance.now();
        const delay = isGroup ? Math.min(480, Math.max(0, (nextStart.get(parent) || now) - now)) : 0;
        if (isGroup) nextStart.set(parent, now + delay + (isProcess ? 200 : 100));
        reveal(entry.target, {
          delay,
          duration: isProcess ? 560 : 480,
          distance: isProcess ? 22 : 18
        });
      });
    }, { threshold: 0, rootMargin: "0px 0px -64px 0px" });
    targets.forEach((element) => {
      if (element.getBoundingClientRect().top <= window.innerHeight) seen.add(element);
      if (!seen.has(element)) {
        observer.observe(element);
        element.classList.add("motion-pending");
        pending.add(element);
      }
    });
  };

  // Esperar la restauración nativa del scroll, sin animar la llegada a una página.
  window.addEventListener("pageshow", () => requestAnimationFrame(observeBlocks));
  window.addEventListener("hashchange", observeBlocks);
  let viewportWidth = window.innerWidth;
  window.addEventListener("resize", () => {
    // La barra del navegador móvil cambia la altura durante el scroll.
    // No reiniciar la secuencia por ese cambio; sí al cambiar el diseño.
    if (window.innerWidth === viewportWidth) return;
    viewportWidth = window.innerWidth;
    observeBlocks();
  });
  window.addEventListener("pagehide", () => { observer?.disconnect(); cancelAnimations(); clearPending(); });
  window.addEventListener("beforeprint", () => { observer?.disconnect(); cancelAnimations(); clearPending(); });
  window.addEventListener("afterprint", observeBlocks);
  document.addEventListener("visibilitychange", observeBlocks);

  motion.addEventListener("change", observeBlocks);
})();

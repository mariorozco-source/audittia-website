/* Recorrido ilustrativo: no envía datos ni acciona una aplicación real. */
(() => {
  "use strict";
  const demo = document.querySelector(".mockup-producto");
  if (!demo || !("IntersectionObserver" in window) || !Element.prototype.animate) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const body = demo.querySelector(".mockup-producto__cuerpo");
  const cursor = demo.querySelector(".mockup-producto__cursor");
  const tabs = [...body.querySelectorAll("aside span")];
  const heading = demo.querySelector(".mockup-producto__estado > span");
  const detail = demo.querySelector(".mockup-producto__hallazgo > span");
  const lines = demo.querySelector(".mockup-producto__lineas");
  const originalHeading = heading.textContent;
  const originalDetail = detail.textContent;
  const descriptions = ["Factura y soportes", "Contexto y soporte", "Órdenes y registro", "Autorización y orden", "Registro y factura"];
  const duration = 4900;
  const firstClick = 750;
  const step = 850;
  let timeline;
  let panelMotion;
  let frame;
  let visible = false;
  let finished = false;
  let selected = -1;

  const select = (index, animate = true) => {
    tabs.forEach((tab, i) => tab.classList.toggle("activo", i === index));
    heading.textContent = tabs[index].textContent;
    detail.textContent = descriptions[index];
    panelMotion?.cancel();
    if (animate) panelMotion = lines.animate([
      { opacity: 0.35, transform: "translateY(3px)" },
      { opacity: 1, transform: "translateY(0)" }
    ], { duration: 240, easing: "ease-out" });
  };
  const finish = () => {
    finished = true;
    cancelAnimationFrame(frame);
    timeline?.cancel();
    panelMotion?.cancel();
  };
  const tick = () => {
    const time = Number(timeline.currentTime) || 0;
    const index = Math.min(tabs.length - 1, Math.floor((time - firstClick) / step));
    if (index >= 0 && index !== selected) {
      selected = index;
      select(index);
    }
    if (timeline.playState === "running") frame = requestAnimationFrame(tick);
  };
  const buildTimeline = (time = 0) => {
    const rect = body.getBoundingClientRect();
    const points = tabs.map((tab) => {
      const box = tab.getBoundingClientRect();
      return { x: box.left - rect.left + box.width * 0.68, y: box.top - rect.top + box.height * 0.55 };
    });
    const pose = (point, scale = 1) => `translate(${point.x}px, ${point.y}px) scale(${scale})`;
    const start = { x: rect.width * 0.65, y: rect.height * 0.65 };
    const frames = [
      { offset: 0, opacity: 0, transform: pose(start) },
      { offset: 250 / duration, opacity: 1, transform: pose(start) }
    ];
    points.forEach((point, index) => {
      const click = firstClick + index * step;
      frames.push(
        { offset: (click - 80) / duration, opacity: 1, transform: pose(point) },
        { offset: click / duration, opacity: 1, transform: pose(point, 0.82) },
        { offset: (click + 100) / duration, opacity: 1, transform: pose(point) },
        { offset: (click + 430) / duration, opacity: 1, transform: pose(point) }
      );
    });
    frames.push({ offset: 1, opacity: 0, transform: pose(points.at(-1)) });
    timeline?.cancel();
    timeline = cursor.animate(frames.map((frame) => ({ ...frame, easing: "cubic-bezier(.2,.7,.2,1)" })), { duration, fill: "both" });
    timeline.pause();
    timeline.currentTime = time;
    timeline.onfinish = () => {
      select(tabs.length - 1, false);
      finish();
    };
  };
  const sync = () => {
    cancelAnimationFrame(frame);
    if (reduced.matches) {
      if (!timeline) return;
      finish();
      tabs.forEach((tab, i) => tab.classList.toggle("activo", i === 0));
      heading.textContent = originalHeading;
      detail.textContent = originalDetail;
      return;
    }
    if (finished) return;
    if (!visible || document.hidden) {
      timeline?.pause();
      panelMotion?.pause();
      return;
    }
    if (!timeline) buildTimeline();
    timeline.play();
    if (panelMotion?.playState === "paused") panelMotion.play();
    tick();
  };
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting && entry.intersectionRatio >= 0.55;
    sync();
  }, { threshold: [0, 0.55] }).observe(demo);
  document.addEventListener("visibilitychange", sync);
  window.addEventListener("pagehide", () => {
    cancelAnimationFrame(frame);
    timeline?.pause();
    panelMotion?.pause();
  });
  window.addEventListener("pageshow", sync);
  window.addEventListener("resize", () => {
    if (!timeline || finished || reduced.matches) return;
    buildTimeline(Number(timeline.currentTime) || 0);
    sync();
  });
  window.addEventListener("beforeprint", finish);
  reduced.addEventListener("change", sync);
})();

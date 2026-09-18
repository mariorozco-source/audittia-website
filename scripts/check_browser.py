#!/usr/bin/env python3
"""Pruebas opcionales de navegador. Requiere Playwright; no modifica el sitio."""

import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--browser-path", help="Chrome local; omitir para Chromium de Playwright.")
    parser.add_argument("--axe-script", type=Path, help="axe.min.js local y revisado; no se descarga ni se publica.")
    args = parser.parse_args()
    base = args.base_url.rstrip("/") + "/"
    pages = ["index.html", "plataforma.html", "para-entidades.html", "seguridad.html",
             "nosotros.html", "recursos.html", "privacidad.html", "404.html"]
    failures, results, console_errors = [], [], []
    with sync_playwright() as playwright:
        options = {"headless": True}
        if args.browser_path:
            options["executable_path"] = args.browser_path
        browser = playwright.chromium.launch(**options)
        context = browser.new_context(reduced_motion="reduce")
        page = context.new_page()
        page.on("pageerror", lambda error: console_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        for width in (360, 390, 820, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 1000})
            for name in pages:
                response = page.goto(base + name, wait_until="networkidle")
                if not response or response.status != 200:
                    failures.append(f"{name}@{width}: respuesta HTTP inesperada")
                page.evaluate("document.fonts.ready")
                # Activar también imágenes lazy y componentes posteriores al primer viewport.
                page.locator("img").evaluate_all("(imgs) => imgs.forEach(img => img.loading = 'eager')")
                page.evaluate("Promise.all([...document.images].map(img => img.decode().catch(() => {})))")
                metrics = page.evaluate("""() => ({
                    overflow: document.documentElement.scrollWidth > window.innerWidth,
                    brokenImages: [...document.images].filter(img => !img.naturalWidth).length,
                    height: document.documentElement.scrollHeight,
                    animations: document.getAnimations().length
                })""")
                if metrics["overflow"] or metrics["brokenImages"] or metrics["animations"]:
                    failures.append(f"{name}@{width}: {metrics}")
                results.append({"page": name, "width": width, **metrics})
            print(f"Renderizados comprobados a {width}px", flush=True)

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(base)
        summary = page.locator(".menu-movil summary")
        summary.click()
        page.keyboard.press("Escape")
        assert not page.locator(".menu-movil").evaluate("el => el.open")
        assert summary.evaluate("el => el === document.activeElement")
        summary.click()
        # El desplegable cubre el H1: el clic exterior debe ocurrir
        # realmente fuera de su rectángulo, no a través de él.
        page.mouse.click(5, 650)
        assert not page.locator(".menu-movil").evaluate("el => el.open")
        page.locator(".preguntas summary").first.click()
        assert page.locator(".preguntas details").first.evaluate("el => el.open")

        nojs = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
        fallback = nojs.new_page()
        fallback.goto(base)
        fallback.locator(".menu-movil summary").click()
        assert fallback.locator(".menu-movil nav").is_visible()
        fallback.locator(".menu-movil summary").click()
        fallback.locator(".preguntas summary").first.click()
        assert fallback.locator(".pregunta__respuesta").first.is_visible()
        nojs.close()

        # Comprobar el modo con movimiento, además del modo reducido anterior.
        animated = browser.new_context(reduced_motion="no-preference", viewport={"width": 390, "height": 844})
        animated.add_init_script("""(() => {
            const original = Element.prototype.animate;
            window.__motionCalls = [];
            Element.prototype.animate = function(frames, options) {
                window.__motionCalls.push({duration: options.duration, delay: options.delay || 0});
                return original.call(this, frames, options);
            };
        })();""")
        moving = animated.new_page()
        moving.goto(base)
        initial = moving.evaluate("window.__motionCalls.length")
        assert initial > 0, "No se activó la entrada del hero."
        moving.locator(".tarjetas-entidad").scroll_into_view_if_needed()
        moving.wait_for_timeout(750)
        assert moving.evaluate("window.__motionCalls.length") > initial, "No se activaron las entradas al desplazarse."
        assert moving.evaluate("document.getAnimations().length") == 0, "Una animación continúa indefinidamente."
        moving.locator(".preguntas summary").first.click()
        moving.emulate_media(reduced_motion="reduce")
        moving.wait_for_timeout(100)
        assert moving.evaluate("document.getAnimations().length") == 0, "No se canceló el movimiento."
        count = moving.evaluate("window.__motionCalls.length")
        moving.locator(".preguntas summary").nth(1).click()
        moving.wait_for_timeout(100)
        assert moving.evaluate("window.__motionCalls.length") == count, "Se animó contenido con movimiento reducido."
        assert moving.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        animated.close()
        print("Movimiento normal, cancelación y preferencia reducida comprobados.", flush=True)

        if args.axe_script:
            axe_source = args.axe_script.read_text(encoding="utf-8")
            for width in (390, 1440):
                page.set_viewport_size({"width": width, "height": 1000})
                for name in pages:
                    page.goto(base + name)
                    page.evaluate("document.fonts.ready")
                    page.locator(".preguntas details").evaluate_all("(items) => items.forEach(el => el.open = true)")
                    page.evaluate(axe_source)
                    axe = page.evaluate("""async () => await axe.run(document, {
                        runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}
                    })""")
                    if axe["violations"]:
                        failures.append(f"{name}@{width}: axe " + json.dumps(axe["violations"], ensure_ascii=False))
                    print(json.dumps({"page": name, "width": width, "axeViolations": len(axe["violations"]),
                                      "needsManualReview": [item["id"] for item in axe["incomplete"]]}, ensure_ascii=False))
        browser.close()
    print(json.dumps({"renders": results, "consoleErrors": console_errors, "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures or console_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

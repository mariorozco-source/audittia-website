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
                // La demostración de Plataforma tiene su propia prueba de secuencia.
                if (!this.closest('.mockup-producto')) window.__motionCalls.push({element: this, frames, duration: options.duration, delay: options.delay || 0});
                return original.call(this, frames, options);
            };
        })();""")
        moving = animated.new_page()
        moving.on("pageerror", lambda error: console_errors.append(str(error)))
        for width in (390, 1440):
            moving.set_viewport_size({"width": width, "height": 844})
            for name in pages:
                moving.goto(base + name, wait_until="networkidle")
                assert moving.evaluate("window.__motionCalls.length") == 0, f"Entrada animada al cargar {name}@{width}"
                height = moving.evaluate("document.documentElement.scrollHeight")
                for offset in range(420, height, 420):
                    moving.evaluate("y => window.scrollTo(0, y)", offset)
                    moving.wait_for_timeout(40)
                moving.wait_for_timeout(1100)
                count = moving.evaluate("window.__motionCalls.length")
                if name not in ("privacidad.html", "404.html"):
                    assert count > 0, f"Sin entradas de scroll en {name}@{width}"
                assert moving.evaluate("""(() => {
                    const calls = window.__motionCalls;
                    return new Set(calls.map(call => call.element)).size === calls.length
                        && calls.every(call => call.duration <= 560 && call.delay <= 480)
                        && calls.every(call => !call.element.closest('.hero, .hero-pagina, .hero--interior'))
                        && !calls.some(a => calls.some(b => a !== b && a.element.contains(b.element)));
                })()"""), f"Movimiento repetitivo, anidado o excesivo en {name}@{width}"
                assert moving.evaluate("document.getAnimations().filter(a => !a.effect?.target?.closest('.mockup-producto')).length") == 0, "Una animación continúa indefinidamente."
                # Subir y volver a bajar no debe reproducir ninguna entrada.
                for offset in (0, height, 0):
                    moving.evaluate("y => window.scrollTo(0, y)", offset)
                    moving.wait_for_timeout(80)
                assert moving.evaluate("window.__motionCalls.length") == count, f"Entrada repetida en {name}@{width}"
            print(f"Navegación estable y scroll sin repeticiones: ocho páginas a {width}px.", flush=True)

        # Verificar la secuencia que ve el usuario, no sólo su configuración.
        for width in (390, 1440):
            moving.set_viewport_size({"width": width, "height": 844})
            moving.goto(base, wait_until="networkidle")
            moving.locator(".flujo-resumen").evaluate("el => window.scrollTo(0, window.scrollY + el.getBoundingClientRect().top - 110)")
            moving.wait_for_timeout(80)
            assert moving.evaluate("window.__motionCalls.filter(call => call.element.matches('.flujo-resumen li')).length") == 3
            moving.evaluate("""() => {
                window.__stepAnimations = [...document.querySelectorAll('.flujo-resumen li')].map(el => el.getAnimations()[0]);
                window.__stepAnimations.forEach(animation => animation.pause());
            }""")
            for elapsed, visible in ((100, [True, False, False]), (300, [True, True, False]), (700, [True, True, True])):
                moving.evaluate("time => window.__stepAnimations.forEach(animation => animation.currentTime = time)", elapsed)
                actual = moving.locator(".flujo-resumen li").evaluate_all("items => items.map(el => Number(getComputedStyle(el).opacity) > 0.01)")
                assert actual == visible, f"Orden incorrecto de pasos a {elapsed}ms@{width}: {actual}"
            moving.evaluate("window.__stepAnimations.forEach(animation => animation.finish())")
            assert moving.locator(".flujo-resumen li").evaluate_all("items => items.every(el => getComputedStyle(el).opacity === '1')")
            # El foco debe sacar de espera un enlace todavía fuera de pantalla.
            moving.locator(".tarjetas-entidad a").first.evaluate("el => el.focus({preventScroll: true})")
            assert moving.locator(".tarjetas-entidad article").first.evaluate("el => getComputedStyle(el).opacity === '1'")
            moving.emulate_media(reduced_motion="reduce")
            moving.wait_for_timeout(100)
            assert moving.locator(".motion-pending").count() == 0, "Quedó contenido oculto con movimiento reducido."
            moving.emulate_media(reduced_motion="no-preference")
        print("Secuencia visual 1 → 2 → 3, foco y visibilidad comprobados en móvil y escritorio.", flush=True)

        moving.set_viewport_size({"width": 1440, "height": 844})
        moving.goto(base, wait_until="networkidle")
        for route in ("plataforma.html", "seguridad.html"):
            moving.locator(f'.navegacion a[href="{route}"]').click()
            moving.wait_for_load_state("networkidle")
            assert moving.evaluate("window.__motionCalls.length") == 0, f"Entrada animada desde el menú: {route}"
        moving.goto(base + "plataforma.html#verificaciones", wait_until="networkidle")
        assert moving.evaluate("window.__motionCalls.length") == 0, "Se animó la llegada por enlace profundo."
        moving.locator('a[href="#contenido-principal"]').last.click()
        moving.wait_for_timeout(100)
        assert moving.evaluate("document.getAnimations().filter(a => !a.effect?.target?.closest('.mockup-producto')).length") == 0, "El salto a una sección dejó animaciones activas."

        moving.set_viewport_size({"width": 390, "height": 844})
        moving.goto(base, wait_until="networkidle")
        moving.locator(".preguntas summary").first.scroll_into_view_if_needed()
        moving.wait_for_timeout(1100)
        moving.locator(".preguntas summary").first.click()
        moving.wait_for_timeout(30)
        assert moving.evaluate("document.getAnimations().filter(a => !a.effect?.target?.closest('.mockup-producto')).length") > 0, "No se activó el fundido de respuesta."
        moving.emulate_media(reduced_motion="reduce")
        moving.wait_for_timeout(100)
        assert moving.evaluate("document.getAnimations().filter(a => !a.effect?.target?.closest('.mockup-producto')).length") == 0, "No se canceló el movimiento."
        count = moving.evaluate("window.__motionCalls.length")
        moving.locator(".preguntas summary").nth(1).click()
        moving.wait_for_timeout(100)
        assert moving.evaluate("window.__motionCalls.length") == count, "Se animó contenido con movimiento reducido."
        assert moving.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        animated.close()
        print("Navegación superior, fragmentos, cancelación y preferencia reducida comprobados.", flush=True)

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

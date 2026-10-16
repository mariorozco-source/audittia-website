#!/usr/bin/env python3
"""Pruebas de la demostración animada; requiere Playwright y servidor local."""
import argparse
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8766')
    parser.add_argument('--browser-path')
    args = parser.parse_args()
    url = args.base_url.rstrip('/') + '/plataforma.html'
    with sync_playwright() as p:
        options = {'headless': True}
        if args.browser_path:
            options['executable_path'] = args.browser_path
        browser = p.chromium.launch(**options)
        page = browser.new_page(reduced_motion='no-preference')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.add_init_script("""document.addEventListener('DOMContentLoaded', () => {
            window.selections = [];
            const title = document.querySelector('.mockup-producto__estado > span');
            new MutationObserver(() => window.selections.push(title.textContent)).observe(title, {childList: true});
        });""")
        expected = ['Factura', 'Historia clínica', 'Órdenes', 'Autorizaciones', 'Registros']
        for width in (360, 390, 820, 1440):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(url, wait_until='networkidle')
            page.locator('.mockup-producto').scroll_into_view_if_needed()
            page.wait_for_timeout(2100)
            if width in (390, 1440):
                page.screenshot(path=f'/tmp/audittia-demo-{width}.png')
            page.wait_for_timeout(3200)
            # El cierre fija el último estado sin cambiar el orden.
            states = page.evaluate('window.selections')
            distinct = [state for i, state in enumerate(states) if i == 0 or state != states[i-1]]
            assert distinct == expected, (width, states)
            assert page.locator('.mockup-producto__cursor').evaluate("el => getComputedStyle(el).opacity === '0' && el.getAnimations().length === 0")
            assert page.locator('.mockup-producto__estado strong').inner_text() == 'Pendiente de auditor'
            assert page.locator('.mockup-producto aside').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            count = len(states)
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(100)
            page.locator('.mockup-producto').scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            assert page.evaluate('window.selections.length') == count, 'Se repitió la demostración.'
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(600)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(150)
        state = page.locator('.mockup-producto__estado > span').inner_text()
        page.wait_for_timeout(1000)
        assert page.locator('.mockup-producto__estado > span').inner_text() == state, 'Animación fuera de pantalla.'
        page.locator('.mockup-producto').scroll_into_view_if_needed()
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_timeout(100)
        assert page.locator('.mockup-producto__estado > span').inner_text() == 'Verificación documental'
        assert page.locator('.mockup-producto__cursor').evaluate("el => getComputedStyle(el).opacity === '0'")
        assert page.evaluate('document.getAnimations().length') == 0
        page.reload(wait_until='networkidle')
        page.wait_for_timeout(1000)
        assert page.evaluate('window.selections.length') == 0
        nojs = browser.new_page(java_script_enabled=False, viewport={'width': 360, 'height': 1000})
        nojs.goto(url)
        assert nojs.locator('.mockup-producto aside').is_visible()
        assert nojs.locator('.mockup-producto__estado > span').inner_text() == 'Verificación documental'
        assert not errors, errors
        browser.close()
    print('Demostración correcta: cinco selecciones en orden, cuatro anchuras, sin repeticiones, pausa fuera de pantalla, movimiento reducido y sin JavaScript.')


if __name__ == '__main__':
    main()

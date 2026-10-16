#!/usr/bin/env python3
"""Comprueba el video de portada con Playwright y un servidor local."""
import argparse
from playwright.sync_api import sync_playwright


def wait_for(page, expression):
    # evaluate evita unsafe-eval y conserva la CSP del sitio.
    for _ in range(100):
        if page.evaluate(expression):
            return
        page.wait_for_timeout(50)
    raise AssertionError(expression)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8766')
    parser.add_argument('--browser-path')
    args = parser.parse_args()
    with sync_playwright() as p:
        options = {'headless': True}
        if args.browser_path:
            options['executable_path'] = args.browser_path
        browser = p.chromium.launch(**options)
        errors = []
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(args.base_url)
        wait_for(page, "!document.querySelector('video').paused && document.querySelector('video').currentTime > 0")
        assert page.locator('video').evaluate('v => v.muted && v.playsInline && !v.loop && v.videoWidth === 1280')
        page.locator('.hero__video-control').click()
        assert page.locator('video').evaluate('v => v.paused')
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(100)
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(100)
        assert page.locator('video').evaluate('v => v.paused'), 'Se ignoró la pausa manual.'
        page.locator('.hero__video-control').click()
        wait_for(page, "!document.querySelector('video').paused")
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        wait_for(page, "document.querySelector('video').paused")
        page.evaluate('window.scrollTo(0, 0)')
        wait_for(page, "!document.querySelector('video').paused")
        page.emulate_media(reduced_motion='reduce')
        wait_for(page, "document.querySelector('video').paused")
        page.reload(wait_until='networkidle')
        assert page.locator('video').evaluate('v => v.paused && v.currentTime === 0')
        page.locator('.hero__video-control').click()
        wait_for(page, "!document.querySelector('video').paused")
        wait_for(page, "document.querySelector('video').readyState >= 2 && Number.isFinite(document.querySelector('video').duration)")
        page.locator('video').evaluate('v => v.currentTime = v.duration - 0.15')
        wait_for(page, "document.querySelector('video').ended")
        assert page.locator('.hero__video-control').inner_text() == 'Volver a reproducir'
        page.locator('.hero__video-control').click()
        wait_for(page, "!document.querySelector('video').paused && document.querySelector('video').currentTime < 2")

        page.emulate_media(reduced_motion='no-preference')
        for width in (360, 390, 820, 1440):
            page.set_viewport_size({'width': width, 'height': 844})
            page.goto(args.base_url)
            page.locator('video').scroll_into_view_if_needed()
            wait_for(page, "!document.querySelector('video').paused")
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='/tmp/audittia-video-desktop.png')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(args.base_url)
        page.locator('video').scroll_into_view_if_needed()
        wait_for(page, "document.querySelector('video').readyState >= 2")
        page.locator('video').evaluate('v => { v.pause(); v.currentTime = 8.5; }')
        page.wait_for_timeout(200)
        page.screenshot(path='/tmp/audittia-video-mobile.png')

        fallback = browser.new_page(java_script_enabled=False)
        fallback.goto(args.base_url)
        assert fallback.locator('video').evaluate('v => v.controls && v.paused')
        assert not fallback.locator('.hero__video-control').is_visible()
        fallback.close()
        page.route('**/medica-auditoria-portada.mp4', lambda route: route.abort())
        page.goto(args.base_url)
        page.locator('.hero__foto-marco').scroll_into_view_if_needed()
        wait_for(page, "!document.querySelector('.hero__video-fallback').hidden")
        assert not page.locator('.hero__video-control').is_visible()
        assert page.locator('.hero__video-fallback').evaluate('img => img.naturalWidth > 0')
        assert not errors, errors
        browser.close()
    print('Video correcto: autoplay, pausa manual, scroll, movimiento reducido, final/repetición, cuatro anchuras, sin JS y respaldo ante errores.')


if __name__ == '__main__':
    main()

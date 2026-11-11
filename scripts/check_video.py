#!/usr/bin/env python3
"""Comprueba un video ambiental con Playwright y un servidor local."""
import argparse
import json
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
    parser.add_argument('--video-selector', choices=['#video-portada', '#video-equipo'], default='#video-portada')
    args = parser.parse_args()
    container = '.hero__foto-marco' if args.video_selector == '#video-portada' else '.foto-editorial__media'
    fallback_selector = container + ' [data-video-fallback]'
    with sync_playwright() as p:
        options = {'headless': True}
        if args.browser_path:
            options['executable_path'] = args.browser_path
        browser = p.chromium.launch(**options)
        errors = []
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page.add_init_script("Object.defineProperty(window, '__testVideo', {get: () => document.querySelector(" + json.dumps(args.video_selector) + ")});")
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(args.base_url)
        if args.video_selector == '#video-equipo':
            assert page.locator(args.video_selector).evaluate('v => v.paused && v.currentTime === 0')
        page.locator(container).scroll_into_view_if_needed()
        wait_for(page, "!window.__testVideo.paused && window.__testVideo.currentTime > 0")
        assert page.locator(args.video_selector).evaluate('v => v.muted && v.playsInline && v.loop && v.videoWidth === 1280')
        assert page.locator('.hero__video-control').count() == 0
        assert page.locator(args.video_selector).evaluate('v => !v.controls')
        page.locator(args.video_selector).evaluate('v => v.currentTime = v.duration - 0.3')
        wait_for(page, "!window.__testVideo.paused && window.__testVideo.currentTime < 2")
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        wait_for(page, "window.__testVideo.paused")
        page.locator(container).scroll_into_view_if_needed()
        wait_for(page, "!window.__testVideo.paused")
        page.emulate_media(reduced_motion='reduce')
        wait_for(page, "window.__testVideo.paused && window.__testVideo.hidden")
        assert page.locator(fallback_selector).is_visible()
        page.wait_for_timeout(600)
        assert page.locator(args.video_selector).evaluate('v => v.paused'), 'Reproducción activa con movimiento reducido.'
        page.reload(wait_until='networkidle')
        assert page.locator(args.video_selector).evaluate('v => v.paused && v.currentTime === 0')
        page.locator(container).scroll_into_view_if_needed()
        assert page.locator(fallback_selector).is_visible()
        page.emulate_media(reduced_motion='no-preference')

        for width in (360, 390, 820, 1440):
            page.set_viewport_size({'width': width, 'height': 844})
            page.goto(args.base_url)
            page.locator(args.video_selector).scroll_into_view_if_needed()
            wait_for(page, "!window.__testVideo.paused && window.__testVideo.currentTime > 0")
            assert page.locator(args.video_selector).evaluate('v => v.videoWidth') == (640 if width <= 760 else 1280)
            assert ('-mobile.mp4' in page.locator(args.video_selector).evaluate('v => v.currentSrc')) == (width <= 760)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            if args.video_selector == '#video-equipo':
                assert page.locator(args.video_selector).evaluate('v => Math.abs(v.clientWidth / v.clientHeight - 16 / 9) < 0.02'), 'El video del equipo está recortado.'
                wait_for(page, "document.querySelector('#video-portada').paused")
        page.wait_for_timeout(600)
        page.screenshot(path='/tmp/audittia-' + args.video_selector[1:] + '-desktop.png')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(args.base_url)
        page.locator(args.video_selector).scroll_into_view_if_needed()
        wait_for(page, "window.__testVideo.readyState >= 2")
        page.locator(args.video_selector).evaluate('v => { v.pause(); v.currentTime = 8.5; }')
        page.wait_for_timeout(600)
        page.screenshot(path='/tmp/audittia-' + args.video_selector[1:] + '-mobile.png')

        fallback = browser.new_page(java_script_enabled=False)
        fallback.goto(args.base_url)
        assert fallback.locator(args.video_selector).evaluate('v => !v.controls && v.paused')
        assert not fallback.locator('.hero__video-control').is_visible()
        fallback.close()
        page.route('**/*.mp4', lambda route: route.abort())
        page.goto(args.base_url)
        page.locator(container).scroll_into_view_if_needed()
        wait_for(page, "!window.__testVideo.parentElement.querySelector('[data-video-fallback]').hidden")
        assert not page.locator('.hero__video-control').is_visible()
        assert page.locator(fallback_selector).evaluate('img => img.naturalWidth > 0')
        assert not errors, errors
        browser.close()
    print('Video correcto: repetición continua, fuentes móviles, pausa fuera de pantalla y con movimiento reducido, sin botones, cuatro anchuras, sin JS y respaldo ante errores.')


if __name__ == '__main__':
    main()

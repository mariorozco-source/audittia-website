#!/usr/bin/env python3
"""Valida el sitio estático con la biblioteca estándar y sin hacer solicitudes de red."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(
    r"\[(?i:CORREO(?:_[A-Z]+)*|NOMBRE(?:_[A-Z]+)*|M[ÉE]TRICA[^\]]*)\]|\bTODO\b"
)
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


@dataclass
class Reference:
    url: str
    line: int
    resource: bool


@dataclass
class Page:
    path: Path
    lang: str = ""
    h1_count: int = 0
    title_count: int = 0
    title: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    viewports: list[str] = field(default_factory=list)
    canonicals: list[str] = field(default_factory=list)
    policies: list[str] = field(default_factory=list)
    referrers: list[str] = field(default_factory=list)
    social_images: list[str] = field(default_factory=list)
    ids: dict[str, int] = field(default_factory=dict)
    references: list[Reference] = field(default_factory=list)
    problems: list[tuple[int, str]] = field(default_factory=list)


class PageParser(HTMLParser):
    def __init__(self, page: Page) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self.in_title = False
        self.in_head = False

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attributes_map = dict(attributes)
        line = self.getpos()[0]
        if tag == "head":
            self.in_head = True
        elif tag == "html":
            self.page.lang = attributes_map.get("lang", "") or ""
        elif tag == "h1":
            self.page.h1_count += 1
        elif tag == "title" and self.in_head:
            self.page.title_count += 1
            self.in_title = True
        elif tag == "meta":
            name = (attributes_map.get("name") or "").lower()
            content = attributes_map.get("content") or ""
            if name == "description":
                self.page.descriptions.append(content)
            elif name == "viewport":
                self.page.viewports.append(content)
            elif name == "referrer":
                self.page.referrers.append(content)
            if (attributes_map.get("http-equiv") or "").lower() == "content-security-policy":
                self.page.policies.append(content)
            if attributes_map.get("property") == "og:image":
                self.page.social_images.append(content)
        elif tag == "link" and attributes_map.get("rel") == "canonical":
            self.page.canonicals.append(attributes_map.get("href") or "")

        identifier = attributes_map.get("id")
        if identifier is not None:
            if not identifier.strip():
                self.page.problems.append((line, "El atributo id está vacío."))
            elif identifier in self.page.ids:
                self.page.problems.append(
                    (line, f"ID duplicado '{identifier}' (primera aparición: línea {self.page.ids[identifier]}).")
                )
            else:
                self.page.ids[identifier] = line

        for attribute in ("href", "src", "poster"):
            if attribute in attributes_map:
                self.page.references.append(
                    Reference(
                        attributes_map[attribute] or "",
                        line,
                        attribute != "href" or tag in {"link", "image", "use"},
                    )
                )
        # Las imágenes responsive habituales usan rutas sin comas. Un data URI
        # completo se omite aquí y nunca se interpreta como ruta del repositorio.
        srcset = attributes_map.get("srcset") or ""
        if srcset and not srcset.lstrip().startswith("data:"):
            for candidate in srcset.split(","):
                parts = candidate.strip().split()
                if parts:
                    self.page.references.append(Reference(parts[0], line, True))

    def handle_startendtag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attributes)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.page.title.append(data)


def inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_reference(
    reference: Reference, source: Path, root: Path, pages: dict[Path, Page]
) -> str | None:
    url = reference.url.strip()
    if not url:
        return "Hay un enlace o recurso con una URL vacía."
    try:
        parsed = urlsplit(url)
    except ValueError:
        return f"URL inválida: {url}"

    if parsed.scheme == "javascript":
        return f"No se permiten enlaces javascript: {url}"
    if reference.resource and parsed.scheme == "http":
        return f"Contenido mixto: el recurso usa HTTP: {url}"
    # mailto y tel son destinos externos, incluso si contienen ? o # codificados.
    # Esta comprobación no verifica que el buzón exista o pueda recibir correo.
    if parsed.scheme or parsed.netloc:
        return None

    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        target = (root / decoded_path.lstrip("/")).resolve()
    elif decoded_path:
        target = (source.parent / decoded_path).resolve()
    else:
        target = source

    if not inside(target, root):
        return f"La ruta sale del directorio publicado: {url}"
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return f"No existe el archivo local: {url}"
    if url.endswith("#") and not parsed.fragment:
        return f"Enlace con fragmento vacío: {url}"
    if parsed.fragment and target.suffix.lower() == ".html":
        fragment = unquote(parsed.fragment)
        # Un fragmento de texto del navegador puede acompañar un ID o aparecer solo.
        fragment = fragment.split(":~:text=", 1)[0]
        if fragment and target in pages and fragment not in pages[target].ids:
            return f"No existe el fragmento '{fragment}' en {target.relative_to(root)}."
    return None


def check(root: Path) -> int:
    if not root.is_dir():
        print(f"ERROR: no existe el directorio del sitio: {root}", file=sys.stderr)
        return 1

    paths = sorted(root.glob("*.html"))
    if not paths:
        print(f"ERROR: no hay páginas HTML en {root}", file=sys.stderr)
        return 1
    pages: dict[Path, Page] = {}
    errors: list[str] = []
    reference_count = 0

    for path in paths:
        page = Page(path.resolve())
        pages[page.path] = page
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{path.name}: no se pudo leer como UTF-8: {error}")
            continue
        parser = PageParser(page)
        parser.feed(source)
        parser.close()
        if not page.lang.strip():
            page.problems.append((1, "Falta el idioma del documento (html lang)."))
        if page.h1_count != 1:
            page.problems.append((1, f"Se requiere un H1; encontrados: {page.h1_count}."))
        if page.title_count != 1 or not "".join(page.title).strip():
            page.problems.append((1, "Se requiere un title único y no vacío."))
        if len(page.descriptions) != 1 or not page.descriptions[0].strip():
            page.problems.append((1, "Se requiere una meta description única y no vacía."))
        if len(page.viewports) != 1 or not page.viewports[0].strip():
            page.problems.append((1, "Se requiere una meta viewport única y no vacía."))
        if len(page.canonicals) != 1 or not page.canonicals[0].startswith("https://audittia.com/"):
            page.problems.append((1, "Se requiere canonical HTTPS único de audittia.com."))
        if len(page.policies) != 1 or "default-src 'self'" not in page.policies[0]:
            page.problems.append((1, "Falta la CSP local esperada."))
        if page.referrers != ["no-referrer"]:
            page.problems.append((1, "Falta la política no-referrer."))
        if len(page.social_images) != 1:
            page.problems.append((1, "Se requiere una imagen social."))
        for url in page.social_images:
            parsed = urlsplit(url)
            if parsed.scheme != "https" or parsed.netloc != "audittia.com":
                page.problems.append((1, "La imagen social debe servirse por HTTPS desde audittia.com."))
            else:
                target = (root / unquote(parsed.path).lstrip("/")).resolve()
                if not inside(target, root) or not target.is_file():
                    page.problems.append((1, "La imagen social local no existe."))
        for line, content in enumerate(source.splitlines(), 1):
            if PLACEHOLDER.search(content):
                page.problems.append((line, "Contenido pendiente de publicación: marcador o TODO."))

    for page in pages.values():
        for reference in page.references:
            reference_count += 1
            problem = validate_reference(reference, page.path, root, pages)
            if problem:
                page.problems.append((reference.line, problem))
        errors.extend(
            f"{page.path.relative_to(root)}:{line}: {message}"
            for line, message in page.problems
        )

    for path in sorted(root.glob("*.css")):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{path.name}: no se pudo leer como UTF-8: {error}")
            continue
        # Mantener los saltos de línea permite señalar ubicaciones útiles.
        source = re.sub(r"/\*.*?\*/", lambda match: "\n" * match.group().count("\n"), source, flags=re.DOTALL)
        for match in CSS_URL.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            reference_count += 1
            problem = validate_reference(Reference(match.group(2), line, True), path, root, pages)
            if problem:
                errors.append(f"{path.name}:{line}: {problem}")

    print(f"Sitio: {root}")
    print(f"Revisadas {len(paths)} páginas HTML y {reference_count} referencias; sin solicitudes de red.")
    if errors:
        for error in errors[:100]:
            print(f"ERROR {error}")
        if len(errors) > 100:
            print(f"... y {len(errors) - 100} errores adicionales.")
        print(f"RESULTADO: {len(errors)} errores. No está listo para publicación.")
        return 1
    print("RESULTADO: validación estática correcta.")
    print("Alcance: no sustituye la revisión visual, HTTPS ni la verificación de entrega del correo.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Directorio del sitio; por defecto, raíz del proyecto.")
    arguments = parser.parse_args()
    return check(arguments.root.resolve())


if __name__ == "__main__":
    sys.exit(main())

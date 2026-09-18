#!/usr/bin/env python3
"""Crea un directorio nuevo con los archivos públicos del sitio, sin desplegarlo."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ("CNAME", ".nojekyll", "robots.txt", "sitemap.xml")
PUBLIC_SUFFIXES = {".html", ".css", ".js"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / ".site",
        help="Directorio nuevo de salida. Por defecto: .site. Nunca se sobrescribe ni se borra una salida existente.",
    )
    arguments = parser.parse_args()
    requested_output = arguments.output.absolute()
    if requested_output.is_symlink() or requested_output.exists():
        parser.error(f"La salida ya existe: {requested_output}. Elige otro directorio; no se ha borrado nada.")
    output = requested_output.resolve()
    if not output.parent.is_dir():
        parser.error(f"El directorio padre debe existir: {output.parent}")
    try:
        relative_output = output.relative_to(PROJECT_ROOT)
    except ValueError:
        relative_output = None
    if relative_output is not None and len(relative_output.parts) != 1:
        parser.error("La salida dentro del proyecto debe ser una carpeta directa, nunca una subcarpeta de assets o de configuración.")

    sources = sorted(
        path for path in PROJECT_ROOT.iterdir()
        if path.suffix.lower() in PUBLIC_SUFFIXES or path.name in PUBLIC_FILES
    )
    assets = PROJECT_ROOT / "assets"
    if not (PROJECT_ROOT / "index.html").is_file() or not assets.is_dir():
        parser.error("Falta index.html o el directorio assets.")
    for source in sources:
        if source.is_symlink() or not source.is_file():
            parser.error(f"Archivo público inválido o enlace simbólico: {source}")
    if assets.is_symlink():
        parser.error("assets no puede ser un enlace simbólico.")
    for asset in assets.rglob("*"):
        if asset.is_symlink():
            parser.error(f"No se publican enlaces simbólicos dentro de assets: {asset}")
        if not asset.is_file() and not asset.is_dir():
            parser.error(f"Tipo de recurso no permitido: {asset}")

    # Prevalidación completa antes de crear la salida. No hay operaciones de borrado.
    try:
        output.mkdir(exist_ok=False)
        for source in sources:
            shutil.copy2(source, output / source.name)
        shutil.copytree(assets, output / "assets")
    except OSError as error:
        print(f"ERROR al preparar el artefacto: {error}", file=sys.stderr)
        print("No se ha borrado ningún archivo. Si quedó una salida parcial, elige una nueva al reintentar.", file=sys.stderr)
        return 1

    count = sum(path.is_file() for path in output.rglob("*"))
    print(f"Artefacto creado: {output}")
    print(f"{count} archivos públicos; excluye scripts, documentación, .git y configuración de desarrollo.")
    print("No se ha desplegado el sitio ni se ha cambiado la configuración de GitHub Pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

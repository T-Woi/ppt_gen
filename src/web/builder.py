"""Utilitário de montagem da interface web a partir de base.html, páginas e componentes."""

from pathlib import Path


def assemble_web_index(web_dir: Path | None = None) -> Path:
    """Mescla base.html com componentes e páginas para gerar index.html pronto para execução."""
    if web_dir is None:
        web_dir = Path(__file__).resolve().parent

    base_file = web_dir / "base.html"
    if not base_file.exists():
        return web_dir / "index.html"

    content = base_file.read_text(encoding="utf-8")

    includes = [
        ("<!-- INCLUDE: components/header.html -->", "components/header.html"),
        ("<!-- INCLUDE: pages/upload.html -->", "pages/upload.html"),
        ("<!-- INCLUDE: pages/editor.html -->", "pages/editor.html"),
        ("<!-- INCLUDE: components/modals.html -->", "components/modals.html"),
    ]

    for marker, rel_path in includes:
        part_path = web_dir / rel_path
        if part_path.exists():
            part_content = part_path.read_text(encoding="utf-8")
            content = content.replace(marker, part_content)

    out_file = web_dir / "index.html"
    out_file.write_text(content, encoding="utf-8")
    return out_file


if __name__ == "__main__":
    assembled = assemble_web_index()
    print(f"[PPT-Gen Web] index.html montado com sucesso em: {assembled}")

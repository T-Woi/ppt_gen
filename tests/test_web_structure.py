"""Testes da estrutura modular da interface web e do gerador assemble_web_index."""

from pathlib import Path

from web.builder import assemble_web_index


def test_web_assets_and_logo_exist():
    """Valida a presença do logo oficial e dos diretórios segmentados."""
    web_dir = Path(__file__).resolve().parent.parent / "src" / "web"
    webp_logo = web_dir / "assets" / "logo.webp"

    assert webp_logo.exists(), "assets/logo.webp não foi encontrado."
    assert webp_logo.stat().st_size > 1000, "assets/logo.webp está vazio ou corrompido."


def test_modular_css_files_exist():
    """Valida a separação e existência de todos os módulos CSS."""
    web_dir = Path(__file__).resolve().parent.parent / "src" / "web"
    css_dir = web_dir / "css"

    required_css = ["base.css", "components.css", "pages.css", "modals.css"]
    for css_file in required_css:
        path = css_dir / css_file
        assert path.exists(), f"Módulo CSS ausente: {css_file}"
        assert path.stat().st_size > 0, f"Módulo CSS vazio: {css_file}"

    styles_master = web_dir / "styles.css"
    assert styles_master.exists(), "styles.css não encontrado."


def test_modular_js_files_exist():
    """Valida a separação e existência de todos os módulos JavaScript."""
    web_dir = Path(__file__).resolve().parent.parent / "src" / "web"
    js_dir = web_dir / "js"

    required_js = [
        "config.js",
        "state.js",
        "components/modals.js",
        "components/slide-card.js",
        "components/lightbox.js",
        "pages/upload.js",
        "pages/editor.js",
        "app.js",
    ]
    for rel_js in required_js:
        path = js_dir / rel_js
        assert path.exists(), f"Módulo JS ausente: {rel_js}"
        assert path.stat().st_size > 0, f"Módulo JS vazio: {rel_js}"

    app_root = web_dir / "app.js"
    assert app_root.exists(), "app.js legado na raiz de web/ não encontrado."


def test_modular_html_and_builder():
    """Valida o base.html, componentes, páginas e a montagem do index.html."""
    web_dir = Path(__file__).resolve().parent.parent / "src" / "web"

    assert (web_dir / "base.html").exists(), "base.html não encontrado."
    assert (web_dir / "components" / "header.html").exists(), (
        "components/header.html não encontrado."
    )
    assert (web_dir / "components" / "modals.html").exists(), (
        "components/modals.html não encontrado."
    )
    assert (web_dir / "pages" / "upload.html").exists(), "pages/upload.html não encontrado."
    assert (web_dir / "pages" / "editor.html").exists(), "pages/editor.html não encontrado."

    assembled_index = assemble_web_index(web_dir)
    assert assembled_index.exists(), "Falha ao gerar index.html."

    content = assembled_index.read_text(encoding="utf-8")
    assert "assets/logo.webp" in content, "Logo webp não referenciado no index.html montado."
    assert "uploadView" in content, "uploadView não incorporado no index.html."
    assert "editorView" in content, "editorView não incorporado no index.html."
    assert "loadingModal" in content, "loadingModal não incorporado no index.html."
    assert "js/app.js" in content, "js/app.js não referenciado no index.html."


def test_assemble_web_index_edge_cases(tmp_path: Path) -> None:
    """Testa caminhos alternativos de assemble_web_index (None, base inexistente)."""
    # 1. Sem argumento (usa Path(__file__).resolve().parent)
    idx = assemble_web_index()
    assert idx.exists()

    # 2. Diretório sem base.html
    empty_dir = tmp_path / "empty_web"
    empty_dir.mkdir()
    fallback_res = assemble_web_index(empty_dir)
    assert fallback_res == empty_dir / "index.html"


def test_builder_run_as_script() -> None:
    """Executa o módulo builder como script para cobrir o bloco if __name__ == '__main__'."""
    import runpy
    import sys

    sys.modules.pop("web.builder", None)
    res = runpy.run_module("web.builder", run_name="__main__")
    assert "assembled" in res

"""Ponto de entrada principal da aplicação PPT-Gen Studio."""

import argparse
from pathlib import Path

import webview

from config import resolve_web_dir, settings
from server.deps import get_session_manager
from server.webview_api import PyWebViewApi


def parse_arguments() -> argparse.Namespace:
    """Configura e processa argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="PPT-Gen Studio: Conversor de Imagens e PDF para PowerPoint (PPTX)"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Caminho inicial de uma pasta de imagens ou arquivo PDF para carregar na abertura",
    )
    return parser.parse_args()


def launch_webview(initial_input: str | None = None) -> None:
    """Inicia a interface nativa via PyWebView (Edge WebView2) sem abrir nenhum servidor ou porta TCP."""
    web_dir = resolve_web_dir()

    # Assegura a montagem automática do index.html a partir dos módulos
    try:
        from web.builder import assemble_web_index

        assemble_web_index(web_dir)
    except Exception as e:
        print(f"[PPT-Gen] Aviso ao montar interface web: {e}")

    index_html = web_dir / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"Interface web não encontrada em: {index_html}")

    manager = get_session_manager()

    if initial_input:
        in_path = Path(initial_input)
        if in_path.exists():
            try:
                loaded = manager.load_path(in_path)
                print(f"[PPT-Gen] Carregados com sucesso {loaded} slides a partir de: {in_path}")
            except Exception as e:
                print(f"[PPT-Gen] Aviso ao carregar entrada inicial: {e}")

    api = PyWebViewApi(session_manager=manager)

    window = webview.create_window(
        title="PPT-Gen Studio",
        url=index_html.as_uri(),
        js_api=api,
        width=1280,
        height=820,
        min_size=(960, 640),
        text_select=True,
    )
    api.window = window

    # Ícone oficial da aplicação
    logo_file = web_dir / "assets" / "logo.ico"
    icon_arg = str(logo_file) if logo_file.exists() else None

    # Inicia o loop de janela nativa (bloqueante até fechar)
    webview.start(debug=settings.debug, icon=icon_arg)


def cli_main() -> None:
    """Executa a aplicação a partir do terminal ou atalho executável."""
    args = parse_arguments()
    launch_webview(args.input)


if __name__ == "__main__":
    cli_main()

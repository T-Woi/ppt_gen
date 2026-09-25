"""Testes unitários para o gerenciador de sessão orientado a objetos (SessionManager)."""

from pathlib import Path

import pytest

from core.session import SessionManager, get_user_documents_dir


def test_session_manager_initial_state(session_manager: SessionManager) -> None:
    """Verifica os valores padrão de uma sessão recém-criada."""
    assert len(session_manager.items) == 0
    assert session_manager.source_description == "Nenhum arquivo carregado"
    assert session_manager.suggested_filename.endswith(".pptx")
    assert session_manager.job.job_id is not None


def test_session_manager_load_folder(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Testa o carregamento de uma pasta de imagens e a geração de itens de slide."""
    count = session_manager.load_folder(test_images_dir)
    assert count == 3
    items = session_manager.items
    assert len(items) == 3
    # Verifica a ordenação natural dos arquivos carregados
    assert items[0].title == "slide_1.png"
    assert items[1].title == "slide_2.png"
    assert items[2].title == "slide_10.png"
    assert session_manager.suggested_filename == f"{test_images_dir.name}.pptx"


def test_session_manager_reorder_and_rotation(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Valida as operações de reordenação e rotação de slides."""
    session_manager.load_folder(test_images_dir)
    items = session_manager.items
    id1, id2, id10 = items[0].id, items[1].id, items[2].id

    # Inverte os dois primeiros itens
    session_manager.reorder([id2, id1, id10])
    reordered = session_manager.items
    assert reordered[0].id == id2
    assert reordered[1].id == id1

    # Rotação horária (90) e anti-horária
    assert session_manager.rotate(id2, direction="cw") is True
    item2 = session_manager.get_item(id2)
    assert item2 is not None and item2.rotation == 90

    assert session_manager.rotate(id2, direction="ccw") is True
    assert item2 is not None and item2.rotation == 0

    # Rotação em item inexistente retorna False
    assert session_manager.rotate("id_fantasma", direction="cw") is False


def test_session_manager_sort_natural_and_reverse(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Valida ordenação natural e inversão da ordem dos slides."""
    session_manager.load_folder(test_images_dir)
    session_manager.reverse()
    assert session_manager.items[0].title == "slide_10.png"

    session_manager.sort_natural()
    assert session_manager.items[0].title == "slide_1.png"


def test_session_manager_manifest_and_serialization(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Valida a construção e serialização do manifesto DTO com msgspec."""
    session_manager.load_folder(test_images_dir)
    manifest = session_manager.build_manifest()
    assert manifest.total_slides == 3
    assert len(manifest.items) == 3
    assert manifest.items[0].thumbnail_url.startswith("/api/thumbnail/")

    json_bytes = session_manager.get_manifest_bytes()
    assert isinstance(json_bytes, bytes)
    assert b"slide_1.png" in json_bytes


def test_session_manager_remove_and_clear(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Testa remoção parcial e limpeza total da sessão."""
    session_manager.load_folder(test_images_dir)
    items = session_manager.items
    first_id = items[0].id

    removed = session_manager.remove([first_id])
    assert removed == 1
    assert len(session_manager.items) == 2

    session_manager.clear()
    assert len(session_manager.items) == 0
    assert session_manager.source_description == "Nenhum arquivo carregado"


def test_session_manager_load_pdf(session_manager: SessionManager, sample_pdf: Path) -> None:
    """Testa carregamento de PDF e tratamento de PDF inválido/vazio."""
    count = session_manager.load_pdf(sample_pdf)
    assert count == 2
    assert len(session_manager.items) == 2
    assert session_manager.items[0].source_type == "pdf_page"

    # Teste append=True
    count2 = session_manager.load_pdf(sample_pdf, append=True)
    assert count2 == 2
    assert len(session_manager.items) == 4

    # PDF inexistente
    with pytest.raises(ValueError):
        session_manager.load_pdf(Path("inexistente.pdf"))


def test_session_manager_load_image_paths(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Testa adição direta de caminhos de imagens."""
    imgs = list(test_images_dir.glob("*.png"))
    # Vazio retorna 0
    assert session_manager.load_image_paths([]) == 0

    count = session_manager.load_image_paths(imgs)
    assert count == 3
    assert len(session_manager.items) == 3

    # Append
    session_manager.load_image_paths([imgs[0]], append=True)
    assert len(session_manager.items) == 4


def test_session_manager_load_path_dispatcher(
    session_manager: SessionManager, test_images_dir: Path, sample_pdf: Path, tmp_path: Path
) -> None:
    """Testa o despachante universal load_path com diretório, PDF, imagem e erros."""
    # 1. Diretório
    assert session_manager.load_path(test_images_dir) == 3

    # 2. PDF
    assert session_manager.load_path(sample_pdf) == 2

    # 3. Imagem isolada (deve carregar a pasta pai)
    one_img = test_images_dir / "slide_1.png"
    assert session_manager.load_path(one_img) == 3

    # 4. Arquivo inexistente
    with pytest.raises(FileNotFoundError):
        session_manager.load_path(tmp_path / "inexistente.xyz")

    # 5. Formato não suportado
    txt_file = tmp_path / "teste.txt"
    txt_file.write_text("conteudo", encoding="utf-8")
    with pytest.raises(ValueError):
        session_manager.load_path(txt_file)


def test_get_user_documents_dir_fallbacks(monkeypatch, tmp_path: Path) -> None:
    """Testa as ramificações de resolução do diretório de documentos."""
    # Cenário 1: Documents existe
    fake_home = tmp_path / "fake_home"
    (fake_home / "Documents").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    assert get_user_documents_dir() == fake_home / "Documents"

    # Cenário 2: Documentos em português existe
    fake_home2 = tmp_path / "fake_home2"
    (fake_home2 / "Documentos").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home2)
    assert get_user_documents_dir() == fake_home2 / "Documentos"

    # Cenário 3: OneDrive Documents existe
    fake_home3 = tmp_path / "fake_home3"
    (fake_home3 / "OneDrive" / "Documents").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home3)
    assert get_user_documents_dir() == fake_home3 / "OneDrive" / "Documents"

    # Cenário 4: Nenhum existe, fallback para home
    fake_home4 = tmp_path / "fake_home4"
    fake_home4.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home4)
    assert get_user_documents_dir() == fake_home4

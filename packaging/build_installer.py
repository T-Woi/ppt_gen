"""PPT-Gen Studio - Construtor Unificado de Instalador para Windows (Inno Setup).

Localizado em: packaging/build_installer.py
Gera o executável autocontido e o instalador oficial do Windows em um único processo:
1. Montagem dos recursos da interface web
2. Congelamento do aplicativo via PyInstaller (dist/PPT-Gen-Studio)
3. Compilação do instalador nativo via Inno Setup (dist/PPT-Gen-Studio-Setup.exe)
4. Cálculo de hash SHA-256 para disponibilização em GitHub Releases
"""

import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Suporte a UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent


def get_version() -> str:
    """Obtém a versão definida no pyproject.toml."""
    try:
        pyproject = ROOT_DIR / "pyproject.toml"
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version"):
                return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.1.0"


# Template oficial do Inno Setup 6 (Padrão de mercado para Windows)
INNO_SETUP_TEMPLATE = """\
; Script gerado automaticamente pelo build_installer.py
#define MyAppName "PPT-Gen Studio"
#define MyAppVersion "{version}"
#define MyAppPublisher "PPT-Gen"
#define MyAppExeName "PPT-Gen Studio.exe"

[Setup]
AppId={{C6287B9F-841B-4E38-9844-325A8D19F0D2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\\Programs\\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
SourceDir={root_dir}
OutputDir={root_dir}\\dist
OutputBaseFilename=PPT-Gen-Studio-Setup
SetupIconFile=src\\web\\assets\\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenuicon"; Description: "Criar atalho na pasta do Menu Iniciar"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\\PPT-Gen-Studio\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\\_internal\\assets\\logo.ico"
Name: "{userprograms}\\{#MyAppName}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: startmenuicon; IconFilename: "{app}\\_internal\\assets\\logo.ico"
Name: "{userprograms}\\{#MyAppName}\\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
"""


def run_command(cmd: list[str], desc: str = "") -> None:
    """Executa um comando no shell com feedback visual e tratamento de erro."""
    if desc:
        print(f"-> {desc}...")
    start = time.time()
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    elapsed = time.time() - start
    if res.returncode != 0:
        print(f"\n[ERRO] Falha ao executar comando: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"[OK] Concluído em {elapsed:.1f}s")


def find_iscc() -> Path:
    """Localiza o executável do compilador Inno Setup (ISCC.exe)."""
    candidates = [
        shutil.which("iscc"),
        shutil.which("ISCC"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 7" / "ISCC.exe",
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
        Path(r"C:\ProgramData\chocolatey\bin\iscc.exe"),
        Path(os.environ.get("ChocolateyInstall", r"C:\ProgramData\chocolatey"))
        / "bin"
        / "iscc.exe",
    ]
    for cand in candidates:
        if cand and Path(cand).exists():
            return Path(cand)

    print("\n[AVISO] Compilador Inno Setup (ISCC.exe) não encontrado no sistema.")
    print("Para instalar oficialmente no Windows, execute no terminal:")
    print("  winget install --id JRSoftware.InnoSetup -e")
    sys.exit(1)


def generate_sha256(file_path: Path) -> Path:
    """Calcula e grava o hash SHA-256 do arquivo para distribuição no GitHub Releases."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    hash_file = file_path.with_name(f"{file_path.name}.sha256")
    hash_file.write_text(f"{digest} *{file_path.name}\n", encoding="utf-8")
    return hash_file


def main() -> None:
    """Executa o pipeline completo de montagem, compilação e criação do instalador."""
    print("\n" + "=" * 65)
    print("  PPT-Gen Studio - Build do Instalador Oficial para Windows")
    print("=" * 65)

    rebuild_app = "--no-rebuild" not in sys.argv

    # 1. Montagem da interface web
    print("\n[1/3] Montando recursos web...")
    sys.path.insert(0, str(ROOT_DIR / "src"))
    from web.builder import assemble_web_index

    assemble_web_index(ROOT_DIR / "src" / "web")

    # 2. Compilação com PyInstaller
    print("\n[2/3] Verificando binários com PyInstaller...")
    app_exe = ROOT_DIR / "dist" / "PPT-Gen-Studio" / "PPT-Gen Studio.exe"
    if not app_exe.exists() or rebuild_app:
        spec_file = SCRIPT_DIR / "ppt_gen.spec"
        run_command(
            [sys.executable, "-m", "PyInstaller", "--noconfirm", str(spec_file)],
            desc="Compilando aplicativo standalone",
        )

    # 3. Compilação do instalador via Inno Setup
    print("\n[3/3] Compilando instalador nativo com Inno Setup...")
    iscc_path = find_iscc()

    temp_iss = ROOT_DIR / ".setup_temp.iss"
    iss_content = INNO_SETUP_TEMPLATE.replace("{version}", get_version()).replace(
        "{root_dir}", str(ROOT_DIR)
    )
    temp_iss.write_text(iss_content, encoding="utf-8")

    try:
        run_command([str(iscc_path), str(temp_iss)], desc="Compilando instalador LZMA2")
    finally:
        if temp_iss.exists():
            temp_iss.unlink()

    setup_exe = ROOT_DIR / "dist" / "PPT-Gen-Studio-Setup.exe"
    if not setup_exe.exists():
        print(f"[ERRO] Executável do instalador não encontrado em: {setup_exe}", file=sys.stderr)
        sys.exit(1)

    # Gera SHA-256 para o GitHub Release
    sha_file = generate_sha256(setup_exe)
    size_mb = setup_exe.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 65)
    print("  INSTALADOR WINDOWS PRONTO PARA GITHUB RELEASE!")
    print("=" * 65)
    print(f"Executável: {setup_exe} ({size_mb:.2f} MB)")
    print(f"Checksum:   {sha_file}")
    print("\nPara publicar como Release no GitHub, você pode:")
    print("  1. Fazer push de uma tag de versão (ex: git tag v0.1.0 && git push origin v0.1.0)")
    print("  2. Ou publicar via GitHub CLI:")
    print(
        f'     gh release create v0.1.0 "{setup_exe}" "{sha_file}" --title "PPT-Gen Studio v0.1.0" --generate-notes'
    )


if __name__ == "__main__":
    main()

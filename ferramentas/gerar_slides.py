"""Renderiza slides.html de um post em PNGs 1080x1350 via Chrome headless.

Uso: python ferramentas/gerar_slides.py posts/2026-10/2026-10-01-quem-e-a-terra-forte
"""
import subprocess
import sys
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def main(pasta: Path) -> None:
    html = (pasta / "slides.html").resolve()
    total = html.read_text(encoding="utf-8").count('<section class="slide')
    for i in range(1, total + 1):
        saida = pasta / f"slide-{i:02d}.png"
        subprocess.run([
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--allow-file-access-from-files", "--window-size=1080,1350",
            "--virtual-time-budget=8000", f"--screenshot={saida.resolve()}",
            f"{html.as_uri()}?s={i}",
        ], check=True, capture_output=True)
        print(saida)


if __name__ == "__main__":
    main(Path(sys.argv[1]))

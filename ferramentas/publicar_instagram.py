"""Publica um post aprovado no Instagram (API oficial da Meta, Instagram Login).

Uso:
  python ferramentas/publicar_instagram.py --testar
  python ferramentas/publicar_instagram.py --renovar-token
  python ferramentas/publicar_instagram.py posts/2026-10/2026-10-06-tema.md            (só verifica)
  python ferramentas/publicar_instagram.py posts/2026-10/2026-10-06-tema.md --publicar
  python ferramentas/publicar_instagram.py posts/2026-10/2026-10-06-tema.md --agendar 2026-10-06T06:30

Imagens: slide-*.png na pasta com o mesmo nome do .md (1 imagem = feed, 2 a 10 = carrossel).
Credenciais: .env na raiz do projeto (INSTAGRAM_TOKEN). O token nunca é impresso.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ENV = RAIZ / ".env"
LOG = RAIZ / "ferramentas" / "publicacoes.log"
HOST = "https://graph.instagram.com"

LIMITE_LEGENDA = 2200
LIMITE_HASHTAGS = 5   # regra do Instagram desde dez/2025
LIMITE_EMOJIS = 3     # regra da marca
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")


def log(msg: str) -> None:
    linha = f"{datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(msg)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(linha + "\n")


def ler_env() -> dict:
    if not ENV.exists():
        sys.exit(f"ERRO: {ENV} não existe. Rode o passo de configuração da skill publicar-instagram-terraforte.")
    dados = {}
    for linha in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.strip().startswith("#"):
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip()
    if not dados.get("INSTAGRAM_TOKEN"):
        sys.exit("ERRO: INSTAGRAM_TOKEN vazio no .env.")
    return dados


ENV_DADOS: dict = {}


def api(metodo: str, caminho: str, **params) -> dict:
    """Chama a API sem nunca deixar o token aparecer em mensagens de erro."""
    token = ENV_DADOS["INSTAGRAM_TOKEN"]
    versao = ENV_DADOS.get("META_API_VERSION", "v26.0")
    url = f"{HOST}/{caminho}" if caminho.startswith("refresh") else f"{HOST}/{versao}/{caminho}"
    params["access_token"] = token
    try:
        if metodo == "GET":
            r = requests.get(url, params=params, timeout=60)
        else:
            r = requests.post(url, data=params, timeout=60)
        dados = r.json()
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(str(e).replace(token, "***")) from None
    if "error" in dados:
        raise RuntimeError(f"API: {dados['error'].get('message', dados['error'])}")
    return dados


def secao(texto: str, titulo: str) -> str:
    m = re.search(rf"^## {titulo}\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""


def montar_post(md: Path) -> tuple[str, list[Path], list[str]]:
    texto = md.read_text(encoding="utf-8")
    erros = []

    status = re.search(r"^Status:\s*(\w+)", texto, re.M)
    if not status or status.group(1) != "aprovado":
        erros.append(f"Status é '{status.group(1) if status else '?'}' — só publico post com 'Status: aprovado'.")

    legenda = secao(texto, "Legenda")
    hashtags = secao(texto, "Hashtags")
    if not legenda:
        erros.append("Seção '## Legenda' vazia ou ausente.")
    caption = f"{legenda}\n\n{hashtags}".strip()

    if len(caption) > LIMITE_LEGENDA:
        erros.append(f"Legenda com {len(caption)} caracteres (máx. {LIMITE_LEGENDA}).")
    n_tags = len(re.findall(r"#\w+", caption))
    if n_tags > LIMITE_HASHTAGS:
        erros.append(f"{n_tags} hashtags (máx. {LIMITE_HASHTAGS}).")
    n_emo = len(EMOJI.findall(caption))
    if n_emo > LIMITE_EMOJIS:
        erros.append(f"{n_emo} emojis (máx. {LIMITE_EMOJIS}).")

    pasta = md.with_suffix("")
    imagens = sorted(pasta.glob("slide-*.png")) if pasta.is_dir() else []
    if not 1 <= len(imagens) <= 10:
        erros.append(f"Encontrei {len(imagens)} imagens slide-*.png em {pasta} (precisa de 1 a 10).")
    for img in imagens:
        with Image.open(img) as im:
            if im.size != (1080, 1350):
                erros.append(f"{img.name} tem {im.size[0]}x{im.size[1]} (esperado 1080x1350).")
    return caption, imagens, erros


def hospedar(img: Path, tmp: Path) -> str:
    """Converte para JPEG (único formato aceito pela API) e hospeda por 1 hora no litterbox."""
    jpg = tmp / (img.stem + ".jpg")
    with Image.open(img) as im:
        im.convert("RGB").save(jpg, "JPEG", quality=95)
    with jpg.open("rb") as f:
        r = requests.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={"reqtype": "fileupload", "time": "1h"},
            files={"fileToUpload": (jpg.name, f, "image/jpeg")},
            timeout=120,
        )
    url = r.text.strip()
    if not url.startswith("https://"):
        raise RuntimeError(f"Falha ao hospedar {img.name}: {url[:200]}")
    return url


def aguardar(container: str) -> None:
    for _ in range(24):
        st = api("GET", container, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {container} com status {st}.")
        time.sleep(5)
    raise RuntimeError(f"Container {container} não ficou pronto em 2 minutos.")


def publicar(md: Path) -> None:
    caption, imagens, erros = montar_post(md)
    if erros:
        for e in erros:
            log(f"BLOQUEADO {md.name}: {e}")
        sys.exit(1)

    ig_id = api("GET", "me", fields="user_id")["user_id"]
    with tempfile.TemporaryDirectory() as t:
        urls = [hospedar(img, Path(t)) for img in imagens]
    if len(urls) == 1:
        container = api("POST", f"{ig_id}/media", image_url=urls[0], caption=caption)["id"]
    else:
        filhos = [api("POST", f"{ig_id}/media", image_url=u, is_carousel_item="true")["id"] for u in urls]
        for c in filhos:
            aguardar(c)
        container = api("POST", f"{ig_id}/media", media_type="CAROUSEL",
                        children=",".join(filhos), caption=caption)["id"]
    aguardar(container)
    media_id = api("POST", f"{ig_id}/media_publish", creation_id=container)["id"]
    link = api("GET", media_id, fields="permalink").get("permalink", media_id)

    texto = md.read_text(encoding="utf-8")
    texto = re.sub(r"^Status:\s*aprovado", "Status: publicado", texto, count=1, flags=re.M)
    texto = re.sub(r"^(Status: publicado.*)$", rf"\1\nPublicado: {datetime.now():%Y-%m-%d %H:%M} · {link}",
                   texto, count=1, flags=re.M)
    md.write_text(texto, encoding="utf-8")
    log(f"PUBLICADO {md.name}: {link}")


def agendar(md: Path, quando: str) -> None:
    alvo = datetime.fromisoformat(quando)
    if alvo <= datetime.now():
        sys.exit("ERRO: horário do agendamento já passou.")
    nome = f"TerraForte-{md.stem}"
    cmd = (
        f"$a = New-ScheduledTaskAction -Execute '{sys.executable}' "
        f"-Argument '\"{Path(__file__).resolve()}\" \"{md.resolve()}\" --publicar' -WorkingDirectory '{RAIZ}'; "
        f"$t = New-ScheduledTaskTrigger -Once -At ([datetime]'{alvo:%Y-%m-%dT%H:%M}'); "
        f"$s = New-ScheduledTaskSettingsSet -StartWhenAvailable; "
        f"Register-ScheduledTask -TaskName '{nome}' -Action $a -Trigger $t -Settings $s -Force | Out-Null"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)
    log(f"AGENDADO {md.name} para {alvo:%d/%m/%Y %H:%M} (tarefa '{nome}' no Agendador do Windows)")


def renovar_token() -> None:
    novo = api("GET", "refresh_access_token", grant_type="ig_refresh_token")
    texto = ENV.read_text(encoding="utf-8")
    texto = re.sub(r"^INSTAGRAM_TOKEN=.*$", f"INSTAGRAM_TOKEN={novo['access_token']}", texto, flags=re.M)
    ENV.write_text(texto, encoding="utf-8")
    dias = int(novo.get("expires_in", 0)) // 86400
    log(f"TOKEN renovado — válido por {dias} dias.")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("post", nargs="?", type=Path)
    p.add_argument("--publicar", action="store_true")
    p.add_argument("--agendar", metavar="AAAA-MM-DDTHH:MM")
    p.add_argument("--testar", action="store_true")
    p.add_argument("--renovar-token", action="store_true")
    a = p.parse_args()

    if a.testar or a.renovar_token or a.publicar:
        ENV_DADOS.update(ler_env())
    if a.testar:
        d = api("GET", "me", fields="user_id,username,account_type")
        print(f"Conectado: @{d['username']} ({d.get('account_type')}) · id {d['user_id']}")
        lim = api("GET", f"{d['user_id']}/content_publishing_limit", fields="quota_usage")
        print(f"Publicações pela API nas últimas 24h: {lim['data'][0]['quota_usage']}")
        return
    if a.renovar_token:
        renovar_token()
        return
    if not a.post:
        p.error("informe o arquivo .md do post")

    md = a.post.resolve()
    if a.agendar:
        _, _, erros = montar_post(md)
        if erros:
            sys.exit("\n".join(f"BLOQUEADO: {e}" for e in erros))
        agendar(md, a.agendar)
    elif a.publicar:
        publicar(md)
    else:
        caption, imagens, erros = montar_post(md)
        print(f"Imagens ({len(imagens)}): {', '.join(i.name for i in imagens)}")
        n_tags = len(re.findall(r"#\w+", caption))
        print(f"Legenda: {len(caption)} caracteres · {n_tags} hashtags")
        print("\n".join(f"BLOQUEADO: {e}" for e in erros) or "OK — pronto para publicar.")


if __name__ == "__main__":
    main()

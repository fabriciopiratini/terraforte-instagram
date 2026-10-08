"""Painel interno das publicações da Terra Forte (rede do escritório).

Uso:
  python ferramentas/painel.py          -> http://<ip-deste-pc>:8080/

Lê direto os posts/instagram/AAAA-MM/*.md e os slide-*.png.
Ações: aprovar / voltar a rascunho (muda o Status do .md), pedir alteração (anota em
"## Pedidos de alteração" para o Claude aplicar), excluir (move para _arquivo/, não apaga) e,
na lista, a caixa "Publicado" para confirmar à mão que o post já está no ar.

Publicação (só post "aprovado"; "publicado" nunca é republicado):
- botão Publicar -> publica na hora;
- sem clique -> o painel publica sozinho no horário do campo Data ("19h", "6h30");
- se o horário passou com o PC desligado -> ao ligar, pergunta na tela antes de publicar.
Post desmarcado de "publicado" só volta ao ar pelo botão Publicar.
"""

import ctypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, abort, redirect, render_template_string, request, send_from_directory

RAIZ = Path(__file__).resolve().parent.parent
POSTS = RAIZ / "posts" / "instagram"
ARQUIVO = RAIZ / "_arquivo" / "posts" / "instagram"
PORTA = 8080
SCRIPT_PUBLICAR = RAIZ / "ferramentas" / "publicar_instagram.py"
TOLERANCIA = timedelta(minutes=10)  # atraso maior que isso = PC estava desligado -> perguntar antes
TITULO = "Terra Forte — Instagram"
trava_publicacao = threading.Lock()

app = Flask(__name__)


def campo(texto: str, nome: str) -> str:
    m = re.search(rf"^{nome}:\s*(.+)$", texto, re.M)
    return m.group(1).strip() if m else ""


def secao(texto: str, titulo: str) -> str:
    m = re.search(rf"^## {titulo}\s*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""


def ler_post(md: Path) -> dict:
    texto = md.read_text(encoding="utf-8")
    data_txt = campo(texto, "Data")
    m = re.search(r"\d{4}-\d{2}-\d{2}", data_txt)
    pasta = md.with_suffix("")
    return {
        "mes": md.parent.name,
        "nome": md.stem,
        "status": (campo(texto, "Status").split() or ["?"])[0].lower(),
        "data": date.fromisoformat(m.group(0)) if m else None,
        "data_txt": data_txt,
        "formato": campo(texto, "Formato"),
        "linha": campo(texto, "Linha"),
        "servico": campo(texto, "Serviço"),
        "arte": secao(texto, "Arte"),
        "legenda": secao(texto, "Legenda"),
        "hashtags": secao(texto, "Hashtags"),
        "observacoes": secao(texto, "Observações"),
        "pedidos": re.findall(r"^- \[( |x)\] (.+)$", secao(texto, "Pedidos de alteração"), re.M),
        "slides": sorted(p.name for p in pasta.glob("slide-*.png")) if pasta.is_dir() else [],
    }


def arquivo_md(mes: str, nome: str) -> Path:
    md = POSTS / mes / f"{nome}.md"
    if not re.fullmatch(r"\d{4}-\d{2}", mes) or not re.fullmatch(r"[\w-]+", nome) or not md.is_file():
        abort(404)
    return md


def todos_posts() -> list[dict]:
    posts = [ler_post(md) for md in POSTS.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]/*.md")]
    # com data primeiro, em ordem; sem data ("definir") no fim
    return sorted(posts, key=lambda p: (p["data"] is None, p["data"] or date.max, p["nome"]))


def horario(p: dict) -> datetime | None:
    """Data + hora do campo Data ("2026-10-08 (quinta, 19h)"); sem hora = não publica sozinho."""
    m = re.search(r"\b(\d{1,2})h(\d{2})?\b", p["data_txt"])
    if not p["data"] or not m:
        return None
    return datetime(p["data"].year, p["data"].month, p["data"].day, int(m.group(1)), int(m.group(2) or 0))


def publicar(md: Path) -> tuple[bool, str]:
    """Roda o publicar_instagram.py (que também recusa status diferente de aprovado)."""
    with trava_publicacao:  # botão e agendador nunca publicam ao mesmo tempo
        status = (campo(md.read_text(encoding="utf-8"), "Status").split() or [""])[0].lower()
        if status != "aprovado":
            return False, f"{md.stem}: status '{status}' — só publico post aprovado."
        python = Path(sys.executable).with_name("python.exe")  # o painel roda em pythonw
        r = subprocess.run(
            [str(python), str(SCRIPT_PUBLICAR), str(md), "--publicar"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        linhas = (r.stdout + r.stderr).strip().splitlines()
        return r.returncode == 0, linhas[-1] if linhas else f"erro {r.returncode}"


def caixa(texto: str, estilo: int) -> int:
    return ctypes.windll.user32.MessageBoxW(0, texto, TITULO, estilo | 0x40000)  # sempre no topo


def perguntar_atrasado(md: Path, quando: datetime) -> None:
    texto = (f"O post «{md.stem}» estava agendado para {quando:%d/%m às %H:%M} "
             f"e não foi publicado (o PC estava desligado).\n\nPublicar agora no Instagram?")
    if caixa(texto, 0x4 | 0x20) == 6:  # Sim/Não; 6 = Sim
        ok, saida = publicar(md)
        caixa(saida, 0x40 if ok else 0x10)


def agendador() -> None:
    """A cada minuto: publica o aprovado que chegou na hora; se passou do horário, pergunta."""
    time.sleep(30)  # se outro painel já ocupa a porta, este processo sai antes de publicar
    vistos: set[Path] = set()  # cada post é tentado/perguntado uma vez por sessão (sem repetir publicação)
    while True:
        agora = datetime.now()
        for p in todos_posts():
            quando = horario(p)
            md = POSTS / p["mes"] / f"{p['nome']}.md"
            if p["status"] != "aprovado" or not quando or quando > agora or md in vistos:
                continue
            if "Publicado:" in md.read_text(encoding="utf-8"):
                continue  # já esteve no ar e foi desmarcado: só volta pelo botão Publicar
            vistos.add(md)
            if agora - quando <= TOLERANCIA:
                ok, saida = publicar(md)
                if not ok:
                    threading.Thread(target=caixa, args=(f"Falha ao publicar no horário:\n\n{saida}", 0x10),
                                     daemon=True).start()
            else:
                threading.Thread(target=perguntar_atrasado, args=(md, quando), daemon=True).start()
        time.sleep(60)


BASE = """<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel Terra Forte</title>
<style>
  :root { --marrom:#522800; --verde:#059734; --amarelo:#f2b705; --creme:#f7f3ec; --cinza:#6b6b6b; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:Segoe UI, Arial, sans-serif; background:var(--creme); color:#222; }
  header { background:var(--marrom); color:#fff; padding:14px 24px; display:flex; align-items:center; gap:14px; }
  header img { height:40px; }
  header a { color:#fff; text-decoration:none; font-size:20px; font-weight:600; }
  main { max-width:1100px; margin:0 auto; padding:24px 16px; }
  table { width:100%; border-collapse:collapse; background:#fff; border-radius:8px; overflow:hidden; }
  th, td { padding:10px 12px; text-align:left; border-bottom:1px solid #eee; }
  th { background:#efe7da; font-size:13px; text-transform:uppercase; color:var(--marrom); }
  tr:hover td { background:#faf7f2; }
  tr.linha-publicada td { background:#e8f3e6; }
  tr.linha-publicada:hover td { background:#dcecd9; }
  td a { color:var(--marrom); font-weight:600; text-decoration:none; }
  .st { display:inline-block; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:600; color:#fff; }
  .st-rascunho { background:var(--cinza); } .st-aprovado { background:var(--verde); }
  .st-publicado { background:var(--marrom); } .st-\\? { background:#b00; }
  .meta { color:var(--cinza); margin:4px 0 20px; }
  .slides { display:flex; gap:12px; overflow-x:auto; padding-bottom:10px; }
  .slides img { height:520px; border-radius:6px; box-shadow:0 2px 8px #0002; }
  .caixa { background:#fff; border-radius:8px; padding:16px 20px; margin-top:18px; }
  .caixa h2 { margin:0 0 10px; font-size:16px; color:var(--marrom); }
  .texto { white-space:pre-wrap; line-height:1.5; }
  .vazio { color:var(--cinza); font-style:italic; }
  .acoes { display:flex; flex-wrap:wrap; gap:10px; margin:0 0 16px; }
  .acoes form { margin:0; }
  .bt { display:inline-block; border:0; border-radius:6px; padding:9px 16px; font-size:14px; font-weight:600;
        cursor:pointer; text-decoration:none; color:#fff; background:var(--cinza); font-family:inherit; }
  .bt-voltar { background:#fff; color:var(--marrom); border:1px solid var(--marrom); }
  .bt-aprovar { background:var(--verde); } .bt-publicar { background:var(--marrom); }
  .bt-excluir { background:#b3261e; margin-left:auto; }
  .aviso { background:#fff6d6; border-left:4px solid var(--amarelo); padding:10px 14px; border-radius:6px; margin-bottom:16px; }
  textarea { width:100%; min-height:90px; font:inherit; padding:8px; border:1px solid #ccc; border-radius:6px; }
  select { font:inherit; padding:6px; border-radius:6px; border:1px solid #ccc; }
  .pedidos { margin:12px 0 0; padding-left:20px; } .pedidos li { margin:4px 0; }
  .feito { color:var(--cinza); text-decoration:line-through; }
  .pub { width:20px; height:20px; cursor:pointer; accent-color:var(--marrom); }
</style></head><body>
<header><img src="/logo" alt=""><a href="/">Painel de publicações</a></header>
<main>{% if msg %}<div class="aviso">{{ msg }}</div>{% endif %}{% block corpo %}{% endblock %}</main>
</body></html>"""

LISTA = BASE.replace("{% block corpo %}{% endblock %}", """
<table>
  <tr><th>Data</th><th>Post</th><th>Linha</th><th>Formato</th><th>Status</th><th>Pedidos pendentes</th><th>Publicado</th></tr>
  {% for p in posts %}
  <tr class="{{ 'linha-publicada' if p.status == 'publicado' }}">
    <td>{{ p.data.strftime('%d/%m') if p.data else 'a definir' }}</td>
    <td><a href="/post/{{ p.mes }}/{{ p.nome }}">{{ p.nome }}</a></td>
    <td>{{ p.linha }}</td>
    <td>{{ p.formato }}</td>
    <td><span class="st st-{{ p.status }}">{{ p.status }}</span></td>
    <td>{% set n = p.pedidos|selectattr(0, 'equalto', ' ')|list|length %}{{ n if n else '' }}</td>
    <td><form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/publicado" style="margin:0">
      <input type="checkbox" name="marcado" value="1" class="pub" {{ 'checked' if p.status == 'publicado' }}
        title="Marque para confirmar que este post já foi publicado"
        onchange="if (confirm(this.checked ? 'Confirmar que «{{ p.nome }}» foi publicado?' : 'Desmarcar? O post volta para aprovado.')) this.form.submit(); else this.checked = !this.checked;">
    </form></td>
  </tr>
  {% else %}
  <tr><td colspan="7" class="vazio">Nenhum post encontrado.</td></tr>
  {% endfor %}
</table>""")

POST = BASE.replace("{% block corpo %}{% endblock %}", """
<div class="acoes">
  <a class="bt bt-voltar" href="/">← Voltar às publicações</a>
  {% if p.status == 'rascunho' %}
  <form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/status"><input type="hidden" name="para" value="aprovado">
    <button class="bt bt-aprovar">Aprovar</button></form>
  {% elif p.status == 'aprovado' %}
  <form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/status"><input type="hidden" name="para" value="rascunho">
    <button class="bt">Voltar para rascunho</button></form>
  {% endif %}
  {% if p.status == 'aprovado' %}
  <form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/publicar"
    onsubmit="if (!confirm('Publicar agora no Instagram?')) return false; this.querySelector('button').disabled = true; this.querySelector('button').textContent = 'Publicando…';">
  <button class="bt bt-publicar">Publicar</button></form>
  {% endif %}
  <form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/excluir"
    onsubmit="return confirm('Excluir esta publicação? Ela vai para a pasta _arquivo (dá para recuperar).')">
    <button class="bt bt-excluir">Excluir</button></form>
</div>
<h1 style="margin:0;color:var(--marrom)">{{ p.nome }}</h1>
<p class="meta"><span class="st st-{{ p.status }}">{{ p.status }}</span>
  &nbsp; {{ p.data_txt }} · {{ p.formato }} · {{ p.linha }} · {{ p.servico }}</p>
{% if p.slides %}
<div class="slides">
  {% for s in p.slides %}<a href="/img/{{ p.mes }}/{{ p.nome }}/{{ s }}" target="_blank">
    <img src="/img/{{ p.mes }}/{{ p.nome }}/{{ s }}" alt="{{ s }}"></a>{% endfor %}
</div>
<!-- visualizador: clique abre em tela cheia; setas, teclado ou arrastar no celular passam os slides -->
<div id="vis" onclick="if(event.target===this)fechar()">
  <button class="vis-fechar" onclick="fechar()">×</button>
  <button class="vis-seta" style="left:12px" onclick="passo(-1)">‹</button>
  <img id="vis-img" alt="">
  <button class="vis-seta" style="right:12px" onclick="passo(1)">›</button>
  <div id="vis-cont"></div>
</div>
<style>
  #vis { display:none; position:fixed; inset:0; background:#000d; z-index:10; align-items:center; justify-content:center; }
  #vis.aberto { display:flex; }
  #vis-img { max-width:92vw; max-height:88vh; border-radius:6px; }
  .vis-seta, .vis-fechar { position:absolute; background:#fff3; color:#fff; border:0; cursor:pointer; font-size:44px; line-height:1; border-radius:50%; width:60px; height:60px; }
  .vis-seta { top:50%; transform:translateY(-50%); }
  .vis-fechar { top:12px; right:12px; font-size:36px; }
  #vis-cont { position:absolute; bottom:14px; color:#fff; font-size:16px; }
</style>
<script>
  const fotos = [...document.querySelectorAll('.slides a')].map(a => a.href);
  let atual = 0, toqueX = null;
  const vis = document.getElementById('vis');
  function mostrar(i) {
    atual = (i + fotos.length) % fotos.length;
    document.getElementById('vis-img').src = fotos[atual];
    document.getElementById('vis-cont').textContent = (atual + 1) + ' / ' + fotos.length;
    vis.classList.add('aberto');
  }
  function passo(d) { mostrar(atual + d); }
  function fechar() { vis.classList.remove('aberto'); }
  document.querySelectorAll('.slides a').forEach((a, i) => a.onclick = e => { e.preventDefault(); mostrar(i); });
  document.addEventListener('keydown', e => {
    if (!vis.classList.contains('aberto')) return;
    if (e.key === 'ArrowRight') passo(1);
    else if (e.key === 'ArrowLeft') passo(-1);
    else if (e.key === 'Escape') fechar();
  });
  vis.addEventListener('touchstart', e => toqueX = e.touches[0].clientX);
  vis.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - toqueX;
    if (Math.abs(dx) > 40) passo(dx < 0 ? 1 : -1);
  });
</script>
{% else %}
<div class="caixa"><h2>Arte (ainda sem imagens — briefing)</h2><div class="texto">{{ p.arte }}</div></div>
{% endif %}
<div class="caixa"><h2>Legenda</h2>
  <div class="texto">{{ p.legenda or '' }}</div>
  {% if not p.legenda %}<span class="vazio">sem legenda</span>{% endif %}
</div>
<div class="caixa"><h2>Hashtags</h2><div class="texto">{{ p.hashtags }}</div></div>
{% if p.observacoes %}
<div class="caixa"><h2>Observações</h2><div class="texto">{{ p.observacoes }}</div></div>
{% endif %}
<div class="caixa" id="pedidos"><h2>Pedir alteração</h2>
  <form method="post" action="/post/{{ p.mes }}/{{ p.nome }}/pedido">
    <p style="margin:0 0 8px">Onde:
      <select name="onde"><option>Geral</option><option>Legenda</option><option>Hashtags</option>
        {% for s in p.slides %}<option>Slide {{ loop.index }}</option>{% endfor %}</select></p>
    <textarea name="texto" required placeholder="Descreva o que deve mudar. O Claude aplica e a página é atualizada."></textarea>
    <p style="margin:8px 0 0"><button class="bt bt-aprovar">Enviar pedido</button></p>
  </form>
  {% if p.pedidos %}<ul class="pedidos">
    {% for feito, txt in p.pedidos %}<li class="{{ 'feito' if feito == 'x' }}">{{ txt }}</li>{% endfor %}
  </ul>{% endif %}
</div>""")


@app.route("/")
def lista():
    return render_template_string(LISTA, posts=todos_posts(), msg=request.args.get("msg"))


@app.route("/post/<mes>/<nome>")
def post(mes: str, nome: str):
    return render_template_string(POST, p=ler_post(arquivo_md(mes, nome)), msg=request.args.get("msg"))


@app.post("/post/<mes>/<nome>/status")
def mudar_status(mes: str, nome: str):
    md = arquivo_md(mes, nome)
    para = request.form.get("para")
    texto = md.read_text(encoding="utf-8")
    atual = (campo(texto, "Status").split() or [""])[0].lower()
    # só rascunho <-> aprovado; "publicado" quem grava é o script de publicação
    if (atual, para) not in (("rascunho", "aprovado"), ("aprovado", "rascunho")):
        abort(400)
    md.write_text(re.sub(r"^Status:\s*\w+", f"Status: {para}", texto, count=1, flags=re.M), encoding="utf-8")
    return redirect(f"/post/{mes}/{nome}?msg=Status alterado para {para}.")


@app.post("/post/<mes>/<nome>/publicado")
def marcar_publicado(mes: str, nome: str):
    md = arquivo_md(mes, nome)
    para = "publicado" if request.form.get("marcado") else "aprovado"  # desmarcar = desfazer um clique errado
    texto = re.sub(r"^Status:\s*\w+", f"Status: {para}", md.read_text(encoding="utf-8"), count=1, flags=re.M)
    if para == "publicado" and not re.search(r"^Publicado:", texto, re.M):
        # registro impede o agendador de publicar de novo se o post for desmarcado depois
        texto = re.sub(r"^(Status: publicado.*)$", rf"\1\nPublicado: {datetime.now():%Y-%m-%d %H:%M} · marcado no painel",
                       texto, count=1, flags=re.M)
    md.write_text(texto, encoding="utf-8")
    return redirect(f"/?msg={nome}: status {para}.")


@app.post("/post/<mes>/<nome>/publicar")
def publicar_agora(mes: str, nome: str):
    ok, saida = publicar(arquivo_md(mes, nome))
    return redirect(f"/post/{mes}/{nome}?msg={'' if ok else 'Não publicado — '}{saida}")


@app.post("/post/<mes>/<nome>/pedido")
def novo_pedido(mes: str, nome: str):
    md = arquivo_md(mes, nome)
    pedido = " ".join(request.form.get("texto", "").split())  # uma linha só, para não quebrar o .md
    if not pedido:
        return redirect(f"/post/{mes}/{nome}")
    onde = request.form.get("onde", "Geral")[:20]
    linha = f"- [ ] {datetime.now():%d/%m %H:%M} · {onde}: {pedido}\n"
    texto = md.read_text(encoding="utf-8").rstrip("\n") + "\n"
    if "## Pedidos de alteração" not in texto:
        texto += "\n## Pedidos de alteração\n"
    md.write_text(texto + linha, encoding="utf-8")  # a seção fica sempre no fim do arquivo
    return redirect(f"/post/{mes}/{nome}?msg=Pedido registrado. Avise o Claude para aplicar.#pedidos")


@app.post("/post/<mes>/<nome>/excluir")
def excluir(mes: str, nome: str):
    md = arquivo_md(mes, nome)
    destino = ARQUIVO / mes
    destino.mkdir(parents=True, exist_ok=True)
    sufixo = f"_{datetime.now():%Y%m%d-%H%M%S}"  # evita sobrescrever um excluído anterior de mesmo nome
    shutil.move(str(md), str(destino / f"{nome}{sufixo}.md"))
    if md.with_suffix("").is_dir():
        shutil.move(str(md.with_suffix("")), str(destino / f"{nome}{sufixo}"))
    return redirect(f"/?msg={nome} movido para _arquivo/posts/instagram/{mes}.")


@app.route("/img/<mes>/<nome>/<arquivo>")
def imagem(mes: str, nome: str, arquivo: str):
    if not re.fullmatch(r"\d{4}-\d{2}", mes) or not re.fullmatch(r"slide-\d+\.png", arquivo):
        abort(404)
    return send_from_directory(POSTS / mes / nome, arquivo)  # send_from_directory barra "../"


@app.route("/logo")
def logo():
    return send_from_directory(RAIZ / "marca", "logo.png")


if __name__ == "__main__":
    threading.Thread(target=agendador, daemon=True).start()
    app.run(host="0.0.0.0", port=PORTA, threaded=True)

"""
Notificador de resultado da Mega-Sena via Telegram.

Fluxo:
1. Busca o concurso mais recente na API da Caixa.
2. Compara com o último concurso já notificado (salvo em ultimo_concurso.json).
3. Se for um concurso novo, envia mensagem pro Telegram e atualiza o arquivo.

Pensado para rodar como um passo a mais no workflow do GitHub Actions do LotoCiclo3.
"""

import json
import os
import sys
from pathlib import Path

import requests

# --- Configuração ---
# Guarde estes valores como Secrets no GitHub Actions:
#   TELEGRAM_BOT_TOKEN
#   TELEGRAM_CHAT_ID
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CAIXA_API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
ARQUIVO_ULTIMO_CONCURSO = Path("ultimo_concurso.json")


def buscar_resultado_mais_recente() -> dict:
    """Busca o resultado do concurso mais recente na API da Caixa."""
    resp = requests.get(CAIXA_API_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def carregar_ultimo_concurso_salvo() -> int | None:
    """Lê o número do último concurso que já foi notificado."""
    if not ARQUIVO_ULTIMO_CONCURSO.exists():
        return None
    with open(ARQUIVO_ULTIMO_CONCURSO, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados.get("numero")


def salvar_ultimo_concurso(numero: int) -> None:
    """Salva o número do concurso que acabou de ser notificado."""
    with open(ARQUIVO_ULTIMO_CONCURSO, "w", encoding="utf-8") as f:
        json.dump({"numero": numero}, f)


def montar_mensagem(resultado: dict) -> str:
    numero = resultado.get("numero")
    data = resultado.get("dataApuracao")
    dezenas = resultado.get("listaDezenas", [])
    acumulou = resultado.get("acumulado", False)
    valor_estimado_proximo = resultado.get("valorEstimadoProximoConcurso")

    dezenas_str = " - ".join(dezenas)

    linhas = [
        f"🎰 Mega-Sena — Concurso {numero} ({data})",
        f"Dezenas: {dezenas_str}",
    ]

    if acumulou:
        linhas.append("Acumulou! 💰")
        if valor_estimado_proximo:
            linhas.append(f"Próximo prêmio estimado: R$ {valor_estimado_proximo:,.2f}")
    else:
        premiacoes = resultado.get("listaRateioPremio", [])
        sena = next((p for p in premiacoes if p.get("descricaoFaixa") == "1º Faixa"), None)
        if sena and sena.get("numeroDeGanhadores", 0) > 0:
            linhas.append(f"Teve ganhador(es) da Sena: {sena['numeroDeGanhadores']}")

    return "\n".join(linhas)


def enviar_telegram(mensagem: str) -> None:
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": mensagem},
        timeout=15,
    )
    resp.raise_for_status()


def main() -> None:
    resultado = buscar_resultado_mais_recente()
    numero_atual = resultado.get("numero")

    ultimo_numero = carregar_ultimo_concurso_salvo()

    if ultimo_numero == numero_atual:
        print(f"Nenhum concurso novo (último notificado: {ultimo_numero}).")
        return

    mensagem = montar_mensagem(resultado)
    enviar_telegram(mensagem)
    salvar_ultimo_concurso(numero_atual)
    print(f"Notificação enviada para o concurso {numero_atual}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

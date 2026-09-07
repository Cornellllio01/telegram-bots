# telegram-bots

Bots de notificação via Telegram.

## mega-sena

Verifica o resultado mais recente da Mega-Sena e envia uma notificação para um chat/canal do Telegram quando sai um concurso novo. Roda automaticamente via GitHub Actions (`.github/workflows/mega-sena.yml`).

### Configuração

No repositório, em **Settings > Secrets and variables > Actions**, adicione:

- `TELEGRAM_BOT_TOKEN` — token do bot obtido via BotFather
- `TELEGRAM_CHAT_ID` — id do chat/canal para onde a notificação será enviada

### Rodar localmente

```bash
cd mega-sena
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="seu_token"
export TELEGRAM_CHAT_ID="seu_chat_id"
python notificar_mega_sena.py
```

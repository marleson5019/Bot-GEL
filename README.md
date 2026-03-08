# Bot GEL

Bot do Discord com verificacao por codigo via Google Sheets.

## Rodando localmente

1. Crie e ative um ambiente virtual.
2. Instale dependencias:

```bash
pip install -r requirements.txt
```

3. Defina as variaveis de ambiente:

- `DISCORD_TOKEN`
- `GOOGLE_CREDENTIALS_JSON` (JSON completo da service account em uma linha)
- `GOOGLE_CREDENTIALS_BASE64` (opcional, mesma credencial em Base64)
- `GOOGLE_SHEET_NAME` (opcional, padrao `Database-GEL-Teste`)

4. Inicie:

```bash
python bot.py
```

## Deploy no Render

Este repositorio inclui `render.yaml` para criar um Worker Service no Render.

Variaveis obrigatorias no Render:

- `DISCORD_TOKEN`
- `GOOGLE_CREDENTIALS_JSON` (ou `GOOGLE_CREDENTIALS_BASE64`)

Variavel opcional:

- `GOOGLE_SHEET_NAME`

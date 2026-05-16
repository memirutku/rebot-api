# REBOT API

KOBİ atık/elektrik/su/lojistik faturalarını **BDDK YVO** ve **GHG Protocol** uyumlu, **Ed25519 imzalı** ESG bundle'a dönüştüren açık çekirdek API.

[![License: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue.svg)](LICENSE)
[![Data License: CC BY-SA 4.0](https://img.shields.io/badge/data-CC%20BY--SA%204.0-lightgrey.svg)](DATA-LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](PROJECT.md#yol-haritası)
[![CI](https://github.com/memirutku/rebot-api/actions/workflows/ci.yml/badge.svg)](https://github.com/memirutku/rebot-api/actions/workflows/ci.yml)

> 📖 **Proje hikayesi, vizyon, yol haritası** → [PROJECT.md](PROJECT.md)
> 📊 **Veri durumu, ne eksik, plan** → [DATA-ROADMAP.md](DATA-ROADMAP.md)

## Canlı

| | |
|---|---|
| 🌐 Landing | <https://memirutku.github.io/rebot-api/> |
| 🔌 API | <https://rebot-api.onrender.com> |
| 📘 Swagger UI (API ref) | <https://rebot-api.onrender.com/docs> |
| 💬 Discussions | <https://github.com/memirutku/rebot-api/discussions> |

> ⚠️ Render free tier — 15 dakika inaktiviteden sonra uyur, ilk istek 30-60 sn sürebilir.

## 30 saniyelik demo

```bash
URL=https://rebot-api.onrender.com

# 1. Fatura gönder → 2. İmzalı ESG bundle al → 3. Doğrulama için public key
curl -X POST $URL/v1/ingest -H "Content-Type: application/json" \
     -d @examples/requests/waste_ingest.json
curl "$URL/v1/esg/9876543210?period=2025-Q2"
curl $URL/v1/signing/pubkey
```

**Tam API referansı için:** <https://rebot-api.onrender.com/docs> (interaktif Swagger UI, her endpoint için parametre, doğrulama kuralları, örnek istek/yanıt orada).

## Yerel kurulum

```bash
git clone https://github.com/memirutku/rebot-api.git
cd rebot-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload
# → http://localhost:8000/docs
```

Görsel demo: `python demo/app.py` (Gradio, http://localhost:7860).

## Lisans

- **Kod**: [Apache 2.0](LICENSE)
- **Veri & şemalar**: [CC BY-SA 4.0](DATA-LICENSE)

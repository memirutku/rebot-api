---
title: REBOT API Demo
emoji: 🌱
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: KOBİ atık faturasından BDDK YVO uyumlu imzalı ESG bundle
---

# REBOT API Demo — KOBİ ESG Doğrulama

Görsel demo: bir KOBİ atık taşıma faturasını seçin veya yapıştırın, **BDDK YVO Tebliği** uyumlu, **GHG Protocol Scope 3.5** hesaplı, **Ed25519 imzalı** ESG bundle'ı tarayıcıda canlı görün.

Bu demo iş mantığı içermez — doğrudan canlı API'ye konuşur: https://rebot-api.onrender.com

## Yerel çalıştırma

```bash
pip install -r requirements.txt
python app.py
# http://localhost:7860
```

## Hugging Face Spaces'e deploy

Bu klasörü ayrı bir HF Space repo'su olarak yayınlayın. Adım adım rehber: [`../docs/deploy-hf-spaces.md`](../docs/deploy-hf-spaces.md)

## Lisans

[Apache 2.0](../LICENSE)

# REBOT API

> **TR** &nbsp;KOBİlerin atık, elektrik, su ve lojistik faturalarını **BDDK YVO Tebliği** ve **GHG Protocol** uyumlu, doğrulanabilir ESG verisine dönüştüren açık çekirdek bir API.
>
> **EN** &nbsp;An open-core API that converts SME utility invoices into **BDDK YVO** and **GHG Protocol** compliant, verifiable ESG data.

[![License: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue.svg)](LICENSE)
[![Data License: CC BY-SA 4.0](https://img.shields.io/badge/data-CC%20BY--SA%204.0-lightgrey.svg)](DATA-LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#)
[![CI](https://github.com/memirutku/rebot-api/actions/workflows/ci.yml/badge.svg)](https://github.com/memirutku/rebot-api/actions/workflows/ci.yml)

**Canlı bağlantılar / Live links**

- 🌐 Landing: <https://memirutku.github.io/rebot-api/>
- 🔌 API: <https://rebot-api.onrender.com>
- 📘 Swagger UI: <https://rebot-api.onrender.com/docs>
- 💬 Tartışma / Discussions: <https://github.com/memirutku/rebot-api/discussions>

---

## 🇹🇷 Türkçe

### Sorun
BDDK'nın Nisan 2025'te yayımladığı **Yeşil Varlık Oranı (YVO) Tebliği**, bankaların yeşil kredi portföylerini bağımsız doğrulanmış çevresel veriyle tevsik etmesini zorunlu kıldı. KOBİler bu veriyi üretemiyor: ya hiç ölçülmüyor ya da firma beyanına dayanıyor. Türkiye'de **BDDK YVO için makine-okunabilir açık veri standardı yok.**

### Çözüm
REBOT API, KOBİ faturalarını alır, **GHG Protocol Scope 1/2/3** hesabını yapar, **BDDK YVO Ek-1** hedeflerine eşler, sonucu imzalı bir bundle olarak bankalara sunar. Üç katman halinde:

1. **Giriş** — `POST /v1/invoices`: PDF/CSV/JSON fatura kabul, normalize
2. **Doğrulama** — Açık emisyon faktör kataloğu (DEFRA + TÜİK)
3. **Çıkış** — `GET /v1/esg/{tax_id}`: BDDK YVO + EFRAG VSME XBRL uyumlu bundle, **Ed25519 imzalı**

### Açık çekirdek
Bu repo REBOT API'nin açık çekirdek motorudur: API uç noktaları, parser'lar, GHG hesap motoru, YVO mapper, JSON şemalar ve emisyon faktör kataloğu Apache 2.0 + CC BY-SA 4.0 lisanslıdır. Ticari sürüm için iletişim: GitHub Discussions.

### Hızlı başlangıç
```bash
git clone https://github.com/memirutku/rebot-api.git
cd rebot-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload
# Tarayıcı: http://localhost:8000/docs
```

### Canlı demo — uçtan uca (3 adım)

🟢 **<https://rebot-api.onrender.com>**

```bash
URL=https://rebot-api.onrender.com

# 1. Atık taşıma faturası gönder
curl -X POST $URL/v1/invoices -H "Content-Type: application/json" \
     -d @examples/requests/waste_ingest.json

# 2. KOBİ bazında dönemsel ESG bundle al (imzalı)
curl "$URL/v1/esg/9876543210?period=2025-Q2" | jq .

# 3. İmza doğrulama için public key
curl $URL/v1/signing/public-key | jq .
```

İmza doğrulama (Python):

```python
import base64, json, requests
from nacl.signing import VerifyKey

URL = "https://rebot-api.onrender.com"
resp = requests.get(f"{URL}/v1/esg/9876543210?period=2025-Q2").json()
pub  = requests.get(f"{URL}/v1/signing/public-key").json()

vk = VerifyKey(base64.b64decode(pub["verify_key_b64"]))
canonical = json.dumps(resp["bundle"], sort_keys=True, separators=(",",":"),
                      ensure_ascii=False).encode()
vk.verify(canonical, base64.b64decode(resp["signature"]["value_b64"]))  # tampered → raises
print("✅ İmza geçerli, BDDK YVO bundle doğrulandı")
```

**Diğer uç noktalar:**

```bash
curl $URL/health                                        # liveness
curl "$URL/v1/emission-factors?region=TR"                        # TR emisyon faktörleri
curl $URL/v1/emission-factors/electricity.tr.grid_average        # tek faktör
curl "$URL/v1/ewc-codes?chapter=20"                   # EWC kodları (chapter 20 — evsel)
```

Örnek imzalı bundle: [`examples/responses/esg_bundle_signed.json`](examples/responses/esg_bundle_signed.json)

> ⚠️ Render free tier — 15 dakika inaktiviteden sonra uyur. **İlk istek 30-60 saniye** sürebilir (cold start), sonraki istekler hızlı. Deploy adımları: [`docs/deploy-render.md`](docs/deploy-render.md).

### Görsel demo (Gradio)
[`demo/app.py`](demo/app.py) Hugging Face Spaces uyumlu bir Gradio arayüzü içerir. Programcı olmayan biri için fatura JSON yapıştır → imzalı YVO bundle gör akışı sunar. Yerel çalıştırma:

```bash
pip install -r demo/requirements.txt
python demo/app.py            # http://localhost:7860
```

HF Spaces'e deploy: [`docs/deploy-hf-spaces.md`](docs/deploy-hf-spaces.md).

### Landing page
[`site/index.html`](site/index.html) — tek dosyalık static landing page, GitHub Pages'te otomatik yayınlanır: [memirutku.github.io/rebot-api](https://memirutku.github.io/rebot-api/). TR/EN dil değiştirici + favicon + og:image dahil. Deploy ayarları: [`docs/deploy-github-pages.md`](docs/deploy-github-pages.md).

### Lisans
- **Kod**: [Apache 2.0](LICENSE)
- **Veri ve şemalar**: [CC BY-SA 4.0](DATA-LICENSE)

### Katkı
- Issue açın, PR atın.
- Tartışma: [GitHub Discussions](https://github.com/memirutku/rebot-api/discussions) — Türkiye yeşil fintech için açık forum.

---

## 🇬🇧 English

### Problem
Turkey's banking regulator (BDDK) issued the **Green Asset Ratio (YVO) Regulation** in April 2025, requiring banks to back green loan portfolios with independently verified environmental data. SMEs cannot produce that data — it's either unmeasured or self-reported. **Turkey has no machine-readable open data standard for YVO reporting.**

### Solution
REBOT API ingests SME utility invoices, runs **GHG Protocol Scope 1/2/3** accounting, maps to **BDDK YVO Annex 1** objectives, and emits a signed bundle to banks. Three layers:

1. **Ingest** — `POST /v1/invoices`: accept PDF/CSV/JSON invoices, normalize
2. **Verify** — Open emission factor catalogue (DEFRA + TÜİK Turkey-grid)
3. **Emit** — `GET /v1/esg/{tax_id}`: BDDK YVO + EFRAG VSME XBRL compatible bundle, **Ed25519 signed**

### Open core
This repository is REBOT API's open-core engine: endpoints, parsers, GHG accounting, YVO mapper, JSON schemas, and emission-factor catalogue, all under Apache 2.0 + CC BY-SA 4.0. For the commercial edition, reach out via GitHub Discussions.

### Quick start
```bash
git clone https://github.com/memirutku/rebot-api.git
cd rebot-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload
# Browser: http://localhost:8000/docs
```

### Live demo — end-to-end (3 steps)

🟢 **<https://rebot-api.onrender.com>**

```bash
URL=https://rebot-api.onrender.com

# 1. Submit a waste-transport invoice
curl -X POST $URL/v1/invoices -H "Content-Type: application/json" \
     -d @examples/requests/waste_ingest.json

# 2. Fetch the signed ESG bundle for the SME and period
curl "$URL/v1/esg/9876543210?period=2025-Q2" | jq .

# 3. Get the public key to verify the signature
curl $URL/v1/signing/public-key | jq .
```

Verify the signature (Python):

```python
import base64, json, requests
from nacl.signing import VerifyKey

URL = "https://rebot-api.onrender.com"
resp = requests.get(f"{URL}/v1/esg/9876543210?period=2025-Q2").json()
pub  = requests.get(f"{URL}/v1/signing/public-key").json()

vk = VerifyKey(base64.b64decode(pub["verify_key_b64"]))
canonical = json.dumps(resp["bundle"], sort_keys=True, separators=(",",":"),
                      ensure_ascii=False).encode()
vk.verify(canonical, base64.b64decode(resp["signature"]["value_b64"]))  # tampered → raises
print("✅ Signature valid — BDDK YVO bundle verified")
```

**Other endpoints:**

```bash
curl $URL/health                                        # liveness
curl "$URL/v1/emission-factors?region=TR"                        # TR emission factors
curl $URL/v1/emission-factors/electricity.tr.grid_average        # single factor
curl "$URL/v1/ewc-codes?chapter=20"                   # EWC waste codes (chapter 20 — municipal)
```

Sample signed bundle: [`examples/responses/esg_bundle_signed.json`](examples/responses/esg_bundle_signed.json)

> ⚠️ Render free tier — sleeps after 15 minutes of inactivity. **First request takes 30-60 seconds** (cold start); subsequent requests are fast. Deploy steps: [`docs/deploy-render.md`](docs/deploy-render.md).

### Visual demo (Gradio)
[`demo/app.py`](demo/app.py) is a Hugging Face Spaces compatible Gradio UI. It lets non-developers paste an invoice JSON and watch the signed YVO bundle render in the browser. Run locally:

```bash
pip install -r demo/requirements.txt
python demo/app.py            # http://localhost:7860
```

Deploy to HF Spaces: [`docs/deploy-hf-spaces.md`](docs/deploy-hf-spaces.md).

### Landing page
[`site/index.html`](site/index.html) — single-file static landing page, auto-deployed to GitHub Pages: [memirutku.github.io/rebot-api](https://memirutku.github.io/rebot-api/). Built-in TR/EN language toggle, favicon, and og:image. Setup: [`docs/deploy-github-pages.md`](docs/deploy-github-pages.md).

### Inspirations
- [fingreen-ai/greenlang](https://github.com/fingreen-ai/greenlang) — open ESG methodology (global parallel)
- [EFRAG VSME XBRL Taxonomy](https://www.efrag.org/en/vsme-digital-template-and-xbrl-taxonomy) — EU SME machine-readable standard (interop target)
- [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) — emission factor catalogue patterns

### License
- **Code**: [Apache 2.0](LICENSE)
- **Data & schemas**: [CC BY-SA 4.0](DATA-LICENSE)

### Contribute
- Open an issue, send a PR.
- Discussion: [GitHub Discussions](https://github.com/memirutku/rebot-api/discussions).

---

## Veri akışı / Data flow

```
        KOBİ veya KOBİ'nin muhasebecisi          SME or its accountant
                  │ (1) atık taşıma fatura JSON   waste-transport invoice JSON
                  ▼
   ┌─────────────────────────────────────────┐
   │  POST /v1/invoices                        │
   │   • EWC kodu + birim doğrulaması        │
   │   • Pydantic ile şema validation        │
   │   • SHA-256 dedupe                      │
   │   • Verifier (GHG Protocol Scope 3.5)   │
   └────────────────┬────────────────────────┘
                    ▼  store
   ┌─────────────────────────────────────────┐
   │  GET /v1/esg/{tax_id}                   │
   │   • Dönemsel toplam (period filtre)     │
   │   • BDDK YVO Ek-1 Hedef 4 alignment     │
   │   • Ed25519 imzalı bundle               │
   └────────────────┬────────────────────────┘
                    ▼
              Banka / Regulator
              (verifies via /v1/signing/public-key)
```

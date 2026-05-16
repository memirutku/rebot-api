# REBOT API

> KOBİlerin atık, elektrik, su ve lojistik faturalarını **BDDK YVO Tebliği** ve **GHG Protocol** uyumlu, doğrulanabilir ESG verisine dönüştüren açık çekirdek bir API.
>
> An open-core API that converts SME utility invoices into BDDK YVO + GHG Protocol compliant, verifiable ESG data.

[![License: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue.svg)](LICENSE)
[![Data License: CC BY-SA 4.0](https://img.shields.io/badge/data-CC%20BY--SA%204.0-lightgrey.svg)](DATA-LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#yol-haritası--roadmap)

---

## Türkçe

### Sorun
BDDK'nın Nisan 2025'te yayımladığı **Yeşil Varlık Oranı (YVO) Tebliği**, bankaların yeşil kredi portföylerini bağımsız doğrulanmış çevresel veriyle tevsik etmesini zorunlu kıldı. KOBİler bu veriyi üretemiyor: ya hiç ölçülmüyor ya da firma beyanına dayanıyor. Türkiye'de **BDDK YVO için makine-okunabilir açık veri standardı yok.**

### Çözüm
REBOT API, KOBİ faturalarını alır, **GHG Protocol Scope 1/2/3** hesabını yapar, **BDDK YVO Ek-1** hedeflerine eşler, sonucu imzalı bir bundle olarak bankalara sunar. Üç katman halinde:

1. **Giriş** — `POST /v1/ingest`: PDF/CSV/JSON fatura kabul, normalize
2. **Doğrulama** — Açık emisyon faktör kataloğu (DEFRA + TÜİK)
3. **Çıkış** — `GET /v1/esg/{tax_id}`: BDDK YVO + EFRAG VSME XBRL uyumlu bundle, Ed25519 imzalı

### Açık çekirdek modeli
| Açık (bu repo) | Kapalı (ticari premium) |
|---|---|
| API motoru, parser'lar, GHG hesabı, YVO mapper, veri şemaları, emisyon faktörleri | Banka konektörleri, multi-tenant SaaS, audit dashboard, KOBİ onboarding UI |

### Hızlı başlangıç
```bash
git clone https://github.com/memirutku/rebot-api.git
cd rebot-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn api.main:app --reload
# Tarayıcı: http://localhost:8000/docs
```

### Canlı demo

🟢 **https://rebot-api.onrender.com** — Swagger UI: [/docs](https://rebot-api.onrender.com/docs)

**Uçtan uca akış (3 adım):**

```bash
URL=https://rebot-api.onrender.com

# 1. Atık taşıma faturası gönder
curl -X POST $URL/v1/ingest -H "Content-Type: application/json" \
     -d @examples/requests/waste_ingest.json

# 2. KOBİ bazında dönemsel ESG bundle al (imzalı)
curl "$URL/v1/esg/9876543210?period=2025-Q2" | jq .

# 3. İmza doğrulama için public key
curl $URL/v1/signing/pubkey | jq .
```

İmza doğrulama (Python):

```python
import base64, json, requests
from nacl.signing import VerifyKey

resp = requests.get(f"{URL}/v1/esg/9876543210?period=2025-Q2").json()
pub  = requests.get(f"{URL}/v1/signing/pubkey").json()

vk = VerifyKey(base64.b64decode(pub["verify_key_b64"]))
canonical = json.dumps(resp["bundle"], sort_keys=True, separators=(",",":"),
                      ensure_ascii=False).encode()
vk.verify(canonical, base64.b64decode(resp["signature"]["value_b64"]))  # raises if tampered
print("✅ Imza geçerli, BDDK YVO bundle doğrulandı")
```

**Diğer endpoint'ler:**

```bash
curl $URL/health                                        # liveness
curl "$URL/v1/factors?region=TR"                        # TR emisyon faktörleri
curl $URL/v1/factors/electricity.tr.grid_average        # tek faktör
```

Örnek imzalı bundle: [`examples/responses/esg_bundle_signed.json`](examples/responses/esg_bundle_signed.json)

> ⚠️ Render free tier — 15 dakika inaktiviteden sonra uyur. **İlk istek 30-60 saniye** sürebilir (cold start), sonraki istekler hızlı. Deploy adımları: [`docs/deploy-render.md`](docs/deploy-render.md).

### Lisans
- **Kod**: [Apache 2.0](LICENSE)
- **Veri ve şemalar**: [CC BY-SA 4.0](DATA-LICENSE)

### Katkı
- Issue açın, PR atın. `CONTRIBUTING.md` (gelecek) ve `CODE_OF_CONDUCT.md` (gelecek) takip edin.
- Tartışma: GitHub Discussions (Türkiye yeşil fintech için açık).

---

## English

### Problem
Turkey's banking regulator (BDDK) issued the **Green Asset Ratio (YVO) Regulation** in April 2025, requiring banks to back green loan portfolios with independently verified environmental data. SMEs cannot produce this data — it's either unmeasured or self-reported. **Turkey lacks a machine-readable open data standard for YVO reporting.**

### Solution
REBOT API ingests SME utility invoices, runs **GHG Protocol Scope 1/2/3** accounting, maps to **BDDK YVO Annex-1** objectives, and emits a signed bundle to banks. Three layers:

1. **Ingest** — `POST /v1/ingest`: accept PDF/CSV/JSON invoices, normalize
2. **Verify** — Open emission factor catalogue (DEFRA + TÜİK Turkey-grid)
3. **Emit** — `GET /v1/esg/{tax_id}`: BDDK YVO + EFRAG VSME XBRL compatible bundle, Ed25519 signed

### Open core
- **Open**: API engine, parsers, GHG accounting, YVO mapper, schemas, emission factor data
- **Closed**: Bank connectors, multi-tenant SaaS, audit dashboard, SME onboarding UI

### Quick start
See **Hızlı başlangıç** above — same commands.

### Inspirations
- [fingreen-ai/greenlang](https://github.com/fingreen-ai/greenlang) — open ESG methodology (global parallel)
- [EFRAG VSME XBRL Taxonomy](https://www.efrag.org/en/vsme-digital-template-and-xbrl-taxonomy) — EU SME machine-readable standard (interop target)
- [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) — emission factor catalogue patterns

### License
- **Code**: [Apache 2.0](LICENSE)
- **Data & schemas**: [CC BY-SA 4.0](DATA-LICENSE)

---

## Veri akışı

```
        KOBİ veya KOBİ'nin muhasebecisi
                  │ (1) atık taşıma fatura JSON
                  ▼
   ┌─────────────────────────────────────────┐
   │  POST /v1/ingest                        │
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
              (verifies via /v1/signing/pubkey)
```

## Yol haritası / Roadmap

**Tamamlandı**
- [x] Repo scaffold, FastAPI iskelet, `/v1/factors` (DEFRA 2024 + TEİAŞ 2023)
- [x] Canlı demo (Render free tier)
- [x] `parser/waste.py` JSON yolu + `POST /v1/ingest` + dedupe
- [x] `core/verifier.py` — GHG Protocol Scope 3.5 (atık)
- [x] `core/bddk_mapper.py` — YVO Ek-1 Objective 4 (circular economy)
- [x] `GET /v1/esg/{tax_id}` — dönemsel imzalı bundle
- [x] `core/signing.py` — Ed25519 detached signature + `/v1/signing/pubkey`

**Sırada**
- [ ] Görsel demo (Gradio @ Hugging Face Spaces)
- [ ] Branded landing page
- [ ] `parser/electricity.py` — EPDK formatlı elektrik faturası → Scope 2
- [ ] `parser/water.py` — İSKİ/İZSU/ASKİ örnekleri → Scope 3.4
- [ ] `parser/logistics.py` — akaryakıt + km bazlı → Scope 1
- [ ] `core/xbrl.py` — EFRAG VSME XBRL-JSON çıktı (AB interop)
- [ ] BDDK YVO Ek-1 Objective 1 (climate mitigation) + Objective 5 (pollution)
- [ ] Atık fatura PDF parser (anonimleştirilmiş örnekler gelince)
- [ ] Üretim için SQLite/Postgres backed storage

İlerleyiş [GitHub Issues](https://github.com/memirutku/rebot-api/issues) ve [Discussions](https://github.com/memirutku/rebot-api/discussions) üzerinden.

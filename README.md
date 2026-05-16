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
> Render'da deploy edildikten sonra link buraya gelecek. Deploy adımları: [`docs/deploy-render.md`](docs/deploy-render.md). Render free tier'da 15 dakika inaktivite sonrası uyur; ilk istek 30-60 saniye sürebilir.

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

## Yol haritası / Roadmap

- [x] Repo scaffold, FastAPI iskelet, `/v1/factors`
- [ ] `parser/waste.py` — atık taşıma faturası (DEFRA referans)
- [ ] `parser/electricity.py` — EPDK formatlı elektrik faturası
- [ ] `parser/water.py` — İSKİ/İZSU/ASKİ örnekleri
- [ ] `parser/logistics.py` — akaryakıt + km bazlı
- [ ] `core/verifier.py` — Scope 1/2/3 hesap motoru
- [ ] `core/bddk_mapper.py` — YVO Ek-1 → bundle
- [ ] `core/xbrl.py` — EFRAG VSME XBRL-JSON çıktı
- [ ] `core/signing.py` — Ed25519 imza
- [ ] Render canlı demo
- [ ] Hugging Face Spaces (ek görünürlük)

İlerleyiş [GitHub Project board](https://github.com/memirutku/rebot-api/projects) üzerinden takip edilebilir.

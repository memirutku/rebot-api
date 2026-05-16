# REBOT ENERGY — Proje genel görünüm

> Bu doküman projenin **niçin/ne**'siyle ilgilenir. API'nin **nasıl kullanılacağı** için [README](README.md) ve canlı [Swagger UI](https://rebot-api.onrender.com/docs).

---

## 🇹🇷 Türkçe

### Problem

BDDK'nın **Nisan 2025**'te yayımladığı **Yeşil Varlık Oranı (YVO) Tebliği**, bankaların yeşil kredi portföylerini bağımsız doğrulanmış çevresel veriyle tevsik etmesini zorunlu kıldı. Raporlama **Haziran 2025**'ten itibaren mecburi.

Ne var ki KOBİler bu veriyi üretemiyor:

- Atık ve karbon verisi ya hiç ölçülmüyor ya firmanın kendi beyanına dayanıyor
- Banka denetleyemiyor → **greenwashing** riski yüksek
- BDDK Ek-1 ekleri PDF formatında, **makine-okunabilir açık veri standardı yok**

### Çözüm

REBOT API üç katmanlı bir köprü kurar:

1. **Giriş** — KOBİ veya muhasebecisi fatura JSON'unu gönderir
2. **Doğrulama** — GHG Protocol Scope 1/2/3 hesabı + BDDK YVO Ek-1 eşlemesi
3. **Çıkış** — Bankaya **Ed25519 imzalı**, denetlenebilir bundle

```
KOBİ → POST /v1/ingest → [doğrulama] → GET /v1/esg/{tax_id} → Banka
                                              ↓
                                     Ed25519 imzalı bundle
                                     (banka offline doğrular)
```

### Açık çekirdek modeli

| Açık (bu repo, Apache 2.0 + CC BY-SA 4.0) | Kapalı (ticari premium) |
|---|---|
| API motoru, parser'lar, GHG hesabı, YVO mapper | Banka konektörleri (KEP, e-arşiv) |
| Veri şemaları, emisyon faktör kataloğu | Multi-tenant SaaS + faturalama |
| Ed25519 imzalama, JSON Schema sözleşmesi | Audit dashboard / regulator portal |
| Görsel demo (Gradio), landing page | KOBİ onboarding UI, alarm motoru |

**Strateji:** Banka REBOT'a değil, REBOT'un imzasına güvenir. Motor topluluğa açık → standart benimsenir → premium katman ölçeklenir.

### Neden açık çekirdek?

Türkiye'de BDDK YVO için makine-okunabilir açık veri standardı yok. Global emsaller:

- [fingreen-ai/greenlang](https://github.com/fingreen-ai/greenlang) — global ESG metodolojisi (BSD-3 + CC BY-SA 4.0)
- [EFRAG VSME XBRL Taxonomy](https://www.efrag.org/en/vsme-digital-template-and-xbrl-taxonomy) — AB SME makine-okunabilir standardı (MIT)
- [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) — Apache 2.0

REBOT bu boşluğun Türkiye-yerli muadili olabilir.

### Yol haritası

**Tamamlandı**
- Repo + FastAPI iskelet + `/v1/factors` (DEFRA + TEİAŞ)
- Canlı API (Render free tier) + Swagger UI
- `POST /v1/ingest` atık dikey (JSON) + dedupe
- `core/verifier.py` — GHG Protocol Scope 3.5
- `core/bddk_mapper.py` — YVO Ek-1 Hedef 4 (döngüsel ekonomi)
- `GET /v1/esg/{tax_id}` — dönemsel imzalı bundle
- `core/signing.py` — Ed25519 detached signature + public key endpoint
- Gradio görsel demo (`demo/app.py`)
- Branded landing (memirutku.github.io/rebot-api) + TR/EN toggle

**Sırada (dikey)**
- `parser/electricity.py` — EPDK formatlı fatura → Scope 2
- `parser/water.py` — İSKİ/İZSU/ASKİ → Scope 3.4
- `parser/logistics.py` — akaryakıt + km → Scope 1
- BDDK YVO Ek-1 Hedef 1 (climate mitigation), 5 (pollution)
- `core/xbrl.py` — EFRAG VSME XBRL-JSON çıktı (AB interop)

**Sırada (veri)**
- EWC kataloğu (840 kod) — bkz. [DATA-ROADMAP.md](DATA-ROADMAP.md)
- Anonim gerçek atık taşıma faturaları (PDF parser için)
- Postgres storage + KOBİ bazlı veri persistance
- HF Spaces deploy + branded domain

**Sırada (regülasyon takibi)**
- BDDK YVO Tebliği güncellemeleri
- CBAM 2026 ihracat raporlama uyumu
- Türkiye İklim Kanunu (Temmuz 2025) bağlantıları

İlerleyiş: [GitHub Issues](https://github.com/memirutku/rebot-api/issues) ve [Discussions](https://github.com/memirutku/rebot-api/discussions)

---

## 🇬🇧 English

### Problem

In **April 2025**, Turkey's banking regulator (BDDK) issued the **Green Asset Ratio (YVO) Regulation**, requiring banks to back green loan portfolios with independently verified environmental data. Mandatory reporting begins **June 2025**.

SMEs cannot produce this data:

- Waste and carbon data is either unmeasured or self-reported
- Banks cannot verify → high **greenwashing** risk
- The BDDK YVO annexes are PDF-only; **no machine-readable open data standard** exists

### Solution

REBOT API is a three-layer bridge:

1. **Ingest** — SME or its accountant submits an invoice JSON
2. **Verify** — GHG Protocol Scope 1/2/3 accounting + BDDK YVO Annex 1 mapping
3. **Emit** — Bank receives an **Ed25519-signed**, auditable bundle

The bank trusts the **signature**, not the operator.

### Open-core model

| Open (this repo, Apache 2.0 + CC BY-SA 4.0) | Closed (commercial) |
|---|---|
| API engine, parsers, GHG accounting, YVO mapper | Bank connectors (KEP, e-archive) |
| Data schemas, emission-factor catalogue | Multi-tenant SaaS + billing |
| Ed25519 signing, JSON Schema contract | Audit dashboard / regulator portal |
| Visual demo (Gradio), landing page | SME onboarding UI, alert engine |

### Inspirations

- [fingreen-ai/greenlang](https://github.com/fingreen-ai/greenlang) — open ESG methodology (BSD-3 + CC BY-SA 4.0)
- [EFRAG VSME XBRL Taxonomy](https://www.efrag.org/en/vsme-digital-template-and-xbrl-taxonomy) — EU SME machine-readable standard (MIT)
- [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) — Apache 2.0

### Roadmap

**Done**
- Repo + FastAPI skeleton + `/v1/factors` (DEFRA + TEİAŞ)
- Live API (Render free tier) + Swagger UI
- `POST /v1/ingest` waste vertical (JSON) + dedupe
- `core/verifier.py` — GHG Protocol Scope 3.5
- `core/bddk_mapper.py` — YVO Annex 1 Objective 4 (circular economy)
- `GET /v1/esg/{tax_id}` — period-scoped signed bundle
- `core/signing.py` — Ed25519 detached signature + public-key endpoint
- Gradio visual demo (`demo/app.py`)
- Branded landing page with TR/EN toggle

**Next**
- Verticals: electricity / water / logistics parsers
- YVO objectives: 1 (mitigation), 5 (pollution)
- EFRAG VSME XBRL-JSON output
- Data enrichment — see [DATA-ROADMAP.md](DATA-ROADMAP.md)
- Postgres storage; HF Spaces deploy

Track progress via [GitHub Issues](https://github.com/memirutku/rebot-api/issues) / [Discussions](https://github.com/memirutku/rebot-api/discussions).

---

## Lisans / License

- **Kod / Code**: [Apache 2.0](LICENSE)
- **Veri ve şemalar / Data & schemas**: [CC BY-SA 4.0](DATA-LICENSE)

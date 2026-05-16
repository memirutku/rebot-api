# Veri Yol Haritası / Data Roadmap

> Bu doküman REBOT API'nin **veri tarafının** mevcut durumunu ve eksiklerini şeffafça listeler. API motoru hazır ama altındaki veri henüz inceyi. Yatırımcı/banka/regülatör görüşmesinde dürüstçe söylenmesi gereken durumdur.
>
> _This document tracks the **data side** of REBOT API: what's real, what's still a stub, and what comes next. Transparent inventory for investor / bank / regulator conversations._

---

## Şu anda neyimiz var? / What's real today?

### ✅ Üretime-hazır

| Veri | Sayım | Kaynak | Konum |
|---|---|---|---|
| **DEFRA 2024 emisyon faktörleri** | 8 faktör | UK DESNZ açık veri | `data/emission_factors/defra_2024.json` |
| **TEİAŞ 2023 elektrik şebeke faktörü** | 2 faktör | TEİAŞ kamuya açık istatistik | `data/emission_factors/tuik_electricity_tr_2023.json` |
| **EWC kataloğu (TR pratik altküme)** | 85 kod, 11 chapter | AB Karar 2014/955/EU + T.C. Atık Yön. Yön. Ek-IV | `data/waste_codes/ewc_tr.json` |
| **BDDK YVO Hedef 4 kuralları** | 1/6 hedef | BDDK YVO Tebliği (11.04.2025) Ek-1 yorumu | `api/core/bddk_mapper.py` |

### ⚠️ Test/demo kalitesinde (uydurma)

| Veri | Konum | Sorun |
|---|---|---|
| Örnek atık faturaları | `examples/requests/`, `demo/sample_invoices/` | "ACME", "Demo KOBİ" gibi uydurma adlar. Gerçek bir atık taşıma firmasının fatura yapısını birebir taklit etmiyor. |
| KOBİ kayıtları | `api/storage.py` (in-memory) | Render restart'ta sıfırlanır. Hiçbir gerçek KOBİ verisi yok. |

### ❌ Henüz hiç yok

- ✗ Tam EWC kataloğu (~840 kod, 20 chapter)
- ✗ BDDK YVO Ek-1 Hedef 1, 2, 3, 5, 6 (5 hedefin makine-okunabilir kuralı)
- ✗ Anonimleştirilmiş gerçek atık taşıma faturası örnekleri (PDF parser için)
- ✗ EPDK fatura şablonları (elektrik dikey için)
- ✗ İSKİ/İZSU/ASKİ fatura şablonları (su dikey için)
- ✗ YEK-G yenilenebilir elektrik sertifika doğrulama
- ✗ Atık taşıma firması veritabanı (kimler lisanslı, neyi taşıyor)
- ✗ Postgres/SQLite kalıcı storage
- ✗ Gerçek bir KOBİ pilot kullanıcı

---

## Yol haritası / Roadmap

### Sprint A — EWC tamamlama (kısa vadeli)
- [ ] Tam 840-kod EWC listesini AB karar metninden çıkar (CSV → JSON)
- [ ] Türkçe açıklamalar: T.C. Atık Yönetimi Yönetmeliği Ek-IV ile eşle
- [ ] Test: her chapter için en az 1 kod çağrısı
- [ ] `/v1/waste-codes?chapter=01..20` tüm chapter'lar dönmeli
- **Tahmini efor**: 1-2 gün (otomatik parse + manuel doğrulama)
- **Kaynaklar**: [EUR-Lex 32014D0955](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014D0955), [Resmi Gazete 29314](https://www.resmigazete.gov.tr/eskiler/2015/04/20150402-3.htm)

### Sprint B — BDDK YVO Ek-1 tam taksonomi
- [ ] Hedef 1 (climate mitigation): NACE kodu × eşik tabanlı kurallar
- [ ] Hedef 2 (climate adaptation): adaptasyon yatırımı testi
- [ ] Hedef 3 (sustainable water): su kaynağı koruma kriterleri
- [ ] Hedef 5 (pollution prevention): kirlilik önleme metrikleri
- [ ] Hedef 6 (biodiversity): ekosistem etki değerlendirme
- [ ] Her hedef için `objectives.json` makine-okunabilir taksonomi
- [ ] `bddk_mapper.py` her hedef için ayrı mapper fonksiyon
- **Tahmini efor**: 3-5 gün (regülasyon yorumu + implementasyon)
- **Bağımlılık**: BDDK PDF Ek-1 detaylı okuma; muhtemelen avukat danışmanlığı

### Sprint C — Gerçek fatura örnekleri (kritik)
- [ ] 2-3 atık taşıma firmasıyla anlaş — anonimleştirilmiş PDF örneği iste
- [ ] EPDK lisanslı elektrik dağıtım şirketlerinden örnek fatura
- [ ] İSKİ/İZSU/ASKİ örnekleri
- [ ] Akaryakıt fişi varyasyonları (Shell, BP, OPET)
- [ ] Her dosya `examples/real-samples/{vendor}/{anonymized}.pdf`
- **Tahmini efor**: 1-2 hafta (anlaşma süreci + anonimleştirme)
- **Bu olmadan**: PDF parser yazılamaz, sadece JSON ingest çalışır
- **Hukuki not**: Anonimleştirme KVKK uyumlu yapılmalı; firma onayı yazılı alınmalı

### Sprint D — Üretim storage + pilot KOBİ
- [ ] PostgreSQL backed `IngestStore` (mevcut interface'i koru)
- [ ] Alembic migration
- [ ] `REBOT_DATABASE_URL` env var, geri dönüşlü in-memory mod
- [ ] 1 gerçek KOBİ pilot (REBOT ENERGY kendi şirketi olabilir)
- [ ] Aylık fatura ingest test akışı
- **Tahmini efor**: 3-5 gün (storage) + sürekli pilot
- **Bağımlılık**: Render Postgres add-on ($7/ay) veya Supabase free tier

### Sprint E — YEK-G ve regülatör API'leri
- [ ] EPDK YEK-G doğrulama (var mı public API?)
- [ ] EÇBS scrape (KOBİ vekaleti ile) — Faz 2, KVKK ağır
- [ ] BDDK e-arşiv entegrasyonu
- **Tahmini efor**: bilinmiyor — regülatör erişimine bağlı
- **Risk**: Yapısal blocker; ya regülatör destek olmazsa pilot programa katılım gerekebilir

---

## Şu anki "demo dürüst" söylemi

Yatırımcı/banka görüşmesinde söylenecek dürüst cümle:

> "REBOT'un motoru çalışıyor — atık faturasından imzalı YVO bundle'a kadar uçtan uca akış var. Şu an altında 10 emisyon faktörü ve 85 EWC kodu var; mimari, daha fazlasına genişletmek için hazır. Gerçek pilotlar için Sprint C ve D'ye geçmemiz lazım — bu da regülatör/banka/atık taşıma firmasıyla anlaşma demek."

**API hazır, veri ince. İkisi farklı işler.** Bu farkındalıkla yola çıkmak yatırımcı güvenini sarsmaz, aksine artırır.

---

## İlerleyiş takibi / Tracking

- GitHub Issues: [data-roadmap label](https://github.com/memirutku/rebot-api/issues?q=label%3Adata-roadmap)
- Yapılan veri eklemeleri commit mesajlarında `data:` prefix'i ile

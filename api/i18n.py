"""English → Turkish lookup for OpenAPI spec field translation.

Used by api.main._translate_spec to produce /openapi.tr.json from the
English source spec. Keys are the exact strings that appear in the
generated spec (path operation summary/description, Pydantic Field
description/title, Query parameter description, tag description).

When adding a new endpoint or model, run
    python -c "from api.main import app; ..."
to dump untranslated strings and add the missing entries here.
"""

EN_TO_TR: dict[str, str] = {
    # ── Top-level info / tags ─────────────────────────────────────────
    # (title kept as 'REBOT API' in both)
    # description and tag descriptions overridden in api/main.py via META_TR
    # ── Path operation summaries ──────────────────────────────────────
    "Service banner": "Servis bilgisi",
    "Liveness probe": "Sağlık kontrolü",
    "Ingest a structured invoice payload": "Yapılandırılmış fatura kaydı al",
    "Retrieve a previously ingested record": "Önceden alınmış kaydı getir",
    "BDDK YVO bundle (Ed25519 signed) for an SME's reporting period": (
        "KOBİ raporlama dönemi için BDDK YVO bundle (Ed25519 imzalı)"
    ),
    "Get the Ed25519 verify key used to sign ESG bundles": (
        "ESG bundle'ları imzalamakta kullanılan Ed25519 doğrulama anahtarı"
    ),
    "List emission factor datasets": "Emisyon faktör veri kümelerini listele",
    "Get a single emission factor by id": "Belirli bir faktörü ID ile sorgula",
    "List EWC waste codes (Turkish + English)": (
        "EWC atık kodlarını listele (Türkçe + İngilizce)"
    ),
    "Look up a single EWC code": "Tek bir EWC kodu sorgula",

    # ── Path operation descriptions (long) ────────────────────────────
    "Accepts a structured JSON invoice (currently `invoice_type=waste`). "
    "Returns a normalized record with a stable `ingest_id` derived from the "
    "SHA-256 of the canonical payload — re-posting the same invoice yields "
    "the same id and is flagged as `duplicate=true`.": (
        "Yapılandırılmış JSON fatura kaydı kabul eder (şu an `invoice_type=waste`). "
        "Kanonik payload'ın SHA-256'sından türetilen kararlı bir `ingest_id` ile "
        "normalize edilmiş kayıt döner — aynı faturayı tekrar göndermek aynı id'yi "
        "verir ve `duplicate=true` olarak işaretlenir."
    ),
    "Aggregates all previously ingested waste invoices for the given Turkish tax "
    "id and returns a BDDK YVO Ek-1 aligned ESG bundle (currently Objective 4 — "
    "Transition to circular economy). The response includes a detached Ed25519 "
    "signature over the canonical JSON of `bundle`. Verify with the public key "
    "from `/v1/signing/pubkey`. Period accepts year-only ('2025') or "
    "year-quarter ('2025-Q2'). Returns 404 if no records exist for the tax id.": (
        "Verilen Türk vergi kimliği için daha önce alınmış tüm atık faturalarını "
        "toplar ve BDDK YVO Ek-1 ile uyumlu ESG bundle döner (şu an Hedef 4 — "
        "Döngüsel ekonomiye geçiş). Yanıt, `bundle` alanının kanonik JSON'ı "
        "üzerinde ayrılmış (detached) Ed25519 imzasını içerir. `/v1/signing/pubkey` "
        "ile dönen public key ile doğrulayın. Dönem 'YYYY' veya 'YYYY-Q[1-4]' "
        "biçiminde kabul edilir. Vergi kimliği için kayıt yoksa 404 döner."
    ),
    "Returns the public key in base64 along with a SHA-256 fingerprint. "
    "Use this to verify the signature attached to /v1/esg/{tax_id} responses. "
    "The signature covers the canonical JSON of the `bundle` field "
    "(sorted keys, compact, UTF-8).": (
        "Public anahtarı base64 ve SHA-256 parmak izi ile birlikte döner. "
        "/v1/esg/{tax_id} yanıtındaki imzayı doğrulamak için kullanın. "
        "İmza `bundle` alanının kanonik JSON'unu kapsar "
        "(sıralı anahtarlar, kompakt, UTF-8)."
    ),
    "European Waste Catalogue (EU 2014/955) Turkish-language subset focused on "
    "SME-relevant chapters (15 packaging, 17 C&D, 20 municipal, etc.). "
    "Returns the chapter index along with codes; supports filtering by chapter, "
    "hazardous flag, and free-text search across descriptions.": (
        "Avrupa Atık Kataloğu (EU 2014/955) Türkçe altküme — KOBİ alakalı bölümler "
        "(15 ambalaj, 17 inşaat & yıkım, 20 belediye atıkları vb.). Kodlarla "
        "birlikte bölüm dizini döner; bölüm, tehlikelilik bayrağı ve serbest "
        "metin arama ile filtreleme destekler."
    ),
    "Accepts the spaced form '20 03 01' or the compact form '200301'.": (
        "Boşluklu '20 03 01' veya kompakt '200301' biçimini kabul eder."
    ),

    # ── Pydantic Field descriptions ───────────────────────────────────
    "European Waste Catalogue code, e.g. '20 03 01' or '200301'": (
        "Avrupa Atık Kataloğu kodu, örn. '20 03 01' veya '200301'"
    ),
    "Turkish tax id (10-digit VKN or 11-digit TC kimlik)": (
        "Türk vergi kimliği (10 haneli VKN veya 11 haneli TC kimlik no)"
    ),
    "Disposal (D) or Recovery (R) operation code per EU Waste Framework Directive": (
        "AB Atık Çerçeve Direktifi'ne göre bertaraf (D) veya geri kazanım (R) kodu"
    ),
    "Quantity in the unit specified": "Belirtilen birimdeki miktar",
    "Ulusal Atık Taşıma Formu (UATF) reference, if available": (
        "Varsa Ulusal Atık Taşıma Formu (UATF) referansı"
    ),
    "Waste carrier (issuer of invoice)": "Atık taşıyıcısı (fatura kesen)",
    "SME receiving the service (ESG subject)": "Hizmeti alan KOBİ (ESG öznesi)",
    "A single waste-transport invoice from a licensed carrier to an SME.": (
        "Lisanslı bir atık taşıyıcısından KOBİ'ye kesilmiş tek bir atık taşıma faturası."
    ),
    "kgCO₂e per tonne": "ton başına kgCO₂e",
    "1.0 for structured JSON; <1.0 for PDF/OCR-derived data": (
        "Yapılandırılmış JSON için 1.0; PDF/OCR'den üretilen veriler için <1.0"
    ),
    "True if a payload with the same content hash was previously ingested": (
        "Aynı içerik hash'ine sahip kayıt daha önce alınmışsa True"
    ),
    "SHA-256 of the canonical input payload": "Kanonik giriş kaydının SHA-256'sı",
    "Scope 3.5 emissions; populated by verifier at ingest time.": (
        "Scope 3.5 emisyonları; kayıt anında doğrulayıcı tarafından doldurulur."
    ),
    "Tonnage-weighted alignment in [0, 1]": "Tonaj-ağırlıklı uyum oranı [0, 1]",
    "List of ingest_id references that fed this calculation": (
        "Bu hesaba katkı veren ingest_id referansları"
    ),
    "Single BDDK YVO Ek-1 objective alignment result.": (
        "Tek bir BDDK YVO Ek-1 hedef uyum sonucu."
    ),
    "Public data contract — bank-facing ESG bundle for a single SME period.": (
        "Açık veri sözleşmesi — tek bir KOBİ döneminin banka tarafına dönecek ESG bundle'ı."
    ),
    "ISO-ish period label, e.g. '2025-Q2' or '2025'": (
        "ISO-benzeri dönem etiketi, örn. '2025-Q2' veya '2025'"
    ),
    "SHA-256 of the raw 32-byte verify key (hex)": (
        "Ham 32-byte doğrulama anahtarının SHA-256'sı (hex)"
    ),
    "Detached Ed25519 signature, base64 standard": (
        "Ayrılmış (detached) Ed25519 imzası, standart base64"
    ),
    "Bundle + detached Ed25519 signature. The signature covers a canonical\n"
    "JSON serialization of the ``bundle`` field only.": (
        "Bundle + ayrılmış Ed25519 imzası. İmza yalnızca `bundle` alanının "
        "kanonik JSON serileştirmesini kapsar."
    ),

    # ── Query parameter descriptions ──────────────────────────────────
    "Filter by GHG Protocol scope: '1', '2', or '3' (substring match)": (
        "GHG Protocol kapsamına göre filtrele: '1', '2' veya '3' (alt-dize eşleşmesi)"
    ),
    "ISO 3166-1 alpha-2 region filter (e.g. 'TR')": (
        "ISO 3166-1 alpha-2 bölge filtresi (örn. 'TR')"
    ),
    "Reporting period: 'YYYY' or 'YYYY-Q[1-4]'": (
        "Raporlama dönemi: 'YYYY' veya 'YYYY-Q[1-4]'"
    ),
    "2-digit chapter prefix (e.g. '15', '17', '20')": (
        "2 haneli bölüm ön-eki (örn. '15', '17', '20')"
    ),
    "Filter by hazardous flag (true = '*' codes in EU EWC)": (
        "Tehlikelilik bayrağına göre filtrele (true = AB EWC'de '*' kodları)"
    ),
    "Case-insensitive substring search across Turkish + English descriptions": (
        "Türkçe + İngilizce açıklamalarda büyük-küçük harf duyarsız alt-dize araması"
    ),

    # ── Field titles (Pydantic auto-generated from attribute names) ──
    # FastAPI converts attribute_name → "Attribute Name" for the OpenAPI title.
    # These show up in Swagger UI as labels next to inputs.
    "Tax Id": "Vergi No",
    "Customer Tax Id": "Müşteri Vergi No",
    "Issuer Tax Id": "Düzenleyen Vergi No",
    "Customer Name": "Müşteri Adı",
    "Issuer Name": "Düzenleyen Adı",
    "Invoice Type": "Fatura Tipi",
    "Invoice Number": "Fatura Numarası",
    "Invoice Date": "Fatura Tarihi",
    "Total Amount Try": "Toplam Tutar (TL)",
    "Lines": "Satırlar",
    "Ewc Code": "EWC Kodu",
    "Description": "Açıklama",
    "Quantity": "Miktar",
    "Unit": "Birim",
    "Disposal Method": "Bertaraf Yöntemi",
    "Uatf Number": "UATF Numarası",
    "Ewc Codes": "EWC Kodları",
    "Disposal Methods": "Bertaraf Yöntemleri",
    "Quantity Tonnes": "Miktar (ton)",
    "Factor Id": "Faktör ID",
    "Factor Value": "Faktör Değeri",
    "Factor Dataset": "Faktör Veri Kümesi",
    "Co2E Kg": "CO₂e (kg)",
    "Total Co2E Kg": "Toplam CO₂e (kg)",
    "Scope 3 5 Co2E Kg": "Scope 3.5 CO₂e (kg)",
    "Ghg Scope": "GHG Kapsamı",
    "Line Count": "Satır Sayısı",
    "Line Index": "Satır Endeksi",
    "Line Emissions": "Satır Emisyonları",
    "Total Quantity Kg": "Toplam Miktar (kg)",
    "Total Tonnes": "Toplam Ton",
    "Aligned Tonnes": "Uyumlu Ton",
    "Aligned Ratio": "Uyum Oranı",
    "Total Waste Tonnes": "Toplam Atık (ton)",
    "Invoice Count": "Fatura Sayısı",
    "Period": "Dönem",
    "Period Year": "Dönem Yılı",
    "Period Quarter": "Dönem Çeyreği",
    "Region": "Bölge",
    "Scope": "Kapsam",
    "Chapter": "Bölüm",
    "Hazardous": "Tehlikeli",
    "Notes": "Notlar",
    "Warnings": "Uyarılar",
    "Methodology": "Yöntem",
    "Objectives": "Hedefler",
    "Objective Id": "Hedef ID",
    "Objective Name Tr": "Hedef Adı (TR)",
    "Objective Name En": "Hedef Adı (EN)",
    "Evidence": "Kanıtlar",
    "Ingest Id": "Kayıt ID",
    "Content Hash": "İçerik Hash'i",
    "Parser Confidence": "Ayrıştırıcı Güveni",
    "Duplicate": "Tekrar",
    "Received At": "Alındığı Zaman",
    "Schema Version": "Şema Sürümü",
    "Algorithm": "Algoritma",
    "Key Id": "Anahtar ID",
    "Key Fingerprint Sha256": "Anahtar Parmak İzi (SHA-256)",
    "Value B64": "Değer (Base64)",
    "Signed At": "İmzalandığı Zaman",
    "Payload Canonicalization": "Kayıt Kanonikleştirme",
    "Detail": "Detay",
    "Message": "Mesaj",
    "Error Type": "Hata Tipi",
    "Context": "Bağlam",
    "Location": "Konum",
    "Input": "Girdi",
    "Limit": "Limit",
    "Code": "Kod",
    "Successful Response": "Başarılı Yanıt",
    "Validation Error": "Doğrulama Hatası",
}


def translate(text: str) -> str:
    """Return Turkish translation if known, else the original text."""
    return EN_TO_TR.get(text, text)

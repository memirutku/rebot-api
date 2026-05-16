"""Gradio demo for REBOT API — Hugging Face Spaces compatible.

This app is a thin client over the public REBOT API (no business logic here).
It lets non-developer audiences submit a waste-transport invoice and see the
resulting BDDK YVO bundle, signed and verifiable.

Run locally:
    python demo/app.py

Deploy: see docs/deploy-hf-spaces.md
"""

from __future__ import annotations

import base64
import json
import os
from datetime import date
from pathlib import Path

import gradio as gr
import requests
from nacl.signing import VerifyKey

API_URL = os.environ.get("REBOT_API_URL", "https://rebot-api.onrender.com")
SAMPLES_DIR = Path(__file__).parent / "sample_invoices"


def _load_samples() -> dict[str, str]:
    samples = {}
    for path in sorted(SAMPLES_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            samples[path.stem] = f.read()
    return samples


SAMPLES = _load_samples()


def _quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def _verify_signature(bundle: dict, sig_b64: str, vk_b64: str) -> tuple[bool, str]:
    try:
        vk = VerifyKey(base64.b64decode(vk_b64))
        canonical = json.dumps(
            bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        vk.verify(canonical, base64.b64decode(sig_b64))
        return True, "✅ İmza geçerli — bundle değiştirilmemiş"
    except Exception as exc:  # noqa: BLE001
        return False, f"❌ İmza doğrulanamadı: {exc}"


def process(invoice_json: str) -> tuple[str, str, str, str, str]:
    """Send invoice to live API, retrieve signed ESG bundle, verify locally."""
    try:
        payload = json.loads(invoice_json)
    except json.JSONDecodeError as e:
        return f"❌ Geçersiz JSON: {e}", "", "", "", ""

    # 1. Ingest
    try:
        r = requests.post(f"{API_URL}/v1/ingest", json=payload, timeout=90)
    except requests.RequestException as e:
        return f"❌ API erişilemedi: {e}", "", "", "", ""

    if r.status_code != 201:
        return f"❌ Ingest reddedildi (HTTP {r.status_code}): {r.text}", "", "", "", ""

    ingest_resp = r.json()
    em = ingest_resp["normalized"]["emissions"]
    ingest_summary = (
        f"**Ingest ID:** `{ingest_resp['ingest_id']}`  \n"
        f"**Parser confidence:** {ingest_resp['parser_confidence']}  \n"
        f"**Dedupe (duplicate):** {ingest_resp['duplicate']}  \n"
        f"**Toplam atık:** {ingest_resp['normalized']['total_quantity_kg']} kg  \n"
        f"**GHG Protocol Scope:** {em['ghg_scope']}  \n"
        f"**Toplam CO₂e:** **{em['total_co2e_kg']} kg**"
    )

    # 2. ESG bundle
    inv_date = date.fromisoformat(payload["invoice_date"])
    period = f"{inv_date.year}-Q{_quarter(inv_date)}"
    tax_id = payload["customer_tax_id"]
    bundle_resp = requests.get(
        f"{API_URL}/v1/esg/{tax_id}?period={period}", timeout=60
    ).json()
    bundle = bundle_resp["bundle"]
    sig = bundle_resp["signature"]

    obj = bundle["objectives"][0]
    aligned_pct = float(obj["aligned_ratio"]) * 100
    bar = "█" * int(aligned_pct / 5) + "░" * (20 - int(aligned_pct / 5))

    if aligned_pct >= 80:
        badge = "🟢 GÜÇLÜ — yeşil kredi için elverişli"
    elif aligned_pct >= 40:
        badge = "🟡 ORTA — kısmi alignment, iyileştirme gerekli"
    else:
        badge = "🔴 ZAYIF — döngüsel ekonomiye geçiş kanıtı yetersiz"

    yvo_summary = (
        f"### {obj['objective_name_tr']} (BDDK YVO Hedef {obj['objective_id']})\n\n"
        f"**Aligned ratio:** `{obj['aligned_ratio']}` ({aligned_pct:.1f}%)  \n"
        f"`{bar}`  \n\n"
        f"**Durum:** {badge}\n\n"
        f"**Aligned tonaj:** {obj['aligned_tonnes']} / {obj['total_tonnes']} t  \n"
        f"**Dönem:** {bundle['period']}  &nbsp;&nbsp;**KOBİ TIN:** {bundle['tax_id']}  \n"
        f"**Methodology:** _{obj['methodology']}_"
    )

    # 3. Signature verify (locally, against /v1/signing/pubkey)
    pub = requests.get(f"{API_URL}/v1/signing/pubkey", timeout=30).json()
    ok, msg = _verify_signature(bundle, sig["value_b64"], pub["verify_key_b64"])
    sig_summary = (
        f"**Algoritma:** {sig['algorithm']}  \n"
        f"**Key fingerprint:** `{sig['key_fingerprint_sha256'][:24]}…`  \n"
        f"**Signed at:** {sig['signed_at']}  \n"
        f"**Doğrulama:** {msg}"
    )

    pretty_bundle = json.dumps(bundle_resp, indent=2, ensure_ascii=False)

    return ingest_summary, yvo_summary, sig_summary, pretty_bundle, ""


with gr.Blocks(title="REBOT API Demo — KOBİ ESG Doğrulama") as app:
    gr.Markdown(
        """
        # 🌱 REBOT API — KOBİ ESG Doğrulama Demosu

        KOBİ'nin atık taşıma faturasını gönderin → **BDDK YVO Tebliği** uyumlu,
        **GHG Protocol Scope 3.5** hesaplı, **Ed25519 imzalı** ESG bundle alın.
        Bu demo doğrudan canlı API'ye konuşur: `https://rebot-api.onrender.com`

        ⚠️ Render free tier — ilk istek 30-60 saniye sürebilir (cold start).
        """
    )

    with gr.Row():
        sample_choice = gr.Dropdown(
            choices=[
                "01_full_recycling — %100 geri dönüşüm (en iyi senaryo)",
                "02_mixed_disposal — yarısı geri dönüşüm, yarısı depolama",
                "03_landfill_only — tamamı depolama (en kötü senaryo)",
            ],
            label="Hazır örnek seç",
            value="01_full_recycling — %100 geri dönüşüm (en iyi senaryo)",
        )
        load_btn = gr.Button("📋 Örneği yükle", variant="secondary")

    invoice_input = gr.Code(
        value=SAMPLES["01_full_recycling"],
        language="json",
        label="Atık taşıma faturası (JSON)",
        lines=20,
    )

    submit_btn = gr.Button("🚀 Gönder → BDDK YVO bundle al", variant="primary")

    gr.Markdown("---")

    with gr.Row():
        with gr.Column():
            ingest_out = gr.Markdown(label="1. Ingest + Verifier")
        with gr.Column():
            yvo_out = gr.Markdown(label="2. BDDK YVO Alignment")
        with gr.Column():
            sig_out = gr.Markdown(label="3. İmza Doğrulama")

    gr.Markdown("### Ham bundle JSON (banka entegrasyonu için)")
    bundle_out = gr.Code(language="json", lines=30, interactive=False)
    err_out = gr.Markdown(visible=False)

    def _load_sample(choice: str) -> str:
        key = choice.split(" — ")[0]
        return SAMPLES.get(key, "")

    load_btn.click(_load_sample, inputs=sample_choice, outputs=invoice_input)
    submit_btn.click(
        process,
        inputs=invoice_input,
        outputs=[ingest_out, yvo_out, sig_out, bundle_out, err_out],
    )

    gr.Markdown(
        """
        ---
        **Proje:** [github.com/memirutku/rebot-api](https://github.com/memirutku/rebot-api)
        &nbsp;•&nbsp; **Lisans:** Apache 2.0 (kod) + CC BY-SA 4.0 (data)
        &nbsp;•&nbsp; **Swagger UI:** [/docs](https://rebot-api.onrender.com/docs)
        """
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Soft(primary_hue="green"),
    )

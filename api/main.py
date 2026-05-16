import copy
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from api import __version__
from api.i18n import translate as tr
from api.routers import emission_factors, esg, ewc_codes, invoices, signing

# Two-language metadata. The OpenAPI spec is generated once in Turkish (default
# user audience), then a translated copy is served at /openapi.en.json. Path
# operation summaries / parameter docs themselves remain English to keep the
# code readable for international contributors — only top-level title,
# description, and tag descriptions get swapped.

META_TR = {
    "title": "REBOT API",
    "description": (
        "KOBİ'ler için açık kaynak ESG doğrulama API'si. "
        "Atık, elektrik, su ve lojistik faturalarını **BDDK YVO** + **GHG Protocol** "
        "uyumlu, **Ed25519 imzalı** ESG bundle'larına dönüştürür. "
        "Apache 2.0 (kod) • CC BY-SA 4.0 (veri ve şemalar)."
    ),
    "tags": {
        "meta": "Sağlık ve sürüm",
        "invoices": "Fatura veri kabulü (normalize etme)",
        "esg": "KOBİ için BDDK YVO uyumlu ESG bundle",
        "signing": "İmzalı bundle'ları doğrulamak için public key",
        "emission-factors": "Açık emisyon faktör kataloğu (CC BY-SA 4.0)",
        "ewc-codes": "EWC (Avrupa Atık Kataloğu) Türkçe arama",
    },
}

META_EN = {
    "title": "REBOT API",
    "description": (
        "Open source ESG verification API for SMEs. "
        "Converts utility invoices (waste, electricity, water, logistics) into "
        "**BDDK YVO** + **GHG Protocol** compliant, **Ed25519 signed** ESG bundles. "
        "Apache 2.0 (code) • CC BY-SA 4.0 (data & schemas)."
    ),
    "tags": {
        "meta": "Health and version",
        "invoices": "Submit utility invoices for normalization",
        "esg": "BDDK YVO compliant ESG bundle for an SME",
        "signing": "Public key for verifying signed bundles",
        "emission-factors": "Open emission factor catalogue (CC BY-SA 4.0)",
        "ewc-codes": "EWC (European Waste Catalogue) Turkish lookup",
    },
}

app = FastAPI(
    title=META_TR["title"],
    description=META_TR["description"],
    version=__version__,
    contact={
        "name": "REBOT ENERGY",
        "url": "https://github.com/memirutku/rebot-api",
    },
    license_info={"name": "Apache 2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
    openapi_tags=[
        {"name": name, "description": desc} for name, desc in META_TR["tags"].items()
    ],
    # Custom UI served at /docs below; disable the built-in route to avoid duplication.
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(invoices.router, prefix="/v1")
app.include_router(esg.router, prefix="/v1")
app.include_router(signing.router, prefix="/v1")
app.include_router(emission_factors.router, prefix="/v1")
app.include_router(ewc_codes.router, prefix="/v1")


TRANSLATABLE_KEYS = {"summary", "description", "title"}


def _translate_in_place(node: object, lang: str) -> None:
    """Recursively walk an OpenAPI dict and translate description/summary/title
    string leaves. Only TR triggers translation; EN leaves the English text
    untouched (since the source spec is generated in English)."""
    if lang != "tr":
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k in TRANSLATABLE_KEYS and isinstance(v, str):
                node[k] = tr(v)
            else:
                _translate_in_place(v, lang)
    elif isinstance(node, list):
        for item in node:
            _translate_in_place(item, lang)


def _spec_in(lang: str) -> dict:
    """Return an OpenAPI dict translated to the requested language.

    Top-level info.title / info.description / tag descriptions are swapped via
    META_TR / META_EN; everything else (path summaries, parameter descriptions,
    schema field titles and descriptions) is translated via api.i18n.translate.
    """
    spec = copy.deepcopy(app.openapi())
    meta = META_EN if lang == "en" else META_TR
    spec["info"]["title"] = meta["title"]
    spec["info"]["description"] = meta["description"]
    for tag in spec.get("tags", []):
        new_desc = meta["tags"].get(tag["name"])
        if new_desc:
            tag["description"] = new_desc

    # Recursively translate everything else when serving the Turkish spec.
    if lang == "tr":
        for section in ("paths", "components"):
            if section in spec:
                _translate_in_place(spec[section], lang)

    return spec


@app.get("/openapi.json", include_in_schema=False)
def openapi_default():
    return JSONResponse(_spec_in("tr"))


@app.get("/openapi.tr.json", include_in_schema=False)
def openapi_tr():
    return JSONResponse(_spec_in("tr"))


@app.get("/openapi.en.json", include_in_schema=False)
def openapi_en():
    return JSONResponse(_spec_in("en"))


SWAGGER_HTML = """<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8" />
<title>REBOT API • {docs_label}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
<link rel="icon" type="image/svg+xml"
      href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2315803d'/%3E%3Cpath d='M44 14c-9 0-18 6-20 18-1 5-1 11 2 14 3 3 9 4 14 3 13-2 19-12 19-22 0-7-5-13-15-13z' fill='%23dcfce7'/%3E%3C/svg%3E" />
<style>
  body {{ margin: 0; }}
  .rebot-langbar {{
    position: fixed; top: 12px; right: 16px; z-index: 1000;
    display: inline-flex; background: #fff;
    border: 2px solid #15803d; border-radius: 999px;
    padding: 3px; box-shadow: 0 2px 6px rgba(21,128,61,0.18);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
  }}
  .rebot-langbar a {{
    text-decoration: none; color: #15803d;
    padding: 6px 14px; font-size: 13px; font-weight: 700;
    border-radius: 999px; display: inline-flex; align-items: center; gap: 6px;
  }}
  .rebot-langbar a.active {{ background: #15803d; color: #fff; }}
  .rebot-langbar a:not(.active):hover {{ background: #dcfce7; }}
  .rebot-langbar img {{ width: 18px; height: 12px; border-radius: 2px; }}
  @media (max-width: 720px) {{
    .rebot-langbar {{ top: 8px; right: 8px; padding: 2px; }}
    .rebot-langbar a {{ padding: 4px 10px; font-size: 12px; }}
  }}
</style>
</head>
<body>
<nav class="rebot-langbar" aria-label="Language">
  <a href="/docs?lang=tr" class="{tr_class}" hreflang="tr">
    <img src="https://memirutku.github.io/rebot-api/flag-tr.svg" alt="" aria-hidden="true">TR
  </a>
  <a href="/docs?lang=en" class="{en_class}" hreflang="en">
    <img src="https://memirutku.github.io/rebot-api/flag-gb.svg" alt="" aria-hidden="true">EN
  </a>
</nav>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
<script>
window.onload = () => {{
  window.ui = SwaggerUIBundle({{
    url: {spec_url_json},
    dom_id: "#swagger-ui",
    deepLinking: true,
    docExpansion: "list",
    defaultModelsExpandDepth: -1,
    displayRequestDuration: true,
    presets: [SwaggerUIBundle.presets.apis],
    layout: "BaseLayout",
  }});
}};
</script>
</body>
</html>
"""


@app.get("/docs", include_in_schema=False)
def swagger_docs(lang: str = "tr"):
    if lang not in ("tr", "en"):
        lang = "tr"
    spec_url = "/openapi.tr.json" if lang == "tr" else "/openapi.en.json"
    html = SWAGGER_HTML.format(
        html_lang=lang,
        docs_label="API Dokümantasyonu" if lang == "tr" else "API documentation",
        tr_class="active" if lang == "tr" else "",
        en_class="active" if lang == "en" else "",
        spec_url_json=json.dumps(spec_url),
    )
    return HTMLResponse(html)


@app.get("/", tags=["meta"], summary="Service banner")
def root() -> dict:
    return {
        "service": "rebot-api",
        "version": __version__,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "repository": "https://github.com/memirutku/rebot-api",
    }


@app.get("/health", tags=["meta"], summary="Liveness probe")
def health() -> dict:
    return {"status": "ok"}

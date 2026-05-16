from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import __version__
from api.routers import esg, factors, ingest, signing

app = FastAPI(
    title="REBOT API",
    description=(
        "Open source ESG verification API for SMEs. "
        "Converts utility invoices (waste, electricity, water, logistics) into "
        "BDDK YVO + GHG Protocol compliant, signed ESG bundles. "
        "Apache 2.0 (code) • CC BY-SA 4.0 (data & schemas)."
    ),
    version=__version__,
    contact={
        "name": "REBOT ENERGY",
        "url": "https://github.com/memirutku/rebot-api",
    },
    license_info={"name": "Apache 2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
    openapi_tags=[
        {"name": "meta", "description": "Health and version"},
        {"name": "ingest", "description": "Submit utility invoices for normalization"},
        {"name": "esg", "description": "BDDK YVO compliant ESG bundle for an SME"},
        {"name": "signing", "description": "Public key for verifying signed bundles"},
        {"name": "factors", "description": "Open emission factor catalogue (CC BY-SA 4.0)"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/v1")
app.include_router(esg.router, prefix="/v1")
app.include_router(signing.router, prefix="/v1")
app.include_router(factors.router, prefix="/v1")


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

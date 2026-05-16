# Render'a ücretsiz deploy

> 5 dakikalık adım adım rehber. Render'ın ücretsiz web service'i Docker bilgisi gerektirmez ve bu repodaki `render.yaml` ile otomatik kurulur.

## 1. Hesap aç

1. https://render.com adresine git
2. Sağ üstte **Get Started for Free** veya **Sign Up**
3. **Sign up with GitHub** ile gir (en kolay; deploy için zaten GitHub bağlantısı gerekecek)
4. Email doğrulama linkini onayla
5. GitHub yetkilendirme penceresinde **Authorize Render** de — tek izin verdiğin şey repo'larını listelemek

> **Kredi kartı?** Web service için gerekmiyor. Add-on (örn. yönetilen Postgres) eklemek istersen kart sorabilir.

## 2. `rebot-api` servisini deploy et

`render.yaml` repo'da hazır olduğu için Render'ın "Blueprint" akışını kullanırız — tıkla, deploy et.

1. Render dashboard'da sol menü → **Blueprints** → **New Blueprint Instance**
2. **Connect a repository** → `memirutku/rebot-api` seç
3. Render `render.yaml`'ı otomatik okur:
   - Service name: `rebot-api`
   - Plan: **Free** (önceden ayarlı)
   - Runtime: Python 3.12
   - Build: `pip install -e .`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. **Apply** / **Create New Resources** butonuna bas
5. ~3-5 dakika içinde build biter; URL şuna benzer çıkar: `https://rebot-api.onrender.com` (alt çizgi yerine tire alabilir, sonuna rastgele suffix gelebilir)

## 3. Doğrula

URL'i tarayıcıda aç:
- `https://YOUR-URL.onrender.com/` → JSON service banner
- `https://YOUR-URL.onrender.com/docs` → Swagger UI
- `https://YOUR-URL.onrender.com/v1/factors` → emisyon faktör kataloğu
- `https://YOUR-URL.onrender.com/health` → `{"status":"ok"}`

## 4. README'i güncelle

Deploy URL'i geldikten sonra README'deki "Canlı demo" bloğunu güncelle:

```bash
# Repo'nun root'unda:
git pull
# README.md'de "## Canlı demo" altındaki placeholder'ı gerçek URL ile değiştir
git add README.md
git commit -m "docs: add live Render demo URL"
git push
```

## 5. Free tier'ın uyku davranışı

Render free web service **15 dakika inaktiviteden sonra uyur**. İlk istek 30-60 saniye sürebilir (uyandırma süresi).

**Uyandırma çözümleri:**
- **Ücretsiz**: https://cron-job.org → 10 dakikada bir `/health` endpoint'ine GET isteği planla
- **Ücretli**: Render'da $7/ay Starter plan → her zaman uyanık (production için önerilir)

## 6. Otomatik deploy

`render.yaml`'da `autoDeploy: true` olduğu için `main` branch'e her push otomatik deploy eder. PR merge → 5dk içinde canlı.

## Sorun giderme

| Hata | Çözüm |
|---|---|
| "Build failed: pip install -e ." | Python sürümü 3.12'den farklı olabilir. `render.yaml` içindeki `pythonVersion: "3.12"` kontrol et. |
| 502 Bad Gateway | Build başarılı ama uvicorn `$PORT` dinlemiyor olabilir. Loglarda `Uvicorn running on http://0.0.0.0:...` görmeli. |
| Uyandırma çok uzun sürüyor | Free tier kısıtı. Cron-ping kur veya Starter plana yükselt. |

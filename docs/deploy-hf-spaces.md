# Hugging Face Spaces'e Gradio demoyu deploy etme

> 5-10 dakikalık rehber. Render free tier'dan farklı olarak HF Spaces **uyumaz** — sürekli açık kalır. ESG/AI topluluğu için ek görünürlük sağlar.

## 1. Hugging Face hesabı aç

1. https://huggingface.co/join — GitHub veya Google ile giriş yapabilirsin
2. Email'i onayla

## 2. Yeni bir Space oluştur

1. Sağ üstte avatar → **+ New Space**
2. Şu değerleri gir:
   - **Owner**: kendi kullanıcı adın
   - **Space name**: `rebot-api-demo` (önerilir)
   - **License**: Apache 2.0
   - **Space SDK**: **Gradio**
   - **Hardware**: CPU basic — Free (yeterli, demo statik bir HTTP istemcisi)
   - **Visibility**: Public
3. **Create Space** → boş bir repo oluşur (örn. `https://huggingface.co/spaces/<USER>/rebot-api-demo`)

## 3. demo/ klasörünü Space'e push et

İki seçenek var. Daha pratiği `git` kullanmak.

### Seçenek A — git ile (önerilir)

```bash
# rebot-api kökünde değil, demo/ içine gir
cd demo

# Yeni bir git repo başlat (var olan ana repo'dan bağımsız)
git init
git remote add hf https://huggingface.co/spaces/<USER>/rebot-api-demo
git pull hf main  # HF'in oluşturduğu boş README'yi al

# Demo dosyalarını ekle
git add .
git commit -m "deploy: REBOT API gradio demo"
git push hf main
```

İlk push'ta HF kullanıcı adı + access token (huggingface.co/settings/tokens'tan al) ister.

### Seçenek B — HF web arayüzünden manuel upload

1. Space sayfasında **Files** sekmesi → **Add file** → **Upload files**
2. `demo/` içindeki tüm dosyaları sürükle-bırak: `app.py`, `requirements.txt`, `README.md`, `sample_invoices/`
3. Commit mesajı yaz → **Commit changes**

## 4. Build'i bekle

HF Spaces dosyalar yüklendikten sonra otomatik build başlatır (~2 dakika). Build durumunu Space sayfasının üstündeki **"Building"** / **"Running"** rozeti gösterir.

Hazır olunca demo şuradan erişilebilir:
```
https://huggingface.co/spaces/<USER>/rebot-api-demo
```

## 5. (Opsiyonel) Repo'dan link ver

`README.md`'nin "Canlı demo" bloğuna ekle:

```markdown
- 🟢 API: https://rebot-api.onrender.com
- 🎨 Görsel demo: https://huggingface.co/spaces/<USER>/rebot-api-demo
```

## Sorun giderme

| Hata | Çözüm |
|---|---|
| `requests.exceptions.ConnectionError` | API'nin Render'da uyandığından emin ol. `curl https://rebot-api.onrender.com/health` → 200 |
| "App is in error state" | Space "Logs" sekmesini aç. Genellikle `requirements.txt` eksik bir paketten kaynaklanır. |
| Gradio sürüm uyuşmazlığı | `demo/README.md`'deki `sdk_version: 4.44.0` HF'in desteklediği sürümlerden biri olmalı. Güncel listeyi HF docs'ta gör. |

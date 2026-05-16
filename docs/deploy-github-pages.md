# Landing page'i GitHub Pages'te yayınlama

Single-file static HTML; build adımı yok. Repo settings'ten Pages açmak yeterli.

## 1. Repo Settings → Pages

1. https://github.com/memirutku/rebot-api/settings/pages
2. **Source**: `Deploy from a branch`
3. **Branch**: `main`
4. **Folder**: `/site`
5. **Save**

GitHub ~30 saniye içinde build edip URL verir:
```
https://memirutku.github.io/rebot-api/
```

## 2. CLI alternatifi

```bash
gh api -X POST repos/memirutku/rebot-api/pages \
  -f "source[branch]=main" -f "source[path]=/site"
```

## 3. Repo homepage'i Pages URL'ine çevir (opsiyonel)

Render API URL'i yerine landing page'i pin'leyebilirsin:

```bash
gh repo edit memirutku/rebot-api \
  --homepage "https://memirutku.github.io/rebot-api/"
```

## 4. Özel alan adı (rebot.energy gibi)

`site/CNAME` dosyasına alan adını yaz, DNS'te CNAME kaydı GitHub Pages'e (memirutku.github.io) yönlendir. Bkz. [GitHub docs — custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).

# 🚀 Deploy LinkHub Pro — Render + Neon (Free Tier)

## What you'll have at the end
- Live URL: `https://linkhub-pro-XXXX.onrender.com`
- Free PostgreSQL from Neon (never expires)
- Auto-deploys every time you push to GitHub

---

## STEP 1 — Push your project to GitHub

1. Go to https://github.com/new → create a repo called `linkhub-pro`
2. In PowerShell from your project root:

```powershell
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/linkhub-pro.git
git push -u origin main
```

---

## STEP 2 — Create a free Neon database

1. Go to https://neon.tech → Sign up free (GitHub login works)
2. Click "New Project" → name it `linkhub-pro` → Create
3. On the dashboard click "Connection string"
4. Copy the string — looks like:
   `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
5. Save it — you need it in Step 4

---

## STEP 3 — Add a Procfile + gunicorn

Create a file called `Procfile` (no extension) in your project root:

```
web: gunicorn backend.app:app
```

Then in PowerShell:
```powershell
pip install gunicorn
pip freeze > requirements.txt
git add .
git commit -m "add Procfile and gunicorn"
git push
```

---

## STEP 4 — Deploy on Render

1. Go to https://render.com → Sign up free with GitHub
2. Click "New" → "Web Service"
3. Connect your `linkhub-pro` repo
4. Fill in:

| Field | Value |
|-------|-------|
| Name | linkhub-pro |
| Runtime | Python 3 |
| Build Command | pip install -r requirements.txt |
| Start Command | gunicorn backend.app:app |
| Instance Type | Free |

5. Add Environment Variables:

| Key | Value |
|-----|-------|
| DATABASE_URL | your Neon connection string |
| SECRET_KEY | any long random string |
| FLASK_APP | backend/app.py |

6. Click "Create Web Service" — first deploy takes ~2 minutes

---

## STEP 5 — Run migrations

In Render dashboard → your service → "Shell" tab:

```bash
flask db upgrade
```

Your database tables are now created. Done! ✅

---

## STEP 6 — Visit your live app

Go to `https://linkhub-pro-XXXX.onrender.com` and register your account.

---

## Notes on free tier limits

- **Render free:** spins down after 15 min inactivity (first request takes ~30s to wake up). Upgrade to $7/mo "Starter" to keep it always on.
- **Neon free:** 0.5 GB storage, 1 compute unit — more than enough for an MVP.
- **Avatar uploads:** Render's filesystem resets on redeploy. For permanent uploads, add Cloudinary (free tier available).

---

## Troubleshooting

**App error on Render:**
Go to Render → Logs → paste the error

**Database connection error:**
Make sure DATABASE_URL ends with `?sslmode=require`

**Static files missing:**
```powershell
git add static/ -f
git commit -m "add static"
git push
```

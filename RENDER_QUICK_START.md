# RENDER DEPLOYMENT - QUICK COPY-PASTE SETUP

## CRITICAL: Use This Exact Setup

---

## 1️⃣ GITHUB REPOSITORY SETUP (Do This First)

### Create/Update These Files in `flask_app/` folder:

**File: Procfile**
```
web: gunicorn --config gunicorn.conf.py run:app
```

**File: runtime.txt**
```
python-3.10.12
```

Then push to GitHub:
```bash
git add flask_app/Procfile flask_app/runtime.txt
git commit -m "Add Render deployment files"
git push origin main
```

---

## 2️⃣ RENDER DATABASE SETUP

### Create PostgreSQL on Render Dashboard:

1. Click: **+ New → PostgreSQL**
2. Name: `car-tint-db`
3. Database: `cartintdb`
4. User: `cartintuser`
5. **COPY DATABASE URL** - save it somewhere!

URL will look like:
```
postgresql://cartintuser:HASH@HOST:5432/cartintdb
```

---

## 3️⃣ RENDER WEB SERVICE SETUP

### Click: **+ New → Web Service**

**PASTE THESE VALUES EXACTLY:**

| Field | Value |
|-------|-------|
| Connect Repository | Select your CarTitntDetection repo |
| Name | `car-tint-detection` |
| Environment | Python 3 |
| Region | (Choose your region) |
| Branch | `main` |
| Build Command | `cd flask_app && pip install -r requirements.txt` |
| Start Command | `cd flask_app && gunicorn --config gunicorn.conf.py run:app` |
| Plan | Standard |

---

## 4️⃣ ENVIRONMENT VARIABLES - COPY INTO RENDER DASHBOARD

Go to Service Settings → Environment and paste ALL these (one per line):

```
FLASK_ENV=production
FLASK_APP=run.py
RENDER=true
SECRET_KEY=paste-your-32-character-hex-string-here
DATABASE_URL=paste-your-postgresql-url-here
ROBOFLOW_API_KEY=paste-your-roboflow-api-key-here
ROBOFLOW_MODEL_VERSION=paste-your-model-version
ROBOFLOW_MODEL_ID=paste-your-model-id
SQLALCHEMY_TRACK_MODIFICATIONS=False
MAX_CONTENT_LENGTH=16777216
DEBUG=False
```

### How to Get Each Value:

**SECRET_KEY** - Run this command (copy the output):
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Output example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1`

**DATABASE_URL** - Paste the exact URL from Step 2 PostgreSQL instance

**ROBOFLOW_API_KEY** - Get from: Account → Settings → API Keys (on Roboflow.com)

**ROBOFLOW_MODEL_VERSION** - Get from: Your dataset → Publish/Deploy section

**ROBOFLOW_MODEL_ID** - Get from: Your dataset → Publish/Deploy section

---

## 5️⃣ ATTACH PERSISTENT STORAGE (For Uploads)

In Web Service Settings, scroll down to **Disks**:

1. Click: **+ Attach Disk**
2. Name: `uploads`
3. Mount Path: `/var/data`
4. Size: `10` GB (minimum)
5. Click: **Add**

---

## 6️⃣ DEPLOY

1. Click **Create Web Service**
2. Watch the build logs
3. Wait for "Deploy successful" ✅
4. Your URL: `https://car-tint-detection.onrender.com`

---

## ⚠️ IF FIRST DEPLOY FAILS

**Check these things in order:**

1. **Build failed?** → Check build logs for missing dependencies in `requirements.txt`
2. **Deploy successful but app crashes?** → Check logs tab for error details
3. **Database error?** → Verify `DATABASE_URL` in environment variables
4. **Port error?** → Already fixed (Render injects PORT environment variable)

**Run database initialization:**
In Render dashboard, click **Shell** (top right) and run:
```bash
cd flask_app && python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

---

## 🔄 REDEPLOY AFTER MAKING CHANGES

Option 1: **Automatic** - Just `git push` your changes to main branch

Option 2: **Manual** - Go to Renders **Deploys** tab → Click **Deploy** button

---

## 📋 VALIDATION CHECKLIST

Before clicking "Create Web Service", confirm:

- [ ] GitHub repo updated with Procfile and runtime.txt
- [ ] PostgreSQL database created and URL copied
- [ ] Build Command: `cd flask_app && pip install -r requirements.txt`
- [ ] Start Command: `cd flask_app && gunicorn --config gunicorn.conf.py run:app`
- [ ] All 10 environment variables are set (don't skip any!)
- [ ] Persistent disk attached with mount path `/var/data`

---

## 🌐 FINAL TEST

Once deployed, test your API:

```bash
curl https://car-tint-detection.onrender.com/
```

Should return your Flask app homepage (status 200)

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Deployment Issues**: Check Logs tab first
- **Database Issues**: Test DATABASE_URL in Shell with `psql $DATABASE_URL`

🚀 **You're ready to deploy!**

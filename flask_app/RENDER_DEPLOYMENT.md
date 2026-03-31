# Car Tint Detection - Render Deployment Guide

## Complete Step-by-Step Instructions for Render

Follow these steps to deploy your Flask app to Render. Each section contains copy-paste ready commands and configurations.

---

## **STEP 1: Prepare Your Repository**

### 1.1 Verify Your `Procfile` Exists

Your Procfile should be in the `flask_app/` directory with this content:

```
web: gunicorn --config gunicorn.conf.py run:app
```

**If it doesn't exist, create it:**
```bash
cd flask_app
echo 'web: gunicorn --config gunicorn.conf.py run:app' > Procfile
```

### 1.2 Verify `runtime.txt` Exists

Create `flask_app/runtime.txt` with:
```
python-3.10.12
```

**Command to create:**
```bash
cd flask_app
echo 'python-3.10.12' > runtime.txt
```

### 1.3 Create `.gitignore` (if not present)

Create `flask_app/.gitignore`:
```
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.env
.venv/
venv/
instance/
.DS_Store
*.db
*.sqlite
.idea/
.vscode/
uploads/
```

### 1.4 Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## **STEP 2: Create Render Account**

1. Go to [https://render.com](https://render.com)
2. Click **Sign Up** (or Sign In if you have an account)
3. Create an account (GitHub recommended for easier deploys)

---

## **STEP 3: Create a PostgreSQL Database on Render**

Database is required for production deployments.

### 3.1 Create PostgreSQL Instance

1. In Render Dashboard, click **+ New**
2. Select **PostgreSQL**
3. Configure:
   - **Name**: `car-tint-db` (or your preferred name)
   - **Database**: `cartintdb`
   - **User**: `cartintuser`
   - **Region**: Select your preferred region
   - **PostgreSQL Version**: 15
   - **Plan**: Standard (minimum for production)

4. Click **Create Database**
5. **COPY the Database URL** - You'll need this in Step 4

Database URL format:
```
postgresql://cartintuser:<password>@<hostname>:5432/cartintdb
```

---

## **STEP 4: Deploy Flask App to Render**

### 4.1 Create Web Service

1. In Render Dashboard, click **+ New**
2. Select **Web Service**
3. Connect your GitHub repository:
   - Click **Connect GitHub**
   - Authorize Render
   - Select your `CarTitntDetection` repository
   - Click **Connect**

4. Configure the service:
   - **Name**: `car-tint-detection` (can be anything)
   - **Environment**: `Python 3`
   - **Region**: Select your preferred region
   - **Branch**: `main`
   - **Build Command**: 
     ```
     cd flask_app && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     cd flask_app && gunicorn --config gunicorn.conf.py run:app
     ```
   - **Plan**: Standard (minimum recommended)

5. Click **Create Web Service**

---

## **STEP 5: Set Environment Variables**

### 5.1 Add Environment Variables in Render

In the Web Service settings, go to **Environment** and add these variables:

```
FLASK_ENV=production
FLASK_APP=run.py
RENDER=true
SECRET_KEY=your-secret-key-here-minimum-32-characters
DATABASE_URL=postgresql://cartintuser:<password>@<hostname>:5432/cartintdb
ROBOFLOW_API_KEY=your-roboflow-api-key-here
ROBOFLOW_MODEL_VERSION=your-model-version
ROBOFLOW_MODEL_ID=your-model-id
SQLALCHEMY_TRACK_MODIFICATIONS=False
MAX_CONTENT_LENGTH=16777216
```

### 5.2 How to Get Each Value

**SECRET_KEY**: Generate a secure key
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

**DATABASE_URL**: Copy from Step 3.1 (your PostgreSQL URL)

**ROBOFLOW_API_KEY**: 
- Get from your Roboflow account dashboard
- Found under Account Settings → API Keys

**ROBOFLOW_MODEL_VERSION** and **ROBOFLOW_MODEL_ID**:
- Get from your Roboflow dataset
- Found in Model deployment instructions

---

## **STEP 6: Configure Disk Storage (For Uploads)**

If your app needs to store uploaded images:

### 6.1 Create Persistent Disk

1. In Web Service settings, scroll to **Disks**
2. Click **+ Attach Disk**
3. Configure:
   - **Name**: `uploads`
   - **Mount Path**: `/var/data`
   - **Size**: 10 GB (adjust as needed, minimum 1 GB)

4. Click **Add**

Your app will use `/var/data/uploads` (already configured in config.py)

---

## **STEP 7: Deploy and Monitor**

### 7.1 Trigger Deployment

The deployment should automatically start. Monitor it:

1. Go to **Deployments** tab
2. Watch the build logs
3. Wait for "Deploy successful" message
4. Your URL will be available (e.g., `https://car-tint-detection.onrender.com`)

### 7.2 View Logs

In the Web Service dashboard:
1. Click **Logs** tab
2. Monitor real-time application logs

### 7.3 Check Your App

Once deployment is complete:
```
https://your-service-name.onrender.com/
```

---

## **STEP 8: Database Initialization (If Needed)**

If the database isn't initialized on first deploy:

### 8.1 Manual Database Setup

1. In Render Dashboard, go to your Web Service
2. Click **Shell** (top right) to open a terminal
3. Run initialization commands:
   ```bash
   cd flask_app
   python -c "from app import create_app, db; app = create_app('production'); with app.app_context(): db.create_all(); print('Database initialized')"
   ```

---

## **STEP 9: Environment-Specific Configuration**

Your app already detects the Render environment via `RENDER=true` and:
- Uses PostgreSQL connection
- Sets upload path to `/var/data/uploads`
- Disables development mode
- Uses production security settings

No additional configuration needed!

---

## **STEP 10: Redeploy After Changes**

### 10.1 Automatic Redeployment
- Any push to `main` branch automatically triggers a new deploy

### 10.2 Manual Redeployment
1. In Render Dashboard, go to Web Service
2. Click **Deploys** tab
3. Click **Deploy** button next to your latest commit
4. Or click **Clear build cache and deploy** if you're having issues

---

## **Troubleshooting**

### Build Fails
- **Check logs**: View full build logs in Deployments tab
- **Common issues**: Missing dependencies, Python version mismatch
- **Fix**: Ensure `requirements.txt` has all dependencies

### App Crashes After Deploy
- **View logs**: Check Logs tab for error messages
- **Database URL**: Verify `DATABASE_URL` is correct
- **API Keys**: Check all environment variables are set

### Uploads Not Persisting
- **Verify disk**: Check that persistent disk is attached
- **Mount path**: Confirm mount path is `/var/data`

### Timeout Errors
- **Gunicorn timeout**: Already set to 120s for inference tasks
- **Increase if needed**: Add to `gunicorn.conf.py`: `timeout = 240`

### Database Connection Issues
```bash
# Test connection by running in shell:
python
import os
print(os.environ.get('DATABASE_URL'))
```

---

## **Quick Copy-Paste Summary**

For quick reference, here are the key copy-paste blocks:

**Build Command:**
```
cd flask_app && pip install -r requirements.txt
```

**Start Command:**
```
cd flask_app && gunicorn --config gunicorn.conf.py run:app
```

**Required Environment Variables:**
```
FLASK_ENV=production
FLASK_APP=run.py
RENDER=true
SECRET_KEY=<your-32-char-hex-key>
DATABASE_URL=<your-render-postgres-url>
ROBOFLOW_API_KEY=<your-api-key>
ROBOFLOW_MODEL_VERSION=<your-model-version>
ROBOFLOW_MODEL_ID=<your-model-id>
SQLALCHEMY_TRACK_MODIFICATIONS=False
MAX_CONTENT_LENGTH=16777216
```

**Procfile Content:**
```
web: gunicorn --config gunicorn.conf.py run:app
```

**runtime.txt Content:**
```
python-3.10.12
```

---

## **Final Checklist**

Before deploying, ensure:

- [ ] GitHub repository is updated and pushed
- [ ] `Procfile` exists in `flask_app/` directory
- [ ] `runtime.txt` exists in `flask_app/` directory with Python version
- [ ] PostgreSQL database is created on Render
- [ ] Web Service is configured with correct Build and Start commands
- [ ] All environment variables are set
- [ ] Persistent disk is attached (if needed for uploads)
- [ ] Database URL is correctly formatted as `postgresql://...`
- [ ] ROBOFLOW API credentials are set

---

## **Support Resources**

- **Render Docs**: https://render.com/docs
- **Render Help**: https://support.render.com
- **Flask Docs**: https://flask.palletsprojects.com
- **Gunicorn Docs**: https://docs.gunicorn.org

Your app is now deployed on Render! 🚀

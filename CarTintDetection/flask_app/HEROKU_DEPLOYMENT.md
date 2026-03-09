# 🚀 Quick Heroku Deployment Guide

## Step 1: Get Your Roboflow API Key

1. Go to [Roboflow](https://roboflow.com) and create a free account
2. Create a new project or use an existing one for car tint detection
3. Go to **Settings** → **Roboflow API**
4. Copy your **API Key** and **Workspace ID**
5. Note your **Model ID** (found in your project settings)

## Step 2: Install Heroku CLI

### Windows
Download and install from: https://devcenter.heroku.com/articles/heroku-cli

### Mac/Linux
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

Verify installation:
```bash
heroku --version
```

## Step 3: Prepare Your Application

1. **Navigate to the flask_app directory:**
```bash
cd CarTitntDetection\flask_app
```

2. **Initialize Git (if not already done):**
```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

3. **Login to Heroku:**
```bash
heroku login
```

## Step 4: Create Heroku Application

```bash
# Create a new Heroku app (replace 'your-app-name' with your desired name)
heroku create your-app-name

# Or let Heroku generate a random name
heroku create
```

## Step 5: Add PostgreSQL Database

```bash
# Add free PostgreSQL addon
heroku addons:create heroku-postgresql:essential-0
```

## Step 6: Set Environment Variables

### Generate a strong SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Set all required environment variables:
```bash
# Flask configuration
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY="<paste-the-generated-secret-key-here>"
heroku config:set DEBUG=False

# Roboflow API (replace with your actual values)
heroku config:set ROBOFLOW_API_URL=https://serverless.roboflow.com
heroku config:set ROBOFLOW_API_KEY="your-actual-api-key"
heroku config:set MODEL_ID="your-model-id"

# Security settings
heroku config:set SESSION_COOKIE_SECURE=True
heroku config:set SESSION_COOKIE_HTTPONLY=True
heroku config:set SESSION_COOKIE_SAMESITE=Lax

# Upload configuration
heroku config:set MAX_CONTENT_LENGTH=16777216
heroku config:set UPLOAD_FOLDER=/tmp/uploads
```

### Verify your configuration:
```bash
heroku config
```

## Step 7: Deploy to Heroku

```bash
# Push your code to Heroku
git push heroku main

# If you're on a different branch (e.g., master):
# git push heroku master:main
```

## Step 8: Initialize the Database

```bash
# Run database initialization
heroku run python run.py init-db
```

## Step 9: Open Your Application

```bash
heroku open
```

## Step 10: Monitor Your Application

### View logs:
```bash
heroku logs --tail
```

### Check dyno status:
```bash
heroku ps
```

### Restart if needed:
```bash
heroku restart
```

## 🔍 Troubleshooting

### If deployment fails:
```bash
# Check logs for errors
heroku logs --tail

# Verify buildpacks
heroku buildpacks

# Should show: heroku/python
```

### If database connection fails:
```bash
# Verify DATABASE_URL is set
heroku config:get DATABASE_URL

# Re-initialize database
heroku run python run.py init-db
```

### If the app crashes:
```bash
# Scale up the dyno
heroku ps:scale web=1

# Check for errors
heroku logs --tail
```

## 📊 Post-Deployment Checklist

- [ ] App opens successfully
- [ ] Can create a new account
- [ ] Can login
- [ ] Can upload images for tint detection
- [ ] API responds correctly
- [ ] Database is working (test history saved)

## 🎯 Performance Tips

### Upgrade dyno for better performance:
```bash
# Professional dyno (recommended for production)
heroku ps:type professional-2x
```

### Add Redis for caching (optional):
```bash
heroku addons:create heroku-redis:mini
```

### Enable automatic backups:
```bash
heroku pg:backups:schedule DATABASE_URL --at '02:00 America/Los_Angeles'
```

## 🔒 Security Recommendations

1. **Enable SSL (automatically done by Heroku)**
2. **Set up custom domain:**
   ```bash
   heroku domains:add www.yourdomain.com
   ```

3. **Enable Heroku's automated certificate management:**
   ```bash
   heroku certs:auto:enable
   ```

## 📈 Monitoring & Maintenance

### View metrics:
```bash
heroku addons:create newrelic:wayne
```

### Set up alerts:
- Log into your Heroku dashboard
- Go to your app → Metrics
- Set up alerts for response time, memory, etc.

## 🔄 Updating Your Application

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push heroku main

# Database migrations (if you add Flask-Migrate)
heroku run flask db upgrade
```

## 💰 Cost Estimate

- **Eco Dyno**: $5/month (sleeps after 30 min of inactivity)
- **Essential PostgreSQL**: $5/month
- **Professional Dyno**: $25/month (recommended, never sleeps)
- **Total**: $10-30/month depending on your needs

## 🆘 Need Help?

- Heroku DevCenter: https://devcenter.heroku.com
- Heroku Support: https://help.heroku.com
- Your deployment logs: `heroku logs --tail`

---

**Your app will be available at:** `https://your-app-name.herokuapp.com`

Good luck with your deployment! 🎉

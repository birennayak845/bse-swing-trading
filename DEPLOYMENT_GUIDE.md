# Swing Trading Platform - Deployment Guide

Complete guide to deploy your Next.js frontend and Flask backend to production.

## 📋 Overview

- **Frontend**: Next.js → Deploy to Vercel (recommended) or Netlify
- **Backend**: Flask → Deploy to Railway, Render, or PythonAnywhere

## 🚀 Option 1: Quick Deploy (Recommended)

### Frontend to Vercel + Backend to Railway

This is the fastest and easiest option with generous free tiers.

---

## 📦 Part 1: Deploy Frontend to Vercel

### Prerequisites
- GitHub account
- Vercel account (sign up at https://vercel.com)

### Step 1: Push to GitHub

```bash
cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app

# Add all files
git add .

# Commit changes
git commit -m "Add Next.js frontend with expandable stock cards"

# Push to GitHub
git push origin main
```

If you don't have a GitHub repo yet:

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/swing-trading-app.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Vercel

1. **Go to Vercel**: https://vercel.com/new

2. **Import Repository**:
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure Project**:
   - **Framework**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `.next` (auto-filled)

4. **Environment Variables**:
   Click "Environment Variables" and add:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-url.up.railway.app
   ```
   (You'll get this URL after deploying the backend)

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be live at: `https://your-project.vercel.app`

### Step 3: Update Frontend Later

For backend URL, you'll need to:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` with your Railway backend URL
3. Redeploy (Vercel → Deployments → Redeploy)

---

## 🐍 Part 2: Deploy Backend to Railway

### Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)

### Step 1: Prepare Backend Files

Create `railway.json` in the root:

```bash
cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app
```

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Ensure `gunicorn` is in `requirements.txt`:

```bash
echo "gunicorn" >> requirements.txt
```

### Step 2: Deploy to Railway

1. **Go to Railway**: https://railway.app/new

2. **Deploy from GitHub**:
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Select the `swing_trading_app` folder (root directory)

3. **Configure**:
   - Railway will auto-detect Python
   - It will use `requirements.txt` to install dependencies
   - Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

4. **Environment Variables** (Optional):
   - Railway automatically sets `PORT`
   - No other env vars needed for basic setup

5. **Get Your URL**:
   - After deployment, go to Settings → Generate Domain
   - Copy the URL (e.g., `https://your-app.up.railway.app`)

6. **Update Frontend**:
   - Go back to Vercel
   - Add/Update `NEXT_PUBLIC_API_URL` with your Railway URL
   - Redeploy frontend

### Step 3: Enable CORS for Production

Update `app.py` to allow your Vercel domain:

```python
from flask_cors import CORS

# Update CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-project.vercel.app",
            "http://localhost:3000"  # Keep for local development
        ]
    }
})
```

Commit and push changes:

```bash
git add app.py
git commit -m "Update CORS for production"
git push
```

Railway will auto-redeploy.

---

## 🎯 Alternative: Deploy Backend to Render

### Step 1: Create Render Account
Sign up at https://render.com

### Step 2: Create New Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: `swing-trading-backend`
   - **Root Directory**: `swing_trading_app`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
   - **Plan**: Free

4. Click "Create Web Service"

5. Get URL from Render dashboard and update Vercel env vars

---

## 🔧 Environment Variables Summary

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### Backend (Railway/Render)
```
PORT=auto-set by platform
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Code committed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `package.json` has correct scripts
- [ ] Environment variables documented

### Frontend Deployment
- [ ] Repository imported to Vercel
- [ ] Root directory set to `frontend`
- [ ] `NEXT_PUBLIC_API_URL` environment variable added
- [ ] Build successful
- [ ] Site is live and accessible

### Backend Deployment
- [ ] Repository imported to Railway/Render
- [ ] Python environment detected
- [ ] Dependencies installed successfully
- [ ] App starts without errors
- [ ] API endpoint responds correctly
- [ ] CORS configured for frontend domain

### Post-Deployment
- [ ] Frontend can fetch data from backend
- [ ] Stock predictions display correctly
- [ ] Expand/collapse functionality works
- [ ] All filters work (stock count, probability)
- [ ] Refresh button works
- [ ] Dark mode works

---

## 🧪 Testing Your Deployment

### Test Backend API
```bash
curl https://your-backend.up.railway.app/api/health
# Should return: {"status": "ok", "timestamp": "..."}

curl "https://your-backend.up.railway.app/api/top-stocks?limit=3"
# Should return stock data
```

### Test Frontend
1. Visit your Vercel URL
2. Wait for stocks to load
3. Try changing stock count
4. Try changing probability filter
5. Click to expand a stock card
6. Check mobile responsiveness

---

## 🐛 Troubleshooting

### Frontend Issues

**"Failed to fetch stocks" error:**
- Check `NEXT_PUBLIC_API_URL` is correct in Vercel
- Verify backend is running: `curl https://your-backend-url/api/health`
- Check browser console for CORS errors

**Build fails:**
```bash
# Test locally first
cd frontend
npm run build
```

### Backend Issues

**App won't start:**
- Check Railway/Render logs
- Verify all dependencies in `requirements.txt`
- Ensure `gunicorn` is installed

**Timeout errors:**
- First load is slow (analyzing stocks)
- Subsequent loads use cache (fast)
- Consider increasing timeout in platform settings

**CORS errors:**
- Update `app.py` with correct frontend URL
- Redeploy backend

---

## 💰 Cost Estimates

### Free Tier Limits

**Vercel (Frontend)**:
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Custom domain support
- **Cost**: FREE

**Railway (Backend)**:
- ✅ $5 free credit/month
- ✅ 500 hours runtime
- ✅ Sleep after inactivity
- **Cost**: FREE (with credit)

**Render (Backend Alternative)**:
- ✅ 750 hours/month
- ✅ Sleeps after 15min inactivity
- ✅ Cold starts (slow first load)
- **Cost**: FREE

---

## 🔄 Updating Your App

### Update Frontend
```bash
cd frontend
# Make changes...
git add .
git commit -m "Update frontend"
git push
# Vercel auto-deploys
```

### Update Backend
```bash
cd swing_trading_app
# Make changes...
git add .
git commit -m "Update backend"
git push
# Railway auto-deploys
```

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain (e.g., `stockanalyzer.com`)
3. Update DNS records as instructed
4. SSL certificate automatically generated

### Add Custom Domain to Railway

1. Go to Railway Dashboard → Your Project → Settings
2. Click "Generate Domain" or add custom domain
3. Update DNS records

---

## 📊 Monitoring

### Vercel Analytics
- Enable in Vercel Dashboard → Your Project → Analytics
- Track page views, performance, errors

### Railway Logs
- View in Railway Dashboard → Your Project → Deployments → Logs
- Monitor API requests, errors

---

## 🔐 Security Best Practices

1. **Never commit sensitive data**:
   - `.env` files are in `.gitignore`
   - Use environment variables for secrets

2. **CORS Configuration**:
   - Only allow your frontend domain
   - Don't use `*` in production

3. **Rate Limiting** (Future Enhancement):
   - Add rate limiting to prevent abuse
   - Use Flask-Limiter

4. **HTTPS Only**:
   - Both Vercel and Railway use HTTPS by default
   - Never use HTTP in production

---

## 📚 Additional Resources

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

## 🎉 You're Live!

Once deployed, share your app:
- **Frontend**: https://your-project.vercel.app
- **Backend API**: https://your-backend.up.railway.app/api/top-stocks

Your swing trading analyzer is now accessible to anyone with the URL!

**Remember**: This is for educational purposes only. Include the risk disclaimer on your site.

---

**Last Updated**: December 15, 2024

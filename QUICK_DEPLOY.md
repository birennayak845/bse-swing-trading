# Quick Deploy Guide

Deploy your Swing Trading Platform in 10 minutes!

## 🚀 Step-by-Step Deployment

### 1️⃣ Push to GitHub (2 minutes)

```bash
# Navigate to project
cd /Users/biren.nayak/Documents/NetMeds/Experiments/Refill_Reminder/Catalogue-uat/swing_trading_app

# Stage all changes
git add .

# Commit
git commit -m "Ready for deployment: Next.js frontend + Flask backend"

# Push to GitHub
git push origin main
```

If you don't have a remote:
```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/swing-trading-app.git
git push -u origin main
```

---

### 2️⃣ Deploy Backend to Railway (3 minutes)

1. **Sign up**: https://railway.app (use GitHub)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `swing-trading-app` repository
   - Railway auto-detects Python

3. **Generate Domain**:
   - Go to Settings → Networking
   - Click "Generate Domain"
   - Copy the URL: `https://your-app.up.railway.app`

4. **Test Backend**:
   ```bash
   curl https://your-app.up.railway.app/api/health
   ```

✅ Backend is live!

---

### 3️⃣ Deploy Frontend to Vercel (3 minutes)

1. **Sign up**: https://vercel.com (use GitHub)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - **Root Directory**: `frontend`
   - Vercel auto-detects Next.js

3. **Add Environment Variable**:
   - Before clicking Deploy, add:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
   ```
   (Use your Railway URL from step 2)

4. **Deploy**:
   - Click "Deploy"
   - Wait 2 minutes
   - Get your URL: `https://your-project.vercel.app`

✅ Frontend is live!

---

### 4️⃣ Update CORS (2 minutes)

Update `app.py` to allow your Vercel domain:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-project.vercel.app",  # Your Vercel URL
            "http://localhost:3000"
        ]
    }
})
```

Push changes:
```bash
git add app.py
git commit -m "Update CORS for production"
git push
```

Railway will auto-redeploy in 1 minute.

---

## ✅ Done!

Your app is now live:

🌐 **Frontend**: https://your-project.vercel.app
🔗 **Backend API**: https://your-app.up.railway.app/api/top-stocks

---

## 🧪 Test Your Deployment

1. Open your Vercel URL in browser
2. Wait for stocks to load (first load: 30-60s)
3. Try expanding a stock card
4. Change filters and click Refresh
5. Check on mobile device

---

## 🎨 Customize Your URLs

### Vercel (Free)
- Go to Settings → Domains
- Add custom domain or use: `your-project.vercel.app`

### Railway (Free)
- Settings → Networking → Custom Domain
- Or use generated: `your-app.up.railway.app`

---

## 🔄 Future Updates

**Update Frontend:**
```bash
# Make changes in frontend/
git add .
git commit -m "Update UI"
git push
# Vercel auto-deploys
```

**Update Backend:**
```bash
# Make changes in root
git add .
git commit -m "Update API"
git push
# Railway auto-deploys
```

---

## 💡 Pro Tips

1. **First Load is Slow**: Backend analyzes 20+ stocks (30-60s)
2. **Subsequent Loads are Fast**: Cache for 15 minutes
3. **Free Tier Limits**:
   - Vercel: Unlimited
   - Railway: $5 credit/month (~450 hours)
4. **Cold Starts**: Railway may sleep after inactivity

---

## 🆘 Troubleshooting

**Frontend can't connect to backend:**
- Check `NEXT_PUBLIC_API_URL` in Vercel settings
- Verify Railway app is running (check logs)
- Update CORS in `app.py` with correct Vercel URL

**Backend errors:**
- Check Railway logs (Deployments → Logs)
- Verify all dependencies in `requirements.txt`
- Ensure PORT environment variable is set (auto by Railway)

---

## 📱 Share Your App

Once live, anyone can access your swing trading analyzer:

**Share link**: `https://your-project.vercel.app`

Add to:
- LinkedIn portfolio
- GitHub README
- Resume projects
- Twitter/social media

---

**Need help?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

**Congratulations! Your app is live! 🎉**

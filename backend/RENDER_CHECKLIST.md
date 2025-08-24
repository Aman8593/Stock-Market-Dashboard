# 📋 Render Deployment Checklist

## Before You Start

- [ ] GitHub repository is up to date
- [ ] MongoDB Atlas account created (free tier)
- [ ] Google OAuth credentials ready

## Quick Deploy Steps

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 2. Create Render Service

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your repository
4. Use these settings:
   - **Name**: `stocksage-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables

```
PYTHON_VERSION=3.11.0
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/stocksage
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-random-secret-key
CORS_ORIGINS=http://localhost:5173
```

### 4. Deploy & Test

- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Test: `https://your-app.onrender.com/health`

## 🎯 Your App URLs

- **API Base**: `https://stocksage-api.onrender.com`
- **Health Check**: `https://stocksage-api.onrender.com/health`
- **Stocks List**: `https://stocksage-api.onrender.com/stocks`
- **Live Signals**: `https://stocksage-api.onrender.com/api/v1/live-top-signals`

## ⚠️ Important Notes

- **Free tier sleeps** after 15 minutes of inactivity
- **Cold start** takes 30-60 seconds to wake up
- **750 hours/month** limit on free tier
- Update `CORS_ORIGINS` after deploying frontend

## 🔧 If Something Goes Wrong

1. Check build logs in Render dashboard
2. Verify all environment variables are set
3. Test endpoints one by one
4. Check MongoDB Atlas network access (allow 0.0.0.0/0)

That's it! Your Stock Sage API will be live on Render 🚀

# Stock Sage Deployment Guide

## 🚀 Free Deployment Strategy

### Backend Deployment (Railway - Recommended)

1. **Create Railway Account**

   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**

   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the Dockerfile
   - Add environment variables:
     - `MONGODB_URL`: Your MongoDB connection string
     - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
     - `GOOGLE_CLIENT_SECRET`: Your Google OAuth secret
     - `JWT_SECRET_KEY`: A secure random string
     - `CORS_ORIGINS`: Your frontend URL (add after frontend deployment)

3. **Get Backend URL**
   - After deployment, copy the Railway app URL (e.g., `https://stocksage-api.railway.app`)

### Frontend Deployment (Vercel - Recommended)

1. **Create Vercel Account**

   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Deploy Frontend**

   - Click "New Project" → Import from GitHub
   - Select your repository
   - Set root directory to `frontend`
   - Add environment variables:
     - `VITE_API_BASE_URL`: Your Railway backend URL
     - `VITE_GOOGLE_CLIENT_ID`: Your Google OAuth client ID

3. **Update Backend CORS**
   - Copy your Vercel URL (e.g., `https://stocksage.vercel.app`)
   - Update Railway environment variable `CORS_ORIGINS` to include your Vercel URL

### Alternative: Render Deployment

**Backend on Render:**

1. Go to [render.com](https://render.com)
2. Create "New Web Service" from GitHub
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Frontend on Netlify:**

1. Go to [netlify.com](https://netlify.com)
2. Drag and drop your `frontend/dist` folder after running `npm run build`

## 🌐 Free Domain Options

### 1. Platform Subdomains (Easiest)

- **Vercel**: `stocksage.vercel.app`
- **Railway**: `stocksage.railway.app`
- **Netlify**: `stocksage.netlify.app`

### 2. Free Custom Domains

- **Freenom**: Free .tk, .ml, .ga, .cf domains
- **InfinityFree**: Free hosting with subdomain
- **GitHub Pages**: `username.github.io/stocksage`

### 3. Recommended Custom Domain

- Buy from **Namecheap** (~$10/year for .com)
- Use **Cloudflare** for free DNS and SSL

## 📋 Pre-Deployment Checklist

### Backend Preparation

- [ ] Create `requirements.txt` ✅
- [ ] Add `Dockerfile` ✅
- [ ] Add health check endpoint ✅
- [ ] Configure environment variables ✅
- [ ] Update CORS for production ✅

### Frontend Preparation

- [ ] Create `vercel.json` ✅
- [ ] Create `netlify.toml` ✅
- [ ] Add production environment variables ✅
- [ ] Test build locally: `npm run build`

### Environment Variables Setup

- [ ] MongoDB Atlas (free tier)
- [ ] Google OAuth credentials
- [ ] JWT secret key
- [ ] Update API URLs

## 🔧 Local Testing Before Deployment

```bash
# Test backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Test frontend build
cd frontend
npm install
npm run build
npm run preview
```

## 🚀 Quick Deploy Commands

```bash
# 1. Prepare repository
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Deploy backend to Railway
# - Connect GitHub repo
# - Set environment variables
# - Deploy automatically

# 3. Deploy frontend to Vercel
# - Connect GitHub repo
# - Set root directory to 'frontend'
# - Set environment variables
# - Deploy automatically

# 4. Update CORS origins in Railway with Vercel URL
```

## 🎯 Recommended Setup

1. **Backend**: Railway (free tier)
2. **Frontend**: Vercel (free tier)
3. **Database**: MongoDB Atlas (free tier)
4. **Domain**: Use platform subdomains initially
5. **Monitoring**: Use platform built-in monitoring

## 💡 Pro Tips

- Use platform subdomains initially to test everything
- Add custom domain later once everything works
- Set up automatic deployments from GitHub
- Monitor usage to stay within free tier limits
- Use environment variables for all configuration

## 🔍 Troubleshooting

**CORS Issues**: Make sure to update `CORS_ORIGINS` environment variable with your frontend URL

**Build Failures**: Check that all dependencies are in `requirements.txt`

**Environment Variables**: Double-check all required environment variables are set

**Database Connection**: Ensure MongoDB Atlas allows connections from anywhere (0.0.0.0/0) for Railway

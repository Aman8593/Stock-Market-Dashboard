# 🚀 Deploy Stock Sage Backend on Render

## Step-by-Step Render Deployment Guide

### Prerequisites

- GitHub account with your Stock Sage repository
- MongoDB Atlas account (free tier)
- Google OAuth credentials

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to GitHub:**

   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify these files exist in your `backend/` directory:**
   - ✅ `requirements.txt`
   - ✅ `app.py`
   - ✅ `render.yaml`
   - ✅ `build.sh`
   - ✅ `.env.example`

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account**
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. **Click "New +" → "Web Service"**
2. **Connect Repository:**

   - Select "Build and deploy from a Git repository"
   - Click "Connect" next to your Stock Sage repository
   - If not visible, click "Configure GitHub App" to grant access

3. **Configure Service Settings:**
   ```
   Name: stocksage-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

### Step 4: Set Environment Variables

Click **"Advanced"** and add these environment variables:

```bash
# Required Environment Variables
PYTHON_VERSION=3.11.0
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/stocksage
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
CORS_ORIGINS=http://localhost:5173,https://your-frontend-url.vercel.app
```

**How to get these values:**

1. **MONGODB_URL**:

   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create free cluster → Connect → Connect your application
   - Copy connection string and replace `<password>` with your password

2. **Google OAuth Credentials**:

   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create project → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Add your Render URL to authorized origins

3. **JWT_SECRET_KEY**: Generate a random string:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes for first deploy)
3. **Monitor build logs** for any errors
4. **Your API will be available at**: `https://stocksage-api.onrender.com`

### Step 6: Test Deployment

1. **Test health endpoint:**

   ```bash
   curl https://your-app-name.onrender.com/health
   ```

2. **Test API endpoint:**

   ```bash
   curl https://your-app-name.onrender.com/stocks
   ```

3. **Check live signals:**
   ```bash
   curl https://your-app-name.onrender.com/api/v1/live-top-signals
   ```

### Step 7: Update Frontend Configuration

Update your frontend environment variables:

```bash
# In frontend/.env.production
VITE_API_BASE_URL=https://your-app-name.onrender.com
```

### Step 8: Update CORS (Important!)

After deploying frontend, update the `CORS_ORIGINS` environment variable in Render:

```
CORS_ORIGINS=https://your-frontend-url.vercel.app,https://your-custom-domain.com
```

## 🔧 Render-Specific Configuration

### Free Tier Limitations

- **Sleep after 15 minutes** of inactivity
- **750 hours/month** of runtime
- **Cold starts** (30-60 seconds to wake up)
- **512 MB RAM**

### Optimization Tips

1. **Keep service warm** with uptime monitoring (like UptimeRobot)
2. **Optimize imports** to reduce cold start time
3. **Use caching** for expensive operations
4. **Monitor usage** in Render dashboard

## 🚨 Troubleshooting

### Common Issues:

1. **Build Fails - Missing Dependencies:**

   ```bash
   # Check requirements.txt has all packages
   pip freeze > requirements.txt
   ```

2. **App Won't Start - Port Issues:**

   ```bash
   # Ensure you're using $PORT environment variable
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

3. **CORS Errors:**

   ```bash
   # Update CORS_ORIGINS environment variable
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

4. **Database Connection Issues:**

   ```bash
   # Check MongoDB Atlas network access
   # Allow access from anywhere: 0.0.0.0/0
   ```

5. **Cold Start Issues:**
   ```bash
   # Service sleeps after 15 minutes on free tier
   # Use uptime monitoring to keep it warm
   ```

### Debug Commands:

```bash
# View logs in Render dashboard
# Or check health endpoint
curl https://your-app.onrender.com/health

# Test specific endpoints
curl https://your-app.onrender.com/stocks
curl https://your-app.onrender.com/api/v1/analysis-status
```

## 📊 Monitoring Your Deployment

1. **Render Dashboard**: Monitor CPU, memory, and request metrics
2. **Health Checks**: Render automatically monitors `/health` endpoint
3. **Logs**: View real-time logs in Render dashboard
4. **Uptime Monitoring**: Use external service to prevent sleeping

## 🎯 Next Steps After Deployment

1. **Deploy Frontend** on Vercel/Netlify
2. **Update CORS** with frontend URL
3. **Test full application** end-to-end
4. **Set up monitoring** (UptimeRobot for free tier)
5. **Configure custom domain** (optional)

## 💡 Pro Tips

- **Use environment variables** for all configuration
- **Test locally first** with same environment variables
- **Monitor free tier usage** to avoid overages
- **Keep service warm** with periodic requests
- **Use Render's built-in SSL** (automatic HTTPS)

Your Stock Sage API will be live at: `https://stocksage-api.onrender.com` 🚀

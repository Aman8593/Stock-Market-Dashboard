# 🎯 Your Stock Sage Deployment Configuration

## ✅ Frontend Status

- **URL**: https://stock-market-dashboard-psi.vercel.app
- **Platform**: Vercel
- **Status**: ✅ Already Deployed

## 🚀 Backend Deployment on Render

### Environment Variables for Render:

```bash
PYTHON_VERSION=3.11.0
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/stocksage
GOOGLE_CLIENT_ID=901831058444-aulhp05opla5c42a6vr3srkljh0kdei0.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-super-secret-random-key
CORS_ORIGINS=https://stock-market-dashboard-psi.vercel.app,http://localhost:5173
```

### Render Service Settings:

```
Name: stocksage-api
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

## 🔗 Final URLs After Backend Deployment:

- **Frontend**: https://stock-market-dashboard-psi.vercel.app
- **Backend**: https://stocksage-api.onrender.com
- **API Health**: https://stocksage-api.onrender.com/health

## 📋 Next Steps:

### 1. Deploy Backend on Render

1. Go to [render.com](https://render.com)
2. Create Web Service from your GitHub repo
3. Use settings above
4. Add environment variables above

### 2. Update Frontend Environment Variables in Vercel

1. Go to your Vercel dashboard
2. Select your project: `stock-market-dashboard-psi`
3. Go to Settings → Environment Variables
4. Add/Update:
   ```
   VITE_API_BASE_URL=https://stocksage-api.onrender.com
   VITE_GOOGLE_CLIENT_ID=901831058444-aulhp05opla5c42a6vr3srkljh0kdei0.apps.googleusercontent.com
   ```
5. Redeploy frontend

### 3. Test Full Application

- Frontend: https://stock-market-dashboard-psi.vercel.app
- Backend health: https://stocksage-api.onrender.com/health
- API test: https://stocksage-api.onrender.com/stocks

## ⚠️ Important Notes:

- **CORS is configured** for your Vercel URL
- **Google OAuth** client ID is already set
- **Free tier limitations**: Backend sleeps after 15 minutes
- **Cold starts**: 30-60 seconds to wake up

## 🎯 What You Need:

1. **MongoDB connection string** (from MongoDB Atlas)
2. **Google OAuth client secret** (from Google Cloud Console)
3. **JWT secret key** (generate random string)

## 🔧 Generate JWT Secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Your setup is almost complete! Just deploy the backend and update the frontend environment variables. 🚀

# 🚀 PaaS Deployment Guide for Climbing Tracker

This guide covers deploying to managed PaaS platforms (Render, Fly.io, Railway).

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub (without `.env` file)
2. **MongoDB Atlas**: Your database should be accessible from the internet
3. **Google OAuth**: Configured with the correct redirect URIs for your domain

## 🔧 Environment Variables Required

Set these in your PaaS platform dashboard (never in your code):

```env
SECRET_KEY=your-long-random-secret-key-here
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ClimbingApp
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

## 🎯 Platform-Specific Deployment

### 🟢 **Render.com** (Recommended - Easiest)

1. **Create Service**:
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Choose the `main` branch

2. **Configuration**:
   - **Name**: `climbing-tracker`
   - **Environment**: `Docker` (if using Dockerfile) or `Python` (auto-detect)
   - **Build Command**: `pip install -r requirements.txt` (auto-detected)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**:
   - Go to "Environment" tab
   - Add all required environment variables from above

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically deploy and provide HTTPS

### 🟦 **Fly.io** (Good Performance)

1. **Install CLI**:
   ```bash
   # Install flyctl
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and Launch**:
   ```bash
   fly auth login
   fly launch
   ```

3. **Set Secrets**:
   ```bash
   fly secrets set SECRET_KEY="your-secret-key"
   fly secrets set MONGODB_URL="your-mongodb-url"
   fly secrets set DATABASE_NAME="ClimbingApp"
   fly secrets set GOOGLE_CLIENT_ID="your-client-id"
   fly secrets set GOOGLE_CLIENT_SECRET="your-client-secret"
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

### 🟣 **Railway** (Simple & Fast)

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your repository

2. **Environment Variables**:
   - Go to "Variables" tab
   - Add all required environment variables

3. **Deploy**:
   - Railway auto-deploys on push
   - Provides automatic HTTPS and domain

## 🔗 Google OAuth Setup

**Important**: Update your Google OAuth settings with your new domain:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" → "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add your new domain to "Authorized redirect URIs":
   ```
   https://your-app-name.onrender.com/auth/google/callback
   https://your-app-name.fly.dev/auth/google/callback
   https://your-app-name.up.railway.app/auth/google/callback
   ```

## 🛡️ Security Checklist

- ✅ Environment variables set in platform dashboard (not in code)
- ✅ `.env` file in `.gitignore` (never pushed to GitHub)
- ✅ HTTPS enabled (automatic on these platforms)
- ✅ Google OAuth redirect URIs updated
- ✅ MongoDB Atlas IP whitelist configured (0.0.0.0/0 for cloud deployment)

## 🔄 Automatic Deployment

All platforms support auto-deployment:
- **Render**: Auto-deploys on git push to main branch
- **Fly.io**: Run `fly deploy` or set up GitHub Actions
- **Railway**: Auto-deploys on git push

## 📊 Monitoring

Each platform provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, response times
- **Health Checks**: Automatic monitoring

## 🆘 Troubleshooting

**Common Issues**:

1. **OAuth Redirect Error**: Update Google OAuth redirect URIs
2. **Database Connection**: Check MongoDB Atlas IP whitelist
3. **Environment Variables**: Verify all secrets are set correctly
4. **Port Issues**: Ensure your app uses `$PORT` environment variable

**Debug Commands**:
```bash
# Render
# Check logs in dashboard

# Fly.io
fly logs

# Railway
# Check logs in dashboard
```

## 💰 Costs

- **Render**: Free tier available, $7/month for production
- **Fly.io**: Pay-as-you-go, ~$5-10/month for small app
- **Railway**: $5/month for hobby plan

Choose based on your needs and budget! 🚀
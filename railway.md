# Railway deployment configuration
# No special config needed - Railway auto-detects Python apps

# Environment Variables needed (set in Railway dashboard):
# SECRET_KEY=your-secret-key
# MONGODB_URL=your-mongodb-connection-string  
# DATABASE_NAME=your-database-name
# GOOGLE_CLIENT_ID=your-google-oauth-client-id
# GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# Railway will automatically:
# - Detect this as a Python app
# - Install from requirements.txt
# - Run with the detected start command
# - Provide HTTPS automatically
# - Give you a public domain

# Optional: Custom start command (Railway usually detects correctly)
# In Railway dashboard, you can override with:
# uvicorn main:app --host 0.0.0.0 --port $PORT
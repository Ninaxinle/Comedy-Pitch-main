# Mock S3 Setup Guide

## Option 1: MinIO Community Edition (S3-Compatible Mock)

### Step 1: Download MinIO Community Edition

**IMPORTANT**: Download the **Community Edition** (free), not the Enterprise version!

1. **Download from GitHub (FREE Community Edition):**
   - Go to: https://github.com/minio/minio/releases
   - Download the latest release for Windows: `minio.exe`
   - Direct link: https://github.com/minio/minio/releases/latest/download/minio.exe

2. **Alternative: Use PowerShell to download:**
   ```powershell
   Invoke-WebRequest -Uri "https://github.com/minio/minio/releases/latest/download/minio.exe" -OutFile "minio.exe"
   ```

3. **Add to PATH:**
   - Move `minio.exe` to a folder (e.g., `C:\minio`)
   - Add the folder to your system PATH
   - Or run it directly from the folder

### Step 2: Start MinIO Server

```bash
# Create data directory (already done)
mkdir C:\minio-data

# Start MinIO server
minio server C:\minio-data --console-address :9001
```

This will start:
- MinIO API server on `http://localhost:9000`
- MinIO Console on `http://localhost:9001`

### Step 3: Configure Your .env File

Add these settings to your `.env` file:

```env
# Storage Backend Configuration - Using MinIO for Mock S3
STORAGE_BACKEND=minio

# MinIO Configuration (Mock S3)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=comedy-peach
MINIO_SECURE=false
```

### Step 4: Install Python Dependencies

```bash
pip install minio
```

### Step 5: Test the Setup

1. Start your FastAPI server
2. Go to MinIO Console: http://localhost:9001
3. Login with: `minioadmin` / `minioadmin`
4. You should see the `comedy-peach` bucket created automatically

## Option 2: Local Storage (Simpler Alternative)

If you don't want to run MinIO, you can use local storage:

```env
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./uploads
LOCAL_STORAGE_URL=http://localhost:8000/uploads/
```

## Option 3: Docker MinIO (Alternative)

If you have Docker:

```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v C:\minio-data:/data \
  minio/minio server /data --console-address ":9001"
```

## Testing Your Setup

1. Start MinIO server
2. Update your `.env` file
3. Start your FastAPI server
4. Test file upload via your API endpoints
5. Check MinIO console to see uploaded files

## Benefits of MinIO for Mock S3

- ✅ S3-compatible API
- ✅ Same code works with real S3
- ✅ Local development
- ✅ No AWS costs
- ✅ Easy to switch to real S3 later

## Troubleshooting

### "No license found" Error
- **Problem**: You downloaded the Enterprise version
- **Solution**: Download from GitHub releases (Community Edition)
- **Correct URL**: https://github.com/minio/minio/releases/latest/download/minio.exe

### Port Already in Use
- **Problem**: Port 9000 or 9001 is already in use
- **Solution**: Use different ports:
  ```bash
  minio server C:\minio-data --console-address :9002 --address :9003
  ``` 
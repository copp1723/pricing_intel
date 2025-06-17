# Pricing Intelligence Platform - Deployment Guide

This guide provides step-by-step instructions for deploying the Pricing Intelligence Platform in various environments.

## 🚀 Quick Deployment (Recommended)

### Automated Deployment
The fastest way to deploy the platform is using the automated deployment script:

```bash
cd /home/ubuntu/pricing-intelligence-platform
./scripts/deploy.sh
```

This script will:
- Check prerequisites
- Set up backend and frontend
- Run integration tests
- Start both services
- Generate a deployment report

### Manual Verification
After deployment, verify the system is working:

1. **Check Services**:
   - Backend: http://localhost:5001/api/health
   - Frontend: http://localhost:5173

2. **Run Tests**:
   ```bash
   python3.11 tests/integration_tests.py
   ```

3. **View Dashboard**:
   - Open http://localhost:5173 in your browser
   - Navigate through different sections
   - Test data refresh functionality

## 🏗️ Manual Deployment

### Backend Deployment

1. **Navigate to Backend Directory**:
   ```bash
   cd /home/ubuntu/pricing-intelligence-platform/backend/pricing-api
   ```

2. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Backend Server**:
   ```bash
   python src/main.py
   ```

The backend will be available at http://localhost:5001

### Frontend Deployment

1. **Navigate to Frontend Directory**:
   ```bash
   cd /home/ubuntu/pricing-intelligence-platform/frontend/pricing-dashboard
   ```

2. **Install Dependencies**:
   ```bash
   pnpm install
   ```

3. **Start Development Server**:
   ```bash
   pnpm run dev --host
   ```

The frontend will be available at http://localhost:5173

### Production Build (Frontend)

For production deployment, build the frontend:

```bash
cd /home/ubuntu/pricing-intelligence-platform/frontend/pricing-dashboard
pnpm run build
```

The built files will be in the `dist/` directory.

## 🌐 Production Deployment

### Using Manus Service Tools

The platform is ready for production deployment using Manus service tools:

#### Deploy Backend
```bash
cd /home/ubuntu/pricing-intelligence-platform/backend/pricing-api
# The backend is ready for Flask deployment
```

#### Deploy Frontend
```bash
cd /home/ubuntu/pricing-intelligence-platform/frontend/pricing-dashboard
pnpm run build
# The dist/ directory contains the built React app
```

### Traditional Production Setup

#### Backend (Flask + Gunicorn)

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Configuration** (`gunicorn.conf.py`):
   ```python
   bind = "0.0.0.0:5001"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 100
   timeout = 30
   keepalive = 2
   ```

3. **Start with Gunicorn**:
   ```bash
   gunicorn --config gunicorn.conf.py src.main:app
   ```

#### Frontend (Nginx)

1. **Build Frontend**:
   ```bash
   pnpm run build
   ```

2. **Nginx Configuration** (`/etc/nginx/sites-available/pricing-platform`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       root /path/to/pricing-intelligence-platform/frontend/pricing-dashboard/dist;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🐳 Docker Deployment

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/pricing-api/ .

RUN pip install -r requirements.txt

EXPOSE 5001
CMD ["python", "src/main.py"]
```

### Frontend Dockerfile
```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY frontend/pricing-dashboard/ .

RUN npm install -g pnpm
RUN pnpm install
RUN pnpm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
  
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db

# API Configuration
VIN_API_KEY=your-vin-api-key
CORS_ORIGINS=*

# Monitoring
ENABLE_MONITORING=true
LOG_LEVEL=INFO
```

### Database Configuration

For production, consider using PostgreSQL:

```python
# In src/main.py
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

## 📊 Monitoring Setup

### Health Checks

The platform includes built-in health check endpoints:

- `/api/health` - Basic health check
- `/api/system-health` - Comprehensive system metrics
- `/api/performance` - Performance metrics
- `/api/diagnostics` - System diagnostics

### Monitoring Integration

For production monitoring, integrate with:

1. **Prometheus** - Metrics collection
2. **Grafana** - Visualization
3. **ELK Stack** - Logging
4. **Uptime monitoring** - Service availability

Example Prometheus configuration:
```yaml
scrape_configs:
  - job_name: 'pricing-platform'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/api/performance'
```

## 🔒 Security Configuration

### SSL/TLS Setup

For production, enable HTTPS:

1. **Obtain SSL Certificate** (Let's Encrypt recommended)
2. **Configure Nginx** with SSL
3. **Update CORS settings** for HTTPS origins
4. **Set secure cookies** in Flask configuration

### Security Headers

Add security headers in Nginx:
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**:
   - Change ports in configuration files
   - Kill existing processes: `pkill -f python` or `pkill -f node`

2. **Database Errors**:
   - Check file permissions: `chmod 664 src/database/app.db`
   - Verify database initialization

3. **CORS Errors**:
   - Verify CORS configuration in Flask app
   - Check frontend API base URL

4. **Memory Issues**:
   - Monitor system resources: `/api/system-health`
   - Increase server memory if needed

### Debugging Commands

```bash
# Check running processes
ps aux | grep python
ps aux | grep node

# Check port usage
netstat -tulpn | grep :5001
netstat -tulpn | grep :5173

# View logs
tail -f /var/log/nginx/error.log
journalctl -u your-service-name -f

# Test API endpoints
curl http://localhost:5001/api/health
curl http://localhost:5001/api/stats
```

## 📈 Performance Optimization

### Backend Optimization

1. **Database Indexing**:
   ```sql
   CREATE INDEX idx_vehicle_vin ON vehicles(vin);
   CREATE INDEX idx_vehicle_make_model ON vehicles(make, model);
   ```

2. **Caching**:
   - Implement Redis for API response caching
   - Cache expensive calculations (scoring, matching)

3. **Connection Pooling**:
   - Configure SQLAlchemy connection pool
   - Use connection pooling for external APIs

### Frontend Optimization

1. **Code Splitting**:
   - Implement lazy loading for routes
   - Split large components

2. **Asset Optimization**:
   - Compress images and assets
   - Use CDN for static files

3. **Caching Strategy**:
   - Implement service worker
   - Cache API responses appropriately

## 🔄 Backup and Recovery

### Database Backup

```bash
# SQLite backup
cp src/database/app.db backups/app_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL backup
pg_dump pricing_platform > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Automated Backups

Create a backup script:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
cp /path/to/app.db "$BACKUP_DIR/db_$DATE.db"

# Configuration backup
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /path/to/config/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
```

## 📞 Support

### Getting Help

1. **Check System Health**: Visit `/api/diagnostics`
2. **Run Integration Tests**: `python3.11 tests/integration_tests.py`
3. **Review Logs**: Check application and system logs
4. **Monitor Resources**: Use `/api/system-health` endpoint

### Maintenance Tasks

1. **Regular Updates**:
   - Update Python dependencies: `pip install -r requirements.txt --upgrade`
   - Update Node.js dependencies: `pnpm update`

2. **Database Maintenance**:
   - Regular backups
   - Monitor database size and performance
   - Clean up old data if needed

3. **Security Updates**:
   - Keep system packages updated
   - Monitor security advisories
   - Regular security scans

## ✅ Deployment Checklist

- [ ] Prerequisites installed (Python 3.11+, Node.js 20+, pnpm)
- [ ] Backend virtual environment activated
- [ ] Dependencies installed (backend and frontend)
- [ ] Database initialized and populated
- [ ] Services started (backend on 5001, frontend on 5173)
- [ ] Integration tests passing (90%+ success rate)
- [ ] Health checks responding
- [ ] Dashboard accessible and functional
- [ ] API endpoints working
- [ ] Monitoring configured
- [ ] Security measures implemented
- [ ] Backup strategy in place
- [ ] Documentation reviewed

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ All services are running without errors
- ✅ Integration tests pass with 90%+ success rate
- ✅ Dashboard loads and displays data correctly
- ✅ API responses are under 100ms average
- ✅ System health shows "healthy" status
- ✅ Vehicle data is loaded (363+ vehicles)
- ✅ Matching and scoring functions work
- ✅ AI insights generate successfully

---

**Your Pricing Intelligence Platform is now ready for production use!**


# BourseChain - Sprint Review

**پروژه**: سامانه کارگزاری بورس آنلاین  
**دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲  
**تاریخ**: بهمن ۱۴۰۴  

---

## خلاصه تحویلی‌ها

### Sprint 1 ✅
- 10 صفحه (Login، Register، Dashboard، Market، StockDetail، Portfolio، Orders، Transactions، Notifications، Admin)
- Dark/Light theme، FA/EN دوزبانه، RTL
- shadcn-style UI components
- Recharts برای نمودارها

### Sprint 2 ✅
- 6 Django app: users، stocks، orders، transactions، notifications، blockchain_service
- 20+ API endpoint
- JWT authentication
- seed_data: 12 سهم، 7 کاربر
- Swagger در `/api/docs/`
- Frontend به API متصل

### Sprint 3 ✅
- Matching Engine در `orders/matching.py`
- Celery + RabbitMQ
- Cash/Stock reservation
- Partial fill، Cancel + Refund
- Notification دوزبانه بعد از match

### Sprint 4 ✅
- TransactionLedger.sol
- Hardhat + Web3.py
- Celery task برای on-chain record
- API `/blockchain/status/` و `/blockchain/verify/<uuid>/`
- 26 + 13 تست

### Sprint 5 ✅
- Django Channels + Daphne
- NotificationConsumer، StockPriceConsumer
- SIWE (nonce + verify)
- Frontend WebSocket با auto-reconnect
- Connect Wallet با MetaMask

### Sprint 6 ✅
- Docker Compose (9 سرویس)
- Kubernetes manifests (11 YAML)
- Prometheus + Grafana dashboard
- Terraform (VPC، EKS، RDS، ElastiCache، ECR)
- مستندات کامل

---

## آمار نهایی

| متریک | مقدار |
|-------|-------|
| تست Django | 150 |
| تست Hardhat | 13 |
| API Endpoints | 25+ |
| صفحات Frontend | 10 |
| فایل‌های K8s | 11 |
| فایل‌های مستندات | 10+ |

---

## Demo Checklist

- [x] http://localhost → اپلیکیشن
- [x] لاگین با ali@example.com / Test1234!
- [x] مشاهده سهام، ثبت سفارش، سبد
- [x] http://localhost/api/docs/ → Swagger
- [x] http://localhost:3000 → Grafana
- [x] http://localhost:9090 → Prometheus
- [x] docker compose ps → 9 container

---

## نتیجه

همه 6 Sprint طبق برنامه تحویل شدند. نیازمندی‌های اجباری و امتیازی (به جز Matching غیرمتمرکز) پیاده‌سازی شده‌اند.

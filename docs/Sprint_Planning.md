# BourseChain - Sprint Planning

**پروژه**: سامانه کارگزاری بورس آنلاین  
**دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲  
**تاریخ**: بهمن ۱۴۰۴  

---

## Sprint 1 - Frontend و UI

### هدف
ساخت فرانت‌اند React با تمام صفحات و Mock Data.

### User Stories
- [x] US1.1: صفحه لاگین و ثبت‌نام
- [x] US1.2: داشبورد با آمار کلی
- [x] US1.3: لیست سهام و جستجو
- [x] US1.4: جزئیات سهم با نمودار
- [x] US1.5: ثبت سفارش خرید/فروش
- [x] US1.6: سبد سهام و پرتفوی
- [x] US1.7: لیست سفارشات
- [x] US1.8: تراکنش‌ها
- [x] US1.9: اعلان‌ها
- [x] US1.10: پنل ادمین
- [x] US1.11: Dark/Light theme + FA/EN دوزبانه

### Definition of Done
- تمام صفحات با Mock Data render شوند
- RTL برای فارسی
- Responsive layout

---

## Sprint 2 - Backend API و Integration

### هدف
Django REST API، دیتابیس، اتصال فرانت به API.

### User Stories
- [x] US2.1: مدل User با JWT
- [x] US2.2: مدل Stock و PriceHistory
- [x] US2.3: مدل Order و PortfolioHolding
- [x] US2.4: مدل Transaction و Notification
- [x] US2.5: API endpoints برای auth، stocks، orders، transactions، notifications
- [x] US2.6: seed_data command
- [x] US2.7: Swagger docs
- [x] US2.8: Axios + JWT auto-refresh در فرانت

### Definition of Done
- 20+ API endpoint
- Frontend از API واقعی داده بگیرد
- تست‌های واحد

---

## Sprint 3 - Matching Engine و Order System

### هدف
الگوریتم matching، Celery، رزرو وجه/سهام.

### User Stories
- [x] US3.1: Matching Engine (Price-Time Priority)
- [x] US3.2: Celery برای match_order_task
- [x] US3.3: رزرو cash برای buy
- [x] US3.4: رزرو holdings برای sell
- [x] US3.5: Partial fill
- [x] US3.6: Cancel و refund
- [x] US3.7: Notification بعد از match

### Definition of Done
- Match اتوماتیک با سفارش مخالف
- test_matching command

---

## Sprint 4 - Blockchain Integration

### هدف
Smart Contract، Web3.py، ثبت تراکنش on-chain.

### User Stories
- [x] US4.1: TransactionLedger.sol
- [x] US4.2: Hardhat project
- [x] US4.3: BlockchainService با Web3.py
- [x] US4.4: Celery task برای record on-chain
- [x] US4.5: API verify transaction
- [x] US4.6: نمایش blockchain_hash در UI

### Definition of Done
- Match → on-chain record
- 26 Django + 13 Hardhat tests

---

## Sprint 5 - Real-time و SIWE

### هدف
WebSocket، اعلان لحظه‌ای، ورود با اتریوم.

### User Stories
- [x] US5.1: Django Channels + Daphne
- [x] US5.2: NotificationConsumer
- [x] US5.3: StockPriceConsumer
- [x] US5.4: SIWE nonce و verify
- [x] US5.5: Frontend WebSocket manager
- [x] US5.6: Connect Wallet در LoginPage

### Definition of Done
- WebSocket auto-reconnect
- SIWE با MetaMask

---

## Sprint 6 - DevOps و مستندات

### هدف
Docker، Kubernetes، Monitoring، Terraform، مستندات.

### User Stories
- [x] US6.1: Dockerfile برای backend، frontend، hardhat
- [x] US6.2: docker-compose.yml (9 سرویس)
- [x] US6.3: Kubernetes manifests
- [x] US6.4: Prometheus + Grafana
- [x] US6.5: Terraform (AWS)
- [x] US6.6: Risk Analysis، Vision، Test Plan
- [x] US6.7: Burndown، Incident Postmortem، Sprint Reports

### Definition of Done
- `docker compose up -d --build` کار کند
- مستندات کامل

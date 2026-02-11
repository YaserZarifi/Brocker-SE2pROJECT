# BourseChain - Test Plan & Test Cases

**پروژه**: سامانه کارگزاری بورس آنلاین  
**دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲  
**تاریخ**: بهمن ۱۴۰۴  

---

## ۱. استراتژی تست

### ۱.۱ سطوح تست

| سطح | ابزار | هدف |
|-----|-------|-----|
| Unit | pytest (Django) | تست مدل‌ها، منطق matching، سرویس‌ها |
| Integration | pytest | تست API endpoints، Celery tasks، WebSocket |
| Contract | Mocha/Chai | تست Smart Contract Solidity |
| E2E | دستی | تست flow کامل از UI |

### ۱.۲ پوشش تست

| جزئ | تعداد تست | وضعیت |
|-----|-----------|-------|
| orders | 47 | ✅ |
| blockchain_service | 26 | ✅ |
| users | 28 | ✅ |
| notifications | 23 | ✅ |
| stocks | 20 | ✅ |
| transactions | 8 | ✅ |
| contracts (Hardhat) | 13 | ✅ |
| **جمع** | **163** | ✅ |

---

## ۲. دستورات اجرای تست

```powershell
# همه تست‌های Django
cd backend
$env:USE_SQLITE="True"; $env:USE_LOCMEM_CACHE="True"
python manage.py test -v2

# تست هر اپ به صورت جدا
python manage.py test orders -v2
python manage.py test blockchain_service -v2
python manage.py test users -v2
python manage.py test notifications -v2
python manage.py test stocks -v2
python manage.py test transactions -v2

# تست Smart Contract
cd ../contracts
npx hardhat test

# تست داخل Docker
docker compose exec backend python manage.py test -v2
```

---

## ۳. Test Cases (نمونه)

### TC-001: ثبت سفارش خرید

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-001 |
| **شرح** | کاربر لاگین‌شده سفارش خرید با قیمت و تعداد معتبر ثبت می‌کند |
| **پیش‌شرط** | کاربر با موجودی کافی، سهم فعال |
| **ورودی** | `POST /api/v1/orders/create/` {stock_symbol: "SHPN", type: "buy", price: 5000, quantity: 100} |
| **خروجی مورد انتظار** | 201 Created، Order با status=pending |
| **وضعیت** | ✅ Pass |

### TC-002: Match سفارش خرید و فروش

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-002 |
| **شرح** | وقتی buy و sell با قیمت سازگار وجود دارد، Transaction ساخته می‌شود |
| **پیش‌شرط** | دو سفارش pending با قیمت match |
| **ورودی** | Celery task یا درخواست create order |
| **خروجی مورد انتظار** | Transaction، Order status=matched، Notification |
| **وضعیت** | ✅ Pass |

### TC-003: ورود SIWE با MetaMask

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-003 |
| **شرح** | کاربر با امضای EIP-4361 وارد می‌شود |
| **پیش‌شرط** | MetaMask نصب، nonce دریافت شده |
| **ورودی** | `POST /api/v1/auth/siwe/verify/` {message, signature} |
| **خروجی مورد انتظار** | 200، JWT tokens + user |
| **وضعیت** | ✅ Pass |

### TC-004: ثبت تراکنش روی بلاکچین

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-004 |
| **شرح** | بعد از match، تراکنش در TransactionLedger ثبت می‌شود |
| **پیش‌شرط** | Hardhat node بالا، contract deploy شده |
| **ورودی** | تراکنش match شده |
| **خروجی مورد انتظار** | Transaction.blockchain_hash پر شود |
| **وضعیت** | ✅ Pass |

### TC-005: WebSocket اعلان real-time

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-005 |
| **شرح** | بعد از match، notification به buyer و seller push می‌شود |
| **پیش‌شرط** | WebSocket متصل با JWT |
| **ورودی** | Match event |
| **خروجی مورد انتظار** | پیام JSON روی WebSocket |
| **وضعیت** | ✅ Pass |

### TC-006: لغو سفارش و برگشت وجه

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-006 |
| **شرح** | لغو سفارش pending باعث برگشت cash/stock رزرو شده می‌شود |
| **پیش‌شرط** | سفارش pending |
| **ورودی** | `PUT /api/v1/orders/<id>/cancel/` |
| **خروجی مورد انتظار** | 200، cash_balance/holdings برگشت |
| **وضعیت** | ✅ Pass |

### TC-007: Docker Compose بالا آمدن

| فیلد | مقدار |
|------|-------|
| **شناسه** | TC-007 |
| **شرح** | `docker compose up -d --build` همه سرویس‌ها را بالا می‌آورد |
| **پیش‌شرط** | Docker Desktop اجرا |
| **ورودی** | docker compose up -d --build |
| **خروجی مورد انتظار** | 9+ container running، http://localhost در دسترس |
| **وضعیت** | ✅ Pass |

---

## ۴. محیط تست

- **OS**: Windows 10/11
- **Python**: 3.12
- **Node**: 20
- **Django**: 5.2
- **Database**: SQLite (dev) / PostgreSQL (Docker)
- **Cache**: LocMem (dev) / Redis (Docker)

---

## ۵. معیارهای پذیرش

- [ ] 150 تست Django pass
- [ ] 13 تست Hardhat pass
- [ ] هیچ regression در تست‌های موجود
- [ ] Docker Compose در کمتر از ۵ دقیقه بالا بیاید

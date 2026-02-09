# BourseChain - پروژه کارگزاری بورس آنلاین

## اطلاعات پروژه
- **دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲
- **استاد**: دکتر گوهری
- **فایل نیازمندی‌ها**: `SE_PRJCT.pdf` (11 صفحه)
- **نام محصول**: BourseChain (بورس‌چین)
- **GitHub**: `https://github.com/YaserZarifi/Brocker-SE2pROJECT.git`

---

## خلاصه پروژه
یک **سامانه کارگزاری بورس آنلاین** با معماری **Modular Monolith** (Django apps جدا به عنوان میکروسرویس منطقی) که امکان خرید و فروش سهام را از طریق پلتفرمی شفاف و امن فراهم می‌کند. تراکنش‌ها روی **بلاکچین خصوصی EVM** ثبت می‌شوند.

---

## Tech Stack

| لایه | تکنولوژی | وضعیت |
|---|---|---|
| **Frontend** | React 19 + Vite 7 + TypeScript + Tailwind CSS v4 + shadcn-style UI | ✅ Sprint 1 |
| **UI Components** | Radix UI primitives + CVA + Tailwind (shadcn-style) | ✅ Sprint 1 |
| **State Management** | Zustand v5 | ✅ Sprint 1 |
| **Routing** | React Router v7 | ✅ Sprint 1 |
| **Charts** | Recharts v3 | ✅ Sprint 1 |
| **i18n** | i18next + react-i18next (FA/EN دوزبانه با RTL) | ✅ Sprint 1 |
| **Icons** | Lucide React | ✅ Sprint 1 |
| **HTTP Client** | Axios (JWT auto-refresh interceptor) | ✅ Sprint 2 |
| **Backend** | Django 5.2 + DRF 3.16 + simplejwt | ✅ Sprint 2 |
| **Database** | PostgreSQL (+ SQLite for dev) | ✅ Sprint 2 |
| **Cache/Session** | Redis (+ LocMem for dev) | ✅ Sprint 2 |
| **API Docs** | drf-spectacular (Swagger UI) | ✅ Sprint 2 |
| **Message Broker** | RabbitMQ (via Celery) | ⏳ Sprint 3 |
| **Blockchain** | Hardhat + Ethers.js + Solidity (ERC20/ERC1155) | ⏳ Sprint 4 |
| **Real-time** | Django Channels + WebSocket | ⏳ Sprint 5 |
| **Container** | Docker + Docker Compose | ⏳ Sprint 6 |
| **Orchestration** | Kubernetes manifests (فقط فایل‌ها) | ⏳ Sprint 6 |
| **Monitoring** | Prometheus + Grafana (config only) | ⏳ Sprint 6 |
| **IaC (امتیازی)** | Terraform | ⏳ Sprint 6 |
| **Login امتیازی** | SIWE (Sign-In with Ethereum) via EIP-4361 | ⏳ Sprint 5 |

---

## ساختار فعلی پروژه

```
d:\Amirkabir\SE2\Project\
├── CONTEXT.md               # ← این فایل
├── SE_PRJCT.pdf             # نیازمندی‌های پروژه
├── diagrams/                # دیاگرام‌های UML (✅ همه انجام شده)
│   ├── *.puml               # PlantUML source files
│   ├── EA/                  # Enterprise Architect diagrams (.png)
│   └── out/                 # Rendered SVGs
│
├── frontend/                # ✅ React Frontend (Sprint 1 + 2)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # shadcn-style: button, card, input, badge, tabs, tooltip, avatar, progress, separator, scroll-area
│   │   │   ├── layout/      # Sidebar, Header, MainLayout
│   │   │   └── common/      # ThemeToggle, LanguageToggle, Logo
│   │   ├── pages/           # LoginPage, RegisterPage, DashboardPage, MarketPage, StockDetailPage, PortfolioPage, OrdersPage, TransactionsPage, NotificationsPage, AdminPage
│   │   ├── stores/          # Zustand: authStore, themeStore, stockStore, notificationStore (← connected to API)
│   │   ├── services/
│   │   │   ├── api.ts           # Axios instance + JWT token management + auto-refresh interceptor
│   │   │   ├── authService.ts   # login, register, getProfile
│   │   │   ├── stockService.ts  # getStocks, getStock, getPriceHistory, getMarketStats
│   │   │   ├── orderService.ts  # getOrders, createOrder, cancelOrder, getPortfolio, getOrderBook
│   │   │   ├── transactionService.ts  # getTransactions
│   │   │   ├── notificationService.ts # getNotifications, markAsRead, markAllAsRead, getUnreadCount
│   │   │   └── mockData.ts      # Fallback generators: generatePriceHistory(), generateOrderBook()
│   │   ├── i18n/            # en.json + fa.json + index.ts
│   │   ├── types/           # TypeScript interfaces: User, Stock, Order, Transaction, Portfolio, Notification, OrderBook, PriceHistory, MarketStats
│   │   ├── lib/             # utils.ts (cn, formatPrice, formatNumber, formatPercent, getChangeColor, ...)
│   │   ├── router.tsx       # React Router config
│   │   ├── App.tsx          # Root component (checkAuth on load, fetchNotifications when authenticated)
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind v4 + CSS variables (dark/light themes)
│   ├── index.html
│   ├── vite.config.ts       # Vite + Tailwind + path aliases + proxy /api → localhost:8000
│   └── package.json
│
├── backend/                 # ✅ Django Backend (Sprint 2)
│   ├── config/              # Django project settings, urls, wsgi, asgi
│   │   └── settings.py      # PostgreSQL, Redis, JWT, CORS, Celery configs
│   ├── users/               # Custom User model (UUID PK, email login, JWT auth, role, wallet_address, cash_balance)
│   │   ├── models.py        # User(AbstractUser) with Role choices
│   │   ├── serializers.py   # UserSerializer, UserRegistrationSerializer, AdminUserSerializer
│   │   ├── views.py         # RegisterView, ProfileView, ChangePasswordView, AdminUserListView
│   │   └── urls.py          # /auth/login/, /auth/register/, /auth/refresh/, /auth/profile/, /auth/users/
│   ├── stocks/              # Stock + PriceHistory models
│   │   ├── models.py        # Stock (symbol, name, name_fa, prices, volume, sector, ...), PriceHistory (OHLCV)
│   │   ├── serializers.py   # StockSerializer (camelCase for frontend), PriceHistorySerializer, MarketStatsSerializer
│   │   ├── views.py         # StockListView, StockDetailView, StockPriceHistoryView, market_stats, AdminStockViews
│   │   ├── urls.py          # /stocks/, /stocks/stats/, /stocks/<symbol>/, /stocks/<symbol>/history/
│   │   └── management/commands/seed_data.py  # Seeds 12 stocks + users + orders + transactions + notifications
│   ├── orders/              # Order + PortfolioHolding models
│   │   ├── models.py        # Order (buy/sell, pending/matched/partial/cancelled/expired), PortfolioHolding
│   │   ├── serializers.py   # OrderSerializer, OrderCreateSerializer, PortfolioSerializer, OrderBookSerializer
│   │   ├── views.py         # OrderListView, OrderCreateView, OrderCancelView, portfolio_view, order_book_view
│   │   └── urls.py          # /orders/, /orders/create/, /orders/<id>/cancel/, /orders/portfolio/, /orders/book/<symbol>/
│   ├── transactions/        # Transaction model (matched buy+sell)
│   │   ├── models.py        # Transaction (buy_order, sell_order, stock, price, qty, blockchain_hash, status)
│   │   ├── serializers.py   # TransactionSerializer (camelCase)
│   │   ├── views.py         # TransactionListView, TransactionDetailView
│   │   └── urls.py          # /transactions/, /transactions/<id>/
│   ├── notifications/       # Notification model (bilingual FA/EN)
│   │   ├── models.py        # Notification (title, title_fa, message, message_fa, type, read)
│   │   ├── serializers.py   # NotificationSerializer (camelCase)
│   │   ├── views.py         # NotificationListView, mark_all_read, unread_count
│   │   └── urls.py          # /notifications/, /notifications/mark-all-read/, /notifications/unread-count/
│   ├── blockchain_service/  # Placeholder for Sprint 4
│   ├── requirements.txt     # Django 5, DRF, simplejwt, cors-headers, django-filter, psycopg2, redis, celery, Pillow, drf-spectacular
│   ├── manage.py
│   ├── .env.example
│   └── .gitignore
│
├── contracts/               # ⏳ Sprint 4 (Solidity)
├── docker/                  # ⏳ Sprint 6
├── k8s/                     # ⏳ Sprint 6
└── terraform/               # ⏳ Sprint 6
```

---

## اجرای پروژه (Development)

### Backend
```powershell
cd backend
# اگه venv نداری:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# اجرا با SQLite (بدون PostgreSQL/Redis):
$env:USE_SQLITE="True"
$env:USE_LOCMEM_CACHE="True"
python manage.py migrate
python manage.py seed_data          # 12 سهم + کاربران + سفارشات + تراکنش‌ها + اعلان‌ها
python manage.py runserver 8000     # → http://localhost:8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev     # → http://localhost:5173 (proxy /api → :8000)
```

### Test Users
| Email | Password | Role |
|---|---|---|
| `ali@example.com` | `Test1234!` | Customer |
| `admin@boursechain.ir` | `Admin1234!` | Admin |

---

## API Endpoints (Sprint 2)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/v1/auth/login/` | POST | No | JWT login (email + password) → {access, refresh} |
| `/api/v1/auth/register/` | POST | No | Register new user |
| `/api/v1/auth/refresh/` | POST | No | Refresh JWT token |
| `/api/v1/auth/profile/` | GET/PUT | Yes | User profile |
| `/api/v1/auth/change-password/` | PUT | Yes | Change password |
| `/api/v1/auth/users/` | GET | Admin | List all users |
| `/api/v1/auth/users/<uuid>/` | GET/PUT | Admin | User detail |
| `/api/v1/stocks/` | GET | No | List all stocks (camelCase response) |
| `/api/v1/stocks/stats/` | GET | No | Market statistics |
| `/api/v1/stocks/<symbol>/` | GET | No | Stock detail |
| `/api/v1/stocks/<symbol>/history/` | GET | No | Price history (?days=30) |
| `/api/v1/stocks/admin/manage/` | GET/POST | Admin | Admin stock management |
| `/api/v1/orders/` | GET | Yes | List user orders |
| `/api/v1/orders/create/` | POST | Yes | Create order {stock_symbol, type, price, quantity} |
| `/api/v1/orders/<uuid>/cancel/` | PUT | Yes | Cancel pending order |
| `/api/v1/orders/portfolio/` | GET | Yes | User portfolio + holdings + P&L |
| `/api/v1/orders/book/<symbol>/` | GET | No | Order book (aggregated bids/asks) |
| `/api/v1/transactions/` | GET | Yes | List user transactions |
| `/api/v1/transactions/<uuid>/` | GET | Yes | Transaction detail |
| `/api/v1/notifications/` | GET | Yes | List notifications |
| `/api/v1/notifications/<uuid>/` | GET/PATCH | Yes | Notification detail / mark read |
| `/api/v1/notifications/mark-all-read/` | POST | Yes | Mark all read |
| `/api/v1/notifications/unread-count/` | GET | Yes | Unread count |
| `/api/v1/blockchain/status/` | GET | No | Blockchain service status (placeholder) |
| `/api/docs/` | GET | No | Swagger UI documentation |
| `/api/schema/` | GET | No | OpenAPI schema |

---

## Frontend ↔ Backend Integration (Sprint 2)

### چگونه وصل شدن:
1. **Vite Proxy**: در `vite.config.ts` → `/api` proxy به `http://127.0.0.1:8000`
2. **Axios Client**: `frontend/src/services/api.ts` → JWT token در localStorage، auto-refresh interceptor
3. **Service Layer**: هر domain یه service file داره (authService, stockService, orderService, ...)
4. **Stores**: Zustand stores از service ها fetch می‌کنن (نه دیگه از mockData)
5. **Pages**: همه صفحات از store ها و service ها استفاده می‌کنن
6. **DRF Serializers**: camelCase field names برای frontend compatibility (مثلا `currentPrice` بجای `current_price`)

### Auth Flow:
1. User → POST `/auth/login/` (email, password) → {access, refresh}
2. Tokens ذخیره در localStorage
3. هر request → `Authorization: Bearer <access>` header
4. اگه 401 → auto-refresh با refresh token
5. اگه refresh هم fail → redirect به `/login`
6. `App.tsx` → `checkAuth()` on mount → اگه token داشت profile رو fetch کن

### Order Flow:
1. User → POST `/orders/create/` {stock_symbol, type:"buy"|"sell", price, quantity}
2. Backend validate: cash balance (buy) یا holdings (sell)
3. Order ساخته میشه با status=pending
4. ⏳ Sprint 3: Matching Engine اتوماتیک match می‌کنه

---

## نقشه‌راه Sprint‌ها

### ✅ Sprint 1 - Frontend (DONE)
- React + Vite + Tailwind + shadcn-style UI
- تمام 10 صفحه با Mock Data
- Dark/Light theme + FA/EN bilingual + RTL
- Real-time price simulation
- Charts (Area, Pie)

### ✅ Sprint 2 - Backend API + Database + Frontend Integration (DONE)
- Django project: 6 apps (users, stocks, orders, transactions, notifications, blockchain_service)
- PostgreSQL + Redis (+ SQLite/LocMem fallback)
- Django REST Framework: 20+ endpoints
- JWT authentication (simplejwt)
- seed_data command (12 سهم ایرانی + mock data)
- Swagger API docs (`/api/docs/`)
- Frontend: Axios + service layer + stores connected to API
- Vite proxy + JWT auto-refresh

### ⏳ Sprint 3 - Matching Engine + Order System (بعدی)
- Order matching algorithm (price-time priority)
- Celery + RabbitMQ for async processing
- وقتی buy و sell با قیمت مناسب وجود داره → اتوماتیک Transaction بسازه
- Order status updates (pending → matched/partial)
- Partial fill support
- آپدیت PortfolioHolding و cash_balance بعد از match
- ارسال Notification بعد از match

### ⏳ Sprint 4 - Blockchain Integration
- Hardhat project setup
- Solidity smart contracts (ERC20 for stock tokens, transaction ledger)
- Web3.py integration in Django
- Record transactions on-chain
- Transaction verification

### ⏳ Sprint 5 - Real-time + Bonus Features
- Django Channels + WebSocket for real-time notifications
- Live price updates via WebSocket
- SIWE (Sign-In with Ethereum) via EIP-4361
- MetaMask wallet integration on frontend

### ⏳ Sprint 6 - DevOps + Documentation
- Docker + Docker Compose for all services
- Kubernetes manifests
- Prometheus + Grafana config
- Terraform IaC (bonus)
- مستندات: Risk Analysis, Vision, Test Plan, Burndown, Incident Postmortem, Sprint Reports

---

## ویژگی‌های اصلی (از PDF نیازمندی‌ها)

### اجباری
1. ✅ مشاهده لیست سهام
2. ⏳ ثبت سفارش خرید/فروش + Matching Engine (Sprint 3)
3. ⏳ اعلان لحظه‌ای وضعیت سفارش‌ها - WebSocket (Sprint 5)
4. ⏳ ثبت تراکنش در بلاکچین خصوصی - EVM + Smart Contract (Sprint 4)
5. ✅ نمایش سبد سهام و وضعیت معاملات

### امتیازی
1. ⏳ ورود با اتریوم (SIWE - EIP-4361) (Sprint 5)
2. ⏳ Matching Engine غیرمتمرکز روی بلاکچین
3. ⏳ Infrastructure as Code - Terraform (Sprint 6)
4. ⏳ گزارش‌های Sprint

### مستندات مورد نیاز
1. سند تحلیل ریسک (Risk Analysis)
2. سند چشم‌انداز (Vision Document)
3. Test Plan + Test Cases
4. Burndown Chart
5. Incident Postmortem (3 سند)
6. Sprint reports (Planning, Review, Retrospective)

### نمودارهای UML (✅ همه انجام شده در `diagrams/`)
1. Use Case Diagram ✅
2. Class Diagram ✅
3. Sequence Diagram ✅
4. Activity Diagram ✅
5. Component Diagram ✅
6. Deployment Diagram ✅

---

## تصمیمات طراحی مهم

1. **Modular Monolith نه Full Microservice**: یک Django project با اپ‌های جدا. Docker فقط برای ارائه نهایی.
2. **Hardhat برای بلاکچین**: ساده‌ترین و مناسب‌ترین برای پروژه دانشگاهی. Local Ethereum node.
3. **RabbitMQ + Celery**: برای ارتباط غیرهمزمان بین سرویس‌ها (matching/اعلان).
4. **shadcn-style components**: کامپوننت‌ها دستی با Radix + CVA + Tailwind نوشته شدن.
5. **Dark mode پیش‌فرض**: مناسب پلتفرم مالی/بورسی.
6. **Font**: Inter (EN) + Vazirmatn (FA).
7. **camelCase API**: DRF serializers فیلدها رو camelCase برمی‌گردونن تا مستقیم با TypeScript types match بشن.
8. **SQLite/LocMem fallback**: برای dev بدون نیاز به PostgreSQL/Redis.

---

## نکات مهم برای ادامه کار

- **Sprint 3 بعدیه**: Matching Engine باید در `backend/orders/` ساخته بشه (Celery task)
- فایل `SE_PRJCT.pdf` را برای نیازمندی‌های دقیق هر بخش بخوان
- دیاگرام‌ها در `diagrams/` هستن (PlantUML + EA PNG)
- Backend virtual env: `backend/venv/` (در .gitignore هست)
- Database: `backend/db.sqlite3` (در .gitignore هست) - `python manage.py seed_data` برای rebuild
- Frontend mock data هنوز موجوده در `mockData.ts` به عنوان fallback (generatePriceHistory, generateOrderBook)
- همه صفحات فرانت الان به API واقعی وصلن (فقط price simulation هنوز client-side هست تا Sprint 5 WebSocket)

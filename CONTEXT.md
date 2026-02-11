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
| **Message Broker** | RabbitMQ (via Celery) + EAGER fallback for dev | ✅ Sprint 3 |
| **Blockchain** | Hardhat + Ethers.js + Solidity 0.8.24 + Web3.py 7 | ✅ Sprint 4 |
| **Real-time** | Django Channels + Daphne + WebSocket (InMemoryChannelLayer) | ✅ Sprint 5 |
| **Login امتیازی** | SIWE (Sign-In with Ethereum) via EIP-4361 + MetaMask + ethers.js | ✅ Sprint 5 |
| **Container** | Docker + Docker Compose (9 services) | ✅ Sprint 6 |
| **Orchestration** | Kubernetes manifests (11 YAML files) | ✅ Sprint 6 |
| **Monitoring** | Prometheus + Grafana (auto-provisioned dashboard) | ✅ Sprint 6 |
| **IaC (امتیازی)** | Terraform (AWS: VPC, EKS, RDS, ElastiCache, ECR) | ✅ Sprint 6 |

---

## ساختار فعلی پروژه

```
d:\Amirkabir\SE2\Project\
├── CONTEXT.md               # ← این فایل (برای چت جدید این رو بخون)
├── SE_PRJCT.pdf             # نیازمندی‌های پروژه
├── docs/                    # مستندات Sprint 6
│   ├── Risk_Analysis.md
│   ├── Vision_Document.md
│   ├── Test_Plan.md
│   ├── Burndown_Chart.md
│   ├── Incident_Postmortem_1.md, 2.md, 3.md
│   └── Sprint_Planning.md, Sprint_Review.md, Sprint_Retrospective.md
├── diagrams/                # دیاگرام‌های UML (✅ همه انجام شده)
│   ├── *.puml               # PlantUML source files
│   ├── EA/                  # Enterprise Architect diagrams (.png)
│   └── out/                 # Rendered SVGs
│
├── frontend/                # ✅ React Frontend (Sprint 1 + 2 + 5)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # shadcn-style: button, card, input, badge, tabs, tooltip, avatar, progress, separator, scroll-area
│   │   │   ├── layout/      # Sidebar, Header, MainLayout
│   │   │   └── common/      # ThemeToggle, LanguageToggle, Logo
│   │   ├── pages/           # LoginPage, RegisterPage, DashboardPage, MarketPage, StockDetailPage, PortfolioPage, OrdersPage, TransactionsPage, NotificationsPage, ProfilePage, AdminPage
│   │   ├── stores/          # Zustand: authStore, themeStore, stockStore, notificationStore (← connected to API + WebSocket)
│   │   ├── services/
│   │   │   ├── api.ts           # Axios instance + JWT token management + auto-refresh interceptor
│   │   │   ├── authService.ts   # login, register, getProfile, updateProfile, changePassword
│   │   │   ├── stockService.ts  # getStocks, getStock, getPriceHistory, getMarketStats
│   │   │   ├── orderService.ts  # getOrders, createOrder, cancelOrder, getPortfolio, getOrderBook
│   │   │   ├── transactionService.ts  # getTransactions
│   │   │   ├── notificationService.ts # getNotifications, markAsRead, markAllAsRead, getUnreadCount
│   │   │   ├── websocketService.ts    # ✅ Sprint 5: WebSocket manager (auto-reconnect, notification + stock channels)
│   │   │   ├── siweService.ts         # ✅ Sprint 5: SIWE MetaMask integration (connect, EIP-55 checksum, sign, verify)
│   │   │   └── mockData.ts      # Fallback generators: generatePriceHistory(), generateOrderBook()
│   │   ├── i18n/            # en.json + fa.json + index.ts
│   │   ├── types/           # TypeScript interfaces: User, Stock, Order, Transaction, Portfolio, Notification, OrderBook, PriceHistory, MarketStats
│   │   ├── lib/             # utils.ts (cn, formatPrice, getAvatarUrl, ...)
│   │   ├── router.tsx       # React Router config
│   │   ├── App.tsx          # Root component (checkAuth + WebSocket connect on load)
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind v4 + CSS variables (dark/light themes)
│   ├── index.html
│   ├── vite.config.ts       # Vite + Tailwind + path aliases + proxy /api, /media, /ws → :8000
│   └── package.json         # Dependencies incl. ethers (Sprint 5)
│
├── backend/                 # ✅ Django Backend (Sprint 2 + 3 + 4 + 5)
│   ├── config/              # Django project settings
│   │   ├── settings.py      # PostgreSQL, Redis, JWT, CORS, Celery, Blockchain, Channels, SIWE configs
│   │   ├── urls.py          # All API routes: auth, stocks, orders, transactions, notifications, blockchain
│   │   ├── asgi.py          # ✅ Sprint 5: ASGI application (HTTP + WebSocket routing via ProtocolTypeRouter)
│   │   ├── routing.py       # ✅ Sprint 5: WebSocket URL routing (/ws/notifications/, /ws/stocks/)
│   │   ├── ws_auth.py       # ✅ Sprint 5: JWT WebSocket authentication middleware (query param token)
│   │   ├── wsgi.py          # WSGI (unused when Daphne runs)
│   │   ├── celery.py        # ✅ Sprint 3: Celery app configuration
│   │   └── __init__.py      # ✅ Sprint 3: Celery app auto-import
│   ├── users/               # Custom User model (UUID PK, email login, JWT auth, role, wallet_address, cash_balance)
│   │   ├── models.py        # User(AbstractUser) with Role choices, USERNAME_FIELD="email"
│   │   ├── serializers.py   # UserSerializer (first_name, last_name, avatar), UserUpdateSerializer, AdminUserSerializer
│   │   ├── views.py         # RegisterView, ProfileView, ChangePasswordView, AdminUserListView
│   │   ├── siwe_views.py    # ✅ Sprint 5: SIWE nonce + verify endpoints (uses `siwe` library + eth_utils)
│   │   ├── tests.py         # 28 tests (incl. 10 SIWE tests)
│   │   └── urls.py          # /auth/login/, /auth/register/, /auth/refresh/, /auth/profile/, /auth/siwe/nonce/, /auth/siwe/verify/, /auth/users/
│   ├── stocks/              # Stock + PriceHistory models + WebSocket
│   │   ├── models.py        # Stock (symbol, name, name_fa, prices, volume, sector, is_active, ...), PriceHistory (OHLCV)
│   │   ├── serializers.py   # StockSerializer (camelCase for frontend), PriceHistorySerializer, MarketStatsSerializer
│   │   ├── views.py         # StockListView, StockDetailView, StockPriceHistoryView, market_stats, AdminStockViews
│   │   ├── consumers.py     # ✅ Sprint 5: StockPriceConsumer (AsyncJsonWebsocketConsumer, group="stock_prices")
│   │   ├── utils.py         # ✅ Sprint 5: broadcast_stock_price() → async_to_sync channel_layer.group_send
│   │   ├── tests.py         # 20 tests (incl. 6 WebSocket tests)
│   │   ├── urls.py          # /stocks/, /stocks/stats/, /stocks/<symbol>/, /stocks/<symbol>/history/
│   │   └── management/commands/seed_data.py  # Seeds 12 stocks + 7 users + orders + transactions + notifications
│   ├── orders/              # Order + PortfolioHolding models + Matching Engine
│   │   ├── models.py        # Order (buy/sell, pending/matched/partial/cancelled/expired), PortfolioHolding
│   │   ├── matching.py      # ✅ Sprint 3+4+5: Price-Time Priority Matching + blockchain on_commit + WS broadcast
│   │   ├── tasks.py         # ✅ Sprint 3: Celery tasks (match_order_task, match_all_pending_task)
│   │   ├── serializers.py   # OrderSerializer, OrderCreateSerializer, PortfolioSerializer, OrderBookSerializer
│   │   ├── views.py         # OrderListView, OrderCreateView (cash/stock reservation), OrderCancelView (refund), portfolio_view, order_book_view
│   │   ├── tests.py         # 47 tests
│   │   ├── urls.py          # /orders/, /orders/create/, /orders/<id>/cancel/, /orders/portfolio/, /orders/book/<symbol>/
│   │   └── management/commands/test_matching.py  # Test command for matching engine (5 scenarios)
│   ├── transactions/        # Transaction model (matched buy+sell)
│   │   ├── models.py        # Transaction (buy_order, sell_order, stock, price, qty, blockchain_hash, status)
│   │   ├── serializers.py   # TransactionSerializer (camelCase, includes blockchainHash)
│   │   ├── views.py         # TransactionListView, TransactionDetailView
│   │   ├── tests.py         # 8 tests
│   │   └── urls.py          # /transactions/, /transactions/<id>/
│   ├── notifications/       # Notification model (bilingual FA/EN) + WebSocket
│   │   ├── models.py        # Notification (title, title_fa, message, message_fa, type, read)
│   │   ├── serializers.py   # NotificationSerializer (camelCase)
│   │   ├── views.py         # NotificationListView, mark_all_read, unread_count
│   │   ├── consumers.py     # ✅ Sprint 5: NotificationConsumer (AsyncJsonWebsocketConsumer, JWT auth, per-user groups)
│   │   ├── utils.py         # ✅ Sprint 5: broadcast_notification() → async_to_sync channel_layer.group_send
│   │   ├── tests.py         # 23 tests (incl. 7 WebSocket tests)
│   │   └── urls.py          # /notifications/, /notifications/mark-all-read/, /notifications/unread-count/
│   ├── blockchain_service/  # ✅ Sprint 4: Web3.py + TransactionLedger contract integration
│   │   ├── apps.py          # BlockchainServiceConfig
│   │   ├── service.py       # BlockchainService singleton: connect, record_transaction, verify_transaction, deploy_contract
│   │   ├── tasks.py         # Celery task: record_transaction_on_blockchain (fires via on_commit after match)
│   │   ├── views.py         # API: blockchain_status (public), verify_transaction (auth required)
│   │   ├── urls.py          # /blockchain/status/, /blockchain/verify/<uuid>/
│   │   ├── models.py        # No models (address in contract_address.json, hash on Transaction model)
│   │   ├── tests.py         # 26 tests (service, task, API, matching integration)
│   │   ├── contract_address.json  # ← auto-generated by deploy_contract (in .gitignore)
│   │   └── management/commands/deploy_contract.py  # Deploy TransactionLedger via Web3.py
│   ├── requirements.txt     # Django 5, DRF, simplejwt, cors-headers, django-filter, psycopg2, redis, celery, Pillow, drf-spectacular, web3, channels[daphne], siwe
│   ├── manage.py
│   ├── .env.example
│   └── .gitignore
│
├── contracts/               # ✅ Sprint 4 (Hardhat + Solidity)
│   ├── package.json         # hardhat + @nomicfoundation/hardhat-toolbox
│   ├── hardhat.config.js    # Solidity 0.8.24, optimizer on, localhost:8545
│   ├── contracts/
│   │   └── TransactionLedger.sol  # On-chain trade ledger (recordTrade, verifyTrade, getTrade, getAllTradeIds)
│   ├── scripts/
│   │   └── deploy.js        # Deploy script (saves address to Django's contract_address.json)
│   ├── test/
│   │   └── TransactionLedger.test.js  # 13 Mocha/Chai tests
│   └── .gitignore           # node_modules, artifacts, cache, deployments
├── docker-compose.yml          # ✅ Sprint 6: Full-stack Docker orchestration
├── .dockerignore               # ✅ Sprint 6: Docker build exclusions
│
├── docker/                     # ✅ Sprint 6: Docker configurations
│   ├── backend/
│   │   ├── Dockerfile          # Python 3.12 + Daphne ASGI
│   │   └── entrypoint.sh      # Wait for deps + migrate + collectstatic
│   ├── frontend/
│   │   ├── Dockerfile          # Multi-stage: Node build → Nginx serve
│   │   └── nginx.conf          # Reverse proxy (API + WebSocket + SPA + /media برای آواتار)
│   ├── hardhat/
│   │   └── Dockerfile          # Hardhat compile + node
│   ├── prometheus/
│   │   └── prometheus.yml      # Scrape config (django-prometheus)
│   └── grafana/
│       ├── provisioning/       # Auto-provision datasource + dashboard
│       └── dashboards/
│           └── boursechain.json # Request rate, latency, errors, DB queries
│
├── k8s/                        # ✅ Sprint 6: Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── postgres.yaml           # Deployment + Service + PVC
│   ├── redis.yaml              # Deployment + Service
│   ├── rabbitmq.yaml           # Deployment + Service
│   ├── hardhat.yaml            # Deployment + Service
│   ├── backend.yaml            # Deployment + Service (2 replicas, init: migrate)
│   ├── celery.yaml             # Deployment (worker)
│   ├── frontend.yaml           # Deployment + Service (2 replicas)
│   └── ingress.yaml            # Nginx Ingress (API/WS→backend, /→frontend)
│
└── terraform/                  # ✅ Sprint 6: AWS IaC
    ├── provider.tf             # AWS + Kubernetes providers
    ├── variables.tf            # All input variables
    ├── main.tf                 # VPC, EKS, RDS, ElastiCache, ECR, Security Groups
    ├── outputs.tf              # Connection strings, endpoints
    ├── terraform.tfvars.example
    └── modules/
        └── eks/                # EKS cluster + node group module
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
python manage.py seed_data          # 12 سهم + 7 کاربر + سفارشات + تراکنش‌ها + اعلان‌ها
python manage.py runserver 8000     # → http://localhost:8000 (Daphne ASGI - HTTP + WebSocket)
```

### Frontend
```powershell
cd frontend
npm install
npm run dev     # → http://localhost:5173 (proxy /api → :8000, /ws → ws://:8000)
```

### Docker (Sprint 6 - یکجا همه سرویس‌ها)
```powershell
cd Project
docker compose up -d --build          # Build + Start all 9 services
# صبر کن setup service تموم بشه (deploy contract + seed data):
docker compose logs -f setup
# بعد از اتمام:
#   Frontend → http://localhost         (Nginx → React SPA)
#   Backend  → http://localhost:8001    (Daphne ASGI - پورت 8001 برای جلوگیری از تداخل)
#   Swagger  → http://localhost/api/docs/
#   Grafana  → http://localhost:3000    (admin / boursechain)
#   Prometheus → http://localhost:9090
#   RabbitMQ → http://localhost:15672   (guest / guest)
#   Hardhat  → http://localhost:8545

docker compose down                   # Stop all
docker compose down -v                # Stop + remove volumes (fresh start)

# ایران: imageها از docker.arvancloud.ir (محدودیت Docker Hub)
# دستورات مفید:
#   docker compose ps -a              # وضعیت همه
#   docker compose logs -f backend    # لاگ زنده
#   docker compose exec backend python manage.py test -v2
#   docker compose restart backend    # Restart یک سرویس
#   docker compose up -d --build      # بعد از تغییر کد
```

### Kubernetes (Sprint 6)
```powershell
# با minikube:
minikube start
minikube addons enable ingress

# Apply all manifests:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Check status:
kubectl get all -n boursechain

# Access:
echo "$(minikube ip) boursechain.local" | Add-Content C:\Windows\System32\drivers\etc\hosts
# → http://boursechain.local
```

### Terraform (Sprint 6 - AWS)
```powershell
cd terraform
cp terraform.tfvars.example terraform.tfvars
# ویرایش terraform.tfvars (password و region)
terraform init
terraform plan
terraform apply
```

### Blockchain (Sprint 4)
```powershell
# Terminal 1 - Hardhat Node:
cd contracts
npm install
npx hardhat compile                          # Compile Solidity
npx hardhat node                             # Start local node → http://localhost:8545

# Terminal 2 - Deploy:
cd backend
.\venv\Scripts\activate
$env:USE_SQLITE="True"; $env:USE_LOCMEM_CACHE="True"
python manage.py deploy_contract             # Deploy TransactionLedger → saves address
# حالا matching engine اتوماتیک تراکنش‌ها رو on-chain ثبت می‌کنه!
```

### Test Users (seed_data)
| Email | Password | Role | توضیح |
|---|---|---|---|
| `ali@example.com` | `Test1234!` | Customer | کاربر اصلی، دارای سفارشات و holdings |
| `admin@boursechain.ir` | `Admin1234!` | Admin | ادمین سیستم |
| `user042@example.com` | `Test1234!` | Customer | Sara Mohammadi |
| `user015@example.com` | `Test1234!` | Customer | Reza Ahmadi |
| `user088@example.com` | `Test1234!` | Customer | Maryam Hosseini |
| `user033@example.com` | `Test1234!` | Customer | Hassan Karimi |
| `user077@example.com` | `Test1234!` | Customer | Zahra Bahrami |

### Pending Orders در Seed Data (آماده match)
| کاربر | سهم | نوع | قیمت | تعداد |
|---|---|---|---|---|
| `ali@example.com` | SHPN (شپنا) | sell | 4,350 | 300 |
| `ali@example.com` | PTRO (پترول) | buy | 5,400 | 400 |

برای تست match: با یکی از کاربرهای دیگه لاگین کن و سفارش مخالف ثبت کن.

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/v1/auth/login/` | POST | No | JWT login (email + password) → {access, refresh} |
| `/api/v1/auth/register/` | POST | No | Register new user |
| `/api/v1/auth/refresh/` | POST | No | Refresh JWT token |
| `/api/v1/auth/profile/` | GET/PATCH | Yes | User profile (first_name, last_name, username, wallet_address, avatar) |
| `/api/v1/auth/change-password/` | PUT | Yes | Change password |
| `/api/v1/auth/siwe/nonce/` | GET | No | Get SIWE nonce for Ethereum login |
| `/api/v1/auth/siwe/verify/` | POST | No | Verify SIWE signature → JWT tokens + user |
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
| `/api/v1/blockchain/status/` | GET | No | Blockchain node status (chain, block, contract, tradeCount) |
| `/api/v1/blockchain/verify/<uuid>/` | GET | Yes | Verify transaction on-chain (returns stockSymbol, price, qty, timestamp) |
| `/api/docs/` | GET | No | Swagger UI documentation |
| `/api/schema/` | GET | No | OpenAPI schema |

### WebSocket Endpoints (Sprint 5)

| Endpoint | Auth | Description |
|---|---|---|
| `ws://host/ws/notifications/?token=<jwt>` | Yes | Real-time notifications (per-user group) |
| `ws://host/ws/stocks/` | No | Real-time stock price updates (broadcast to all) |

---

## Frontend ↔ Backend Integration

### چگونه وصل شدن:
1. **Vite Proxy**: در `vite.config.ts` → `/api` proxy به `http://127.0.0.1:8000` و `/ws` proxy به `ws://127.0.0.1:8000`
2. **Axios Client**: `frontend/src/services/api.ts` → JWT token در localStorage، auto-refresh interceptor
3. **Service Layer**: هر domain یه service file داره (authService, stockService, orderService, siweService, websocketService, ...)
4. **Stores**: Zustand stores از service ها fetch می‌کنن + WebSocket real-time updates
5. **Pages**: همه صفحات از store ها و service ها استفاده می‌کنن
6. **DRF Serializers**: camelCase field names برای frontend compatibility (مثلا `currentPrice` بجای `current_price`)

### Auth Flow:
1. User → POST `/auth/login/` (email, password) → {access, refresh}
2. Tokens ذخیره در localStorage
3. هر request → `Authorization: Bearer <access>` header
4. اگه 401 → auto-refresh با refresh token
5. اگه refresh هم fail → redirect به `/login`
6. `App.tsx` → `checkAuth()` on mount → اگه token داشت profile رو fetch کن
7. **SIWE Alternative (Sprint 5)**: MetaMask → nonce → EIP-4361 sign → verify → JWT tokens

### SIWE Flow (Sprint 5):
1. User کلیک روی "Connect Wallet" در LoginPage
2. MetaMask باز میشه → `eth_requestAccounts` → آدرس wallet
3. آدرس با `ethers.getAddress()` به فرمت EIP-55 checksum تبدیل میشه
4. Frontend → GET `/auth/siwe/nonce/` → nonce دریافت
5. ساخت EIP-4361 message (domain, address, statement, URI, nonce, issuedAt)
6. MetaMask → `personal_sign` → امضای پیام
7. Frontend → POST `/auth/siwe/verify/` {message, signature}
8. Backend: `siwe` library → verify → find/create user → JWT tokens
9. Frontend: tokens ذخیره + redirect به Dashboard

### Order Flow (Sprint 3 + 4 + 5 - Complete):
1. User → POST `/orders/create/` {stock_symbol, type:"buy"|"sell", price, quantity}
2. Backend validate: cash balance (buy) یا holdings (sell)
3. **Cash/Stock Reservation**: پول (buy) یا سهام (sell) فوراً کسر میشه
4. Order ساخته میشه با status=pending
5. **Celery Task**: `match_order_task` اتوماتیک trigger میشه
6. **Matching Engine** (`orders/matching.py`):
   - Buy: پیدا کردن sell orders با price <= buy_price (ارزان‌ترین اول)
   - Sell: پیدا کردن buy orders با price >= sell_price (گران‌ترین اول)
   - Execution price = قیمت maker (سفارشی که زودتر ثبت شده)
7. برای هر match:
   - Transaction ساخته میشه (status=confirmed)
   - filled_quantity و status آپدیت میشه
   - پول به فروشنده منتقل میشه
   - سهام به خریدار منتقل میشه (با weighted average price)
   - قیمت سهم و volume آپدیت میشه
   - Notification دوزبانه به هر دو طرف
8. **WebSocket Push (Sprint 5)**: بعد از DB commit:
   - `_schedule_ws_notification()` → notification push به buyer و seller
   - `_schedule_ws_stock_update()` → stock price broadcast به همه clients
9. **Blockchain (Sprint 4)**: بعد از commit شدن DB transaction:
   - `on_commit` → `record_transaction_on_blockchain.delay(tx_id)`
   - Celery task تراکنش رو روی بلاکچین خصوصی ثبت می‌کنه
   - `Transaction.blockchain_hash` آپدیت میشه
   - اگه Hardhat node بالا نباشه، match کار می‌کنه ولی `blockchain_hash` خالی می‌مونه
10. **Cancel**: لغو سفارش → برگشت پول/سهام رزرو شده (فقط بخش fill نشده)

### Blockchain Flow (Sprint 4):
1. `_execute_match()` در matching.py → `_schedule_blockchain_recording(tx)`
2. `db_transaction.on_commit()` → `record_transaction_on_blockchain.delay(tx_id)`
3. Celery task: `BlockchainService.record_transaction(tx)` → Web3.py
4. UUID → bytes16، قیمت/تعداد → uint256
5. `TransactionLedger.recordTrade()` → emit `TradeRecorded` event
6. `receipt.transactionHash` → `Transaction.blockchain_hash`
7. Verify: `TransactionLedger.verifyTrade(tx_id)` → (exists, timestamp)

### WebSocket Flow (Sprint 5):
1. **App.tsx mount** → `connectStockWs()` (public, بدون auth)
2. **isAuthenticated تغییر** → `connectNotificationWs()` (با JWT token)
3. **Notification Consumer**: client → `/ws/notifications/?token=<jwt>` → join group `notifications_{user_id}`
4. **Stock Consumer**: client → `/ws/stocks/` → join group `stock_prices`
5. **Match event** → `_schedule_ws_notification(notif)` → `on_commit` → `broadcast_notification(notif)` → channel_layer.group_send
6. **Match event** → `_schedule_ws_stock_update(stock)` → `on_commit` → `broadcast_stock_price(stock)` → channel_layer.group_send
7. **Consumer** دریافت → `send_json` → WebSocket → Frontend store update (real-time UI)
8. **Logout** → `wsManager.disconnectAll()`

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
- seed_data command (12 سهم ایرانی + 7 کاربر + mock data)
- Swagger API docs (`/api/docs/`)
- Frontend: Axios + service layer + stores connected to API
- Vite proxy + JWT auto-refresh

### ✅ Sprint 3 - Matching Engine + Order System (DONE)
- Order matching algorithm (price-time priority) → `orders/matching.py`
- Celery + RabbitMQ for async processing → `orders/tasks.py` + `config/celery.py`
- Dev fallback: `CELERY_TASK_ALWAYS_EAGER=True` (auto-enabled with USE_SQLITE)
- وقتی buy و sell با قیمت مناسب وجود داره → اتوماتیک Transaction ساخته میشه
- Order status updates (pending → matched/partial)
- Partial fill support (یک سفارش بزرگ با چندین سفارش کوچک match میشه)
- Cash reservation: پول خریدار موقع ثبت سفارش کسر و موقع لغو برگشت داده میشه
- Stock reservation: سهام فروشنده موقع ثبت سفارش کسر و موقع لغو برگشت داده میشه
- آپدیت PortfolioHolding (weighted avg price) و cash_balance بعد از match
- آپدیت قیمت سهم و حجم معاملات بعد از هر match
- ارسال Notification دوزبانه (FA/EN) بعد از match به هر دو طرف
- Order Book view: نمایش مقدار باقی‌مانده (remaining) بجای کل
- Management command: `python manage.py test_matching` (5 scenario test)

### ✅ Sprint 4 - Blockchain Integration (DONE)
- **Hardhat project**: `contracts/` → package.json, hardhat.config.js, Solidity 0.8.24
- **Smart Contract**: `TransactionLedger.sol`
  - `recordTrade(bytes16 txId, string symbol, uint256 price, uint256 qty, uint256 total, bytes16 buyerId, bytes16 sellerId)` → onlyOwner
  - `verifyTrade(bytes16 txId)` → (bool exists, uint256 timestamp)
  - `getTrade(bytes16 txId)` → full trade data
  - `getAllTradeIds()` → bytes16[]
  - `TradeRecorded` event
- **Web3.py Service**: `blockchain_service/service.py` → BlockchainService singleton
  - Lazy init، non-blocking (هرگز matching engine رو block نمی‌کنه)
  - اگه Hardhat بالا نباشه gracefully handle می‌کنه
  - Contract ABI از `contracts/artifacts/` خونده میشه
  - Contract address از `contract_address.json` خونده میشه
- **Celery Task**: `record_transaction_on_blockchain` → fires via `on_commit` after each match
- **Management Command**: `python manage.py deploy_contract` → deploy via Web3.py
- **API Endpoints**: `/blockchain/status/` (public), `/blockchain/verify/<uuid>/` (auth)
- **Frontend**: صفحه Transactions هش بلاکچین truncated نمایش میده (0x71aa...e570)
- **Settings**: `BLOCKCHAIN_ENABLED`, `BLOCKCHAIN_RPC_URL`, `BLOCKCHAIN_PRIVATE_KEY` (Hardhat account #0)
- **تست‌ها**: 26 Django + 13 Hardhat/Mocha = 39 تست جدید
- **End-to-End تأیید شده**: match → on-chain record → blockchain_hash saved → verify confirmed

### ✅ Sprint 5 - Real-time + Bonus Features (DONE)
- **Django Channels + WebSocket**: Real-time notifications and stock price updates
  - `daphne` در INSTALLED_APPS → `manage.py runserver` اتوماتیک ASGI server (Daphne) اجرا می‌کنه
  - `notifications/consumers.py` → NotificationConsumer (AsyncJsonWebsocketConsumer, JWT auth, per-user groups)
  - `stocks/consumers.py` → StockPriceConsumer (AsyncJsonWebsocketConsumer, public, shared group)
  - `config/ws_auth.py` → JWTAuthMiddleware (JWT از query string: `?token=<jwt>`)
  - `config/routing.py` → WebSocket URL routing (`/ws/notifications/`, `/ws/stocks/`)
  - `config/asgi.py` → ProtocolTypeRouter (HTTP → Django, WebSocket → Channels)
  - `CHANNEL_LAYERS` → InMemoryChannelLayer (dev, بدون Redis)
- **WebSocket integration in Matching Engine** (`orders/matching.py`):
  - `_schedule_ws_notification()` → after match: notification push via `on_commit`
  - `_schedule_ws_stock_update()` → after match: stock price broadcast via `on_commit`
  - `notifications/utils.py` → `broadcast_notification()` (async_to_sync → channel_layer.group_send)
  - `stocks/utils.py` → `broadcast_stock_price()` (async_to_sync → channel_layer.group_send)
- **SIWE (Sign-In with Ethereum) - EIP-4361**:
  - `users/siwe_views.py` → `siwe_nonce()` GET + `siwe_verify()` POST
  - Uses `siwe` Python library for message parsing + verification
  - One-time nonce (cached 5 min, deleted after use) to prevent replay attacks
  - Auto-creates user with wallet_address on first SIWE login (`_get_or_create_siwe_user`)
  - Returns JWT tokens (same as normal login) + user profile
- **Frontend WebSocket**:
  - `services/websocketService.ts` → WebSocketManager singleton (auto-reconnect, exponential backoff)
  - `stores/notificationStore.ts` → `connectWebSocket()` / `addNotification()` from WS
  - `stores/stockStore.ts` → `connectWebSocket()` / `updateStockPrice()` from WS (replaced client-side simulation)
  - `App.tsx` → connects stock WS on mount + notification WS when authenticated
  - `vite.config.ts` → proxy `/ws` → `ws://127.0.0.1:8000`
- **Frontend SIWE**:
  - `services/siweService.ts` → MetaMask integration (connectWallet, EIP-55 checksum via `getAddress()`, createSiweMessage, signMessage)
  - `stores/authStore.ts` → `loginWithEthereum()` real SIWE flow (replaces mock)
  - `pages/LoginPage.tsx` → "Connect Wallet" button with MetaMask detection
  - Installed `ethers` for MetaMask/signing + EIP-55 address conversion
- **تست‌ها**: 21 تست جدید (150 Django total)
  - WebSocket notification consumer: auth connect, reject unauthenticated, reject invalid token, receive broadcast
  - WebSocket stock consumer: public connect, receive price update, multi-client broadcast
  - SIWE: get nonce, nonce cached, nonce unique, verify valid signature, create user, existing wallet user, invalid signature, missing fields, expired nonce, fake nonce
  - Broadcast utilities: no-raise guarantee

### ✅ Sprint 6 - DevOps + Infrastructure (DONE)
- **Docker + Docker Compose**: 9 services (backend, celery, frontend, postgres, redis, rabbitmq, hardhat, prometheus, grafana) + setup service
  - Backend: Python 3.12 + Daphne ASGI + entrypoint.sh (wait→migrate→collectstatic→start)
  - Frontend: Multi-stage (Node build → Nginx) + reverse proxy (API/WS/admin/metrics)
  - Hardhat: Compile + persistent local Ethereum node
  - `docker compose up -d --build` → همه سرویس‌ها بالا می‌آد!
- **Kubernetes manifests**: 11 YAML files
  - Namespace, ConfigMap, Secret (base64)
  - PostgreSQL (Deployment + Service + PVC 5Gi)
  - Redis, RabbitMQ, Hardhat (Deployment + Service)
  - Backend (2 replicas, init container: migrate, readiness/liveness probes)
  - Celery Worker (liveness: celery inspect ping)
  - Frontend (2 replicas, Nginx health check)
  - Ingress (Nginx Ingress Controller: /api,/ws→backend, /→frontend)
- **Monitoring**: Prometheus + Grafana
  - `django-prometheus` middleware → `/metrics` endpoint (request rate, latency, status codes, DB queries)
  - Prometheus scrape config (15s interval)
  - Grafana auto-provisioned dashboard (8 panels: health, request rate, latency p50/95/99, status codes, DB queries, top views)
  - Grafana: http://localhost:3000 (admin/boursechain)
- **Terraform IaC** (AWS - امتیازی):
  - VPC + public/private subnets + NAT Gateway
  - EKS cluster + managed node group (auto-scaling)
  - RDS PostgreSQL 16 (private subnet, multi-AZ in prod)
  - ElastiCache Redis 7.1 (private subnet)
  - ECR repositories (backend, frontend, hardhat)
  - Security Groups (EKS↔RDS, EKS↔Redis)
  - Region: me-south-1 (Bahrain - نزدیک‌ترین به ایران)
- **Backend Updates**:
  - `whitenoise` middleware → static files in production
  - `django-prometheus` → request/DB metrics at `/metrics`
  - `channels-redis` → Redis Channel Layer in production (InMemory in dev)
  - `/health/` endpoint → Docker/K8s health checks
- ✅ مستندات: Risk Analysis, Vision, Test Plan, Burndown, Incident Postmortem (3), Sprint Reports (Planning, Review, Retrospective) → `docs/`

---

## ویژگی‌های اصلی (از PDF نیازمندی‌ها)

### اجباری
1. ✅ مشاهده لیست سهام
2. ✅ ثبت سفارش خرید/فروش + Matching Engine (Sprint 3)
3. ✅ اعلان لحظه‌ای وضعیت سفارش‌ها - WebSocket (Sprint 5)
4. ✅ ثبت تراکنش در بلاکچین خصوصی - EVM + Smart Contract (Sprint 4)
5. ✅ نمایش سبد سهام و وضعیت معاملات

### امتیازی
1. ✅ ورود با اتریوم (SIWE - EIP-4361) (Sprint 5)
2. ⏳ Matching Engine غیرمتمرکز روی بلاکچین
3. ✅ Infrastructure as Code - Terraform (Sprint 6)
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
4. **Django Channels + Daphne**: برای WebSocket support. Daphne جایگزین WSGI server شده.
5. **shadcn-style components**: کامپوننت‌ها دستی با Radix + CVA + Tailwind نوشته شدن.
6. **Dark mode پیش‌فرض**: مناسب پلتفرم مالی/بورسی.
7. **Font**: Inter (EN) + Vazirmatn (FA).
8. **camelCase API**: DRF serializers فیلدها رو camelCase برمی‌گردونن تا مستقیم با TypeScript types match بشن.
9. **SQLite/LocMem/InMemoryChannelLayer fallback**: برای dev بدون نیاز به PostgreSQL/Redis.
10. **Non-blocking blockchain + WebSocket**: ثبت on-chain و WS broadcast هر دو بعد از DB commit (via `on_commit`). هرگز matching engine رو block نمی‌کنن.
11. **Hardhat Account #0**: private key معروف (`0xac09...`) فقط برای dev. هیچ ارزش واقعی نداره.
12. **EIP-55 checksum**: MetaMask آدرس lowercase برمیگردونه، `ethers.getAddress()` در frontend آدرس رو به checksum تبدیل میکنه قبل از ارسال به backend (مورد نیاز `siwe` library).

---

## تست‌ها (Sprint 5 - 150 Django + 13 Hardhat = 163 تست)

### اجرا
```powershell
cd backend
.\venv\Scripts\activate
$env:USE_SQLITE="True"; $env:USE_LOCMEM_CACHE="True"
python manage.py test -v2                    # همه 150 تست Django
python manage.py test users -v2             # تست‌های User + SIWE
python manage.py test notifications -v2     # تست‌های Notification + WebSocket
python manage.py test stocks -v2            # تست‌های Stock + WebSocket
python manage.py test orders -v2             # فقط تست‌های Matching Engine
python manage.py test blockchain_service -v2 # فقط تست‌های Blockchain

# Hardhat tests (Solidity):
cd ../contracts
npx hardhat test                             # 13 تست Solidity
```

### فایل‌های تست
| فایل | تعداد | شامل |
|---|---|---|
| `orders/tests.py` | 47 | Matching Engine (exact/partial/no-match/multi/priority/self-trade), Order API, Cancel+Refund, Portfolio, OrderBook |
| `blockchain_service/tests.py` | 26 | BlockchainService (disabled/connection/record/verify), Celery task, API endpoints, Matching Engine integration |
| `users/tests.py` | 28 | مدل User, ثبت‌نام, ورود JWT, پروفایل, تغییر رمز, **SIWE: nonce, verify, user creation, replay protection** |
| `notifications/tests.py` | 23 | مدل Notification, اعلان دوزبانه بعد از match, API, **WebSocket: auth, reject, broadcast** |
| `stocks/tests.py` | 20 | مدل Stock, لیست سهام, جزئیات, آمار بازار, **WebSocket: public, multi-client broadcast** |
| `transactions/tests.py` | 8 | مدل Transaction, تراکنش بعد از match, API لیست |
| `contracts/test/TransactionLedger.test.js` | 13 | Solidity contract: deploy, record, verify, duplicates, access control, multiple trades |

---

## Settings مهم (config/settings.py)

```python
# Dev mode (بدون PostgreSQL/Redis/RabbitMQ):
USE_SQLITE=True                    # SQLite بجای PostgreSQL
USE_LOCMEM_CACHE=True              # LocMem بجای Redis
CELERY_TASK_ALWAYS_EAGER=True      # Celery sync (auto with USE_SQLITE)

# Blockchain (Sprint 4):
BLOCKCHAIN_ENABLED=True            # فعال/غیرفعال کردن blockchain
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545   # Hardhat node
BLOCKCHAIN_PRIVATE_KEY=0xac09...   # Hardhat Account #0 (well-known dev key)
BLOCKCHAIN_CONTRACT_ADDRESS=       # خالی = خوندن از contract_address.json

# Django Channels (Sprint 5):
ASGI_APPLICATION=config.asgi.application
CHANNEL_LAYERS=InMemoryChannelLayer  # dev (no Redis needed)
# daphne در INSTALLED_APPS → runserver اتوماتیک از Daphne ASGI استفاده می‌کنه

# SIWE (Sprint 5):
SIWE_DOMAIN=localhost
SIWE_URI=http://localhost:5173

# CORS:
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,...
```

---

## نکات مهم برای ادامه کار

- **Sprint 6 انجام شد**: Docker + K8s + Monitoring + Terraform
- **همه 5 نیازمندی اجباری PDF انجام شد** ✅
- **همه ویژگی‌های امتیازی فنی انجام شد** ✅ (SIWE + Terraform)
- **هیچ API پولی لازم نیست**: Hardhat یک بلاکچین لوکال رایگان اجرا می‌کنه
- مدل Transaction فیلد `blockchain_hash` داره و بعد از هر match پر میشه
- `backend/blockchain_service/` سرویس Web3.py + Celery task + API endpoints
- `contracts/` پروژه Hardhat با TransactionLedger.sol (compiled + deployed)
- **Hardhat Node**: برای کار blockchain: `cd contracts; npx hardhat node` (terminal جدا)
- **Deploy**: `python manage.py deploy_contract` (یکبار بعد از اجرای node)
- **User model**: `USERNAME_FIELD="email"` ولی `create_user()` نیاز به `username` هم داره
- فایل `SE_PRJCT.pdf` را برای نیازمندی‌های دقیق هر بخش بخوان
- دیاگرام‌ها در `diagrams/` هستن (PlantUML + EA PNG)
- Backend virtual env: `backend/venv/` (در .gitignore هست)
- Database: `backend/db.sqlite3` (در .gitignore هست) - `python manage.py seed_data` برای rebuild
- Frontend mock data هنوز موجوده در `mockData.ts` به عنوان fallback
- همه صفحات فرانت الان به API واقعی وصلن + قیمت‌ها real-time از WebSocket می‌آیند (Sprint 5)
- **Daphne**: با نصب daphne, `manage.py runserver` اتوماتیک از ASGI (بجای WSGI) استفاده می‌کنه
- **WebSocket**: `ws://localhost:8000/ws/notifications/` (با JWT) و `ws://localhost:8000/ws/stocks/` (بدون auth)
- **SIWE**: دکمه "Connect Wallet" در LoginPage با MetaMask کار می‌کنه (extension مرورگر) - آدرس اتوماتیک به EIP-55 checksum تبدیل میشه
- **PowerShell**: از `&&` استفاده نکن، بجاش از `;` استفاده کن. working_directory پارامتر Shell tool رو ست کن.
- **سیستم‌عامل**: Windows (PowerShell)
- **صفحه پروفایل**: `/profile` - ویرایش اطلاعات شخصی، تغییر رمز، تنظیمات تم/زبان، آپلود آواتار. دسترسی: Sidebar یا کلیک روی آواتار در Header.
- **`.gitattributes`**: `*.sh text eol=lf` برای جلوگیری از خطای CRLF در entrypoint.sh (Docker).

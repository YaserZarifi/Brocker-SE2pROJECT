# BourseChain - پروژه کارگزاری بورس آنلاین

## اطلاعات پروژه
- **دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲
- **استاد**: دکتر گوهری
- **فایل نیازمندی‌ها**: `SE_PRJCT.pdf` (11 صفحه)
- **نام محصول**: BourseChain (بورس‌چین)

---

## خلاصه پروژه
یک **سامانه کارگزاری بورس آنلاین** با معماری **Modular Monolith** (Django apps جدا به عنوان میکروسرویس منطقی) که امکان خرید و فروش سهام را از طریق پلتفرمی شفاف و امن فراهم می‌کند. تراکنش‌ها روی **بلاکچین خصوصی EVM** ثبت می‌شوند.

---

## Tech Stack (تصمیم‌گیری شده)

| لایه | تکنولوژی | وضعیت |
|---|---|---|
| **Frontend** | React 19 + Vite 7 + TypeScript + Tailwind CSS v4 + shadcn-style UI | ✅ انجام شده |
| **UI Components** | Radix UI primitives + CVA + Tailwind (shadcn-style) | ✅ انجام شده |
| **State Management** | Zustand v5 | ✅ انجام شده |
| **Routing** | React Router v7 | ✅ انجام شده |
| **Charts** | Recharts v3 | ✅ انجام شده |
| **i18n** | i18next + react-i18next (FA/EN دوزبانه با RTL) | ✅ انجام شده |
| **Icons** | Lucide React | ✅ انجام شده |
| **Backend** | Django 5 + Django REST Framework + Django Channels | ⏳ Sprint 2 |
| **Database** | PostgreSQL | ⏳ Sprint 2 |
| **Cache/Session** | Redis | ⏳ Sprint 2 |
| **Message Broker** | RabbitMQ (via Celery) | ⏳ Sprint 3 |
| **Blockchain** | Hardhat + Ethers.js + Solidity (ERC20/ERC1155) | ⏳ Sprint 4 |
| **Real-time** | Django Channels + WebSocket | ⏳ Sprint 5 |
| **Container** | Docker + Docker Compose (برای ارائه نهایی) | ⏳ Sprint 6 |
| **Orchestration** | Kubernetes manifests (فقط فایل‌ها، اجرا نیاز نیست) | ⏳ Sprint 6 |
| **Monitoring** | Prometheus + Grafana (config only) | ⏳ Sprint 6 |
| **IaC (امتیازی)** | Terraform | ⏳ Sprint 6 |
| **Login امتیازی** | SIWE (Sign-In with Ethereum) via EIP-4361 | ⏳ Sprint 5 |

---

## معماری: Modular Monolith

یک پروژه Django با اپ‌های جدا (هر اپ = یک میکروسرویس منطقی):

```
backend/
├── config/                  # Django project settings
├── users/                   # User Management Service
├── stocks/                  # Stock Service (قیمت‌ها، لیست سهام)
├── orders/                  # Order Service + Matching Engine
├── transactions/            # Transaction Service
├── notifications/           # Notification Service (Django Channels/WebSocket)
└── blockchain_service/      # Blockchain Integration (Web3.py + Hardhat)
```

ارتباط بین سرویس‌ها از طریق **RabbitMQ/Celery** (مثل میکروسرویس واقعی).
برای ارائه نهایی: **Docker Compose** برای بسته‌بندی همه چیز.

---

## ساختار فعلی پروژه

```
d:\Amirkabir\SE2\Project\
├── CONTEXT.md               # ← این فایل
├── SE_PRJCT.pdf             # نیازمندی‌های پروژه (11 صفحه)
├── diagrams/                # دیاگرام‌های UML
│   ├── *.puml               # PlantUML source files
│   ├── EA/                  # Enterprise Architect diagrams (.png)
│   └── out/                 # Rendered SVGs
├── frontend/                # ✅ React Frontend (Sprint 1 - DONE)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # shadcn-style: button, card, input, badge, tabs, tooltip, avatar, progress, separator, scroll-area
│   │   │   ├── layout/      # Sidebar, Header, MainLayout
│   │   │   └── common/      # ThemeToggle, LanguageToggle, Logo
│   │   ├── pages/           # LoginPage, RegisterPage, DashboardPage, MarketPage, StockDetailPage, PortfolioPage, OrdersPage, TransactionsPage, NotificationsPage, AdminPage
│   │   ├── stores/          # Zustand: authStore, themeStore, stockStore, notificationStore
│   │   ├── services/        # mockData.ts (12 سهم ایرانی، portfolio, orders, transactions, notifications, orderBook, priceHistory generators)
│   │   ├── i18n/            # en.json + fa.json + index.ts
│   │   ├── types/           # TypeScript interfaces: User, Stock, Order, Transaction, Portfolio, Notification, OrderBook, PriceHistory, MarketStats
│   │   ├── lib/             # utils.ts (cn, formatPrice, formatNumber, formatPercent, getChangeColor, ...)
│   │   ├── router.tsx       # React Router config
│   │   ├── App.tsx          # Root component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind v4 + CSS variables (dark/light themes)
│   ├── index.html
│   ├── vite.config.ts       # Vite + Tailwind plugin + path aliases (@/)
│   ├── tsconfig.app.json    # TypeScript config with path aliases
│   └── package.json
├── backend/                 # ⏳ هنوز ساخته نشده
├── contracts/               # ⏳ هنوز ساخته نشده (Solidity)
├── docker/                  # ⏳ هنوز ساخته نشده
├── k8s/                     # ⏳ هنوز ساخته نشده
└── terraform/               # ⏳ هنوز ساخته نشده
```

---

## Frontend - جزئیات فنی

### اجرا
```bash
cd frontend
npm install
npm run dev     # → http://localhost:5173
```

### Theme System
- CSS variables در `:root` (light) و `.dark` (dark)
- رنگ‌های سفارشی: `--stock-up` (سبز), `--stock-down` (قرمز), `--sidebar`, `--chart-*`
- Tailwind v4 با `@theme inline` برای رجیستر کردن CSS vars به عنوان utility classes
- Toggle: `useThemeStore` → `toggleTheme()`

### i18n (دوزبانه)
- فارسی (RTL) + انگلیسی (LTR)
- `dir` attribute روی `<html>` تغییر می‌کنه
- فونت: Inter (EN) + Vazirmatn (FA) از Google Fonts
- Toggle: `useThemeStore` → `toggleLanguage()`

### Mock Data
- **12 سهم ایرانی** با نام فارسی و انگلیسی (FOLD, SHPN, KGDR, FMLI, SHBN, IKCO, SSEP, TAPK, PTRO, MKBT, SSAN, ZINC)
- **Real-time price simulation**: هر 3 ثانیه قیمت‌ها آپدیت میشن
- **Portfolio**: 5 هلدینگ با سود/زیان
- **Orders**: 6 سفارش با وضعیت‌های مختلف
- **Transactions**: 5 تراکنش تأیید شده با blockchain hash
- **Notifications**: 5 اعلان با انواع مختلف
- **Generator functions**: `generatePriceHistory()`, `generateOrderBook()`

### صفحات
1. **Login** (`/login`): فرم ورود + SIWE (Sign-In with Ethereum) button
2. **Register** (`/register`): فرم ثبت‌نام
3. **Dashboard** (`/dashboard`): 4 stat card + market index chart + portfolio summary + top gainers/losers + recent transactions
4. **Market** (`/market`): جستجو + فیلتر sector + sort + جدول سهام با real-time prices
5. **Stock Detail** (`/market/:symbol`): price chart + stats grid + order book (visual depth) + trade panel (buy/sell)
6. **Portfolio** (`/portfolio`): summary cards + holdings table + allocation pie chart
7. **Orders** (`/orders`): filter tabs + orders table with status badges
8. **Transactions** (`/transactions`): summary cards + table with blockchain hash links
9. **Notifications** (`/notifications`): notification list with read/unread + mark all read
10. **Admin** (`/admin`): stats + stocks management table + users table

---

## نقشه‌راه Sprint‌ها

### ✅ Sprint 1 - Frontend (DONE)
- React + Vite + Tailwind + shadcn-style UI
- تمام صفحات با Mock Data
- Dark/Light theme + FA/EN bilingual + RTL
- Real-time price simulation
- Charts (Area, Pie)

### ⏳ Sprint 2 - Backend API + Database
- Django project setup با اپ‌های جدا (users, stocks, orders, transactions, notifications, blockchain_service)
- PostgreSQL + Redis setup
- Django REST Framework APIs
- User authentication (JWT)
- CRUD for stocks, orders
- اتصال Frontend به Backend API (جایگزینی Mock Data)

### ⏳ Sprint 3 - Matching Engine + Order System
- Order matching algorithm (price-time priority)
- Celery + RabbitMQ for async processing
- Order status updates
- Partial fill support

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
- Incident management documentation
- Risk analysis document
- Vision document
- Test plan + test cases

---

## ویژگی‌های اصلی (از PDF نیازمندی‌ها)

### اجباری
1. مشاهده لیست سهام
2. ثبت سفارش خرید/فروش + Matching Engine
3. اعلان لحظه‌ای وضعیت سفارش‌ها (WebSocket)
4. ثبت تراکنش در بلاکچین خصوصی (EVM + Smart Contract)
5. نمایش سبد سهام و وضعیت معاملات

### امتیازی
1. ورود با اتریوم (SIWE - EIP-4361)
2. Matching Engine غیرمتمرکز روی بلاکچین
3. Infrastructure as Code (Terraform)
4. گزارش‌های Sprint

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
3. **RabbitMQ + Celery**: برای ارتباط غیرهمزمان بین سرویس‌ها (ایمیل/اعلان/matching).
4. **shadcn-style components**: بجای نصب shadcn/ui CLI، کامپوننت‌ها دستی با Radix + CVA + Tailwind نوشته شدن.
5. **Dark mode پیش‌فرض**: مناسب پلتفرم مالی/بورسی.
6. **Font**: Inter (EN) + Vazirmatn (FA).

---

## نکات مهم برای ادامه کار

- وقتی Backend ساخته شد، Mock Data در `frontend/src/services/mockData.ts` باید با API calls جایگزین بشن
- Stores در `frontend/src/stores/` باید API integration بگیرن
- Types در `frontend/src/types/index.ts` با backend models هماهنگ باشن
- فایل `SE_PRJCT.pdf` را برای نیازمندی‌های دقیق هر بخش بخوان
- دیاگرام‌ها در `diagrams/` هستن (PlantUML + EA PNG)
- برای backend از **Django 5 + DRF + Channels + Celery** استفاده کن
- برای blockchain از **Hardhat + Solidity + Ethers.js/Web3.py** استفاده کن

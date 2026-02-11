"""
Management command to seed the database with mock data.
Mirrors the frontend mockData.ts for consistent data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush  (delete existing data first)

Test users (after seeding):
    Main user:     ali@example.com      / Test1234!
    Demo (you):    demo@boursechain.ir  / Demo1234!
    Admin:         admin@boursechain.ir / Admin1234!
    Test seller:   seller@test.com      / Test1234!
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

from notifications.models import Notification
from orders.models import Order, PortfolioHolding
from stocks.models import PriceHistory, Stock
from transactions.models import Transaction

User = get_user_model()


def _add_holding_for_buyer(buyer, stock, quantity, execution_price):
    """Update buyer's portfolio after a seed-created transaction (matching engine not run)."""
    holding, _ = PortfolioHolding.objects.get_or_create(
        user=buyer,
        stock=stock,
        defaults={"quantity": 0, "average_buy_price": Decimal("0")},
    )
    old_total = holding.quantity * holding.average_buy_price
    new_qty = holding.quantity + quantity
    new_cost = old_total + quantity * execution_price
    holding.quantity = new_qty
    holding.average_buy_price = (new_cost / new_qty) if new_qty else Decimal("0")
    holding.save(update_fields=["quantity", "average_buy_price"])

# fmt: off
STOCKS_DATA = [
    {"symbol": "FOLD", "name": "Foolad Mobarakeh", "name_fa": "فولاد مبارکه", "current_price": 8750, "previous_close": 8520, "change": 230, "change_percent": 2.70, "volume": 45200000, "market_cap": 2625000000, "high_24h": 8820, "low_24h": 8490, "open_price": 8530, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "SHPN", "name": "Pars Oil Refinery", "name_fa": "شپنا", "current_price": 4320, "previous_close": 4480, "change": -160, "change_percent": -3.57, "volume": 38100000, "market_cap": 1296000000, "high_24h": 4510, "low_24h": 4290, "open_price": 4470, "sector": "Energy", "sector_fa": "انرژی"},
    {"symbol": "KGDR", "name": "Gol Gohar Mining", "name_fa": "کگل", "current_price": 12450, "previous_close": 12200, "change": 250, "change_percent": 2.05, "volume": 22800000, "market_cap": 4980000000, "high_24h": 12580, "low_24h": 12180, "open_price": 12220, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "FMLI", "name": "National Copper", "name_fa": "فملی", "current_price": 6780, "previous_close": 6650, "change": 130, "change_percent": 1.95, "volume": 31500000, "market_cap": 3390000000, "high_24h": 6830, "low_24h": 6620, "open_price": 6660, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "SHBN", "name": "Bandar Abbas Refinery", "name_fa": "شبندر", "current_price": 3890, "previous_close": 4010, "change": -120, "change_percent": -2.99, "volume": 28900000, "market_cap": 1167000000, "high_24h": 4030, "low_24h": 3860, "open_price": 4000, "sector": "Energy", "sector_fa": "انرژی"},
    {"symbol": "IKCO", "name": "Iran Khodro", "name_fa": "خودرو", "current_price": 2150, "previous_close": 2080, "change": 70, "change_percent": 3.37, "volume": 89400000, "market_cap": 6450000000, "high_24h": 2190, "low_24h": 2060, "open_price": 2090, "sector": "Automotive", "sector_fa": "خودرو"},
    {"symbol": "SSEP", "name": "Sepah Bank", "name_fa": "وسپه", "current_price": 1540, "previous_close": 1560, "change": -20, "change_percent": -1.28, "volume": 15600000, "market_cap": 924000000, "high_24h": 1575, "low_24h": 1520, "open_price": 1555, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "TAPK", "name": "TAPICO Holding", "name_fa": "تاپیکو", "current_price": 9870, "previous_close": 9640, "change": 230, "change_percent": 2.39, "volume": 18200000, "market_cap": 3948000000, "high_24h": 9920, "low_24h": 9600, "open_price": 9650, "sector": "Petrochemical", "sector_fa": "پتروشیمی"},
    {"symbol": "PTRO", "name": "Petrol Group", "name_fa": "پترول", "current_price": 5430, "previous_close": 5310, "change": 120, "change_percent": 2.26, "volume": 25700000, "market_cap": 2172000000, "high_24h": 5480, "low_24h": 5280, "open_price": 5320, "sector": "Petrochemical", "sector_fa": "پتروشیمی"},
    {"symbol": "MKBT", "name": "Mobin Telecom", "name_fa": "همراه اول", "current_price": 7250, "previous_close": 7380, "change": -130, "change_percent": -1.76, "volume": 12300000, "market_cap": 4350000000, "high_24h": 7410, "low_24h": 7200, "open_price": 7370, "sector": "Telecom", "sector_fa": "مخابرات"},
    {"symbol": "SSAN", "name": "Saipa Auto", "name_fa": "خساپا", "current_price": 1820, "previous_close": 1790, "change": 30, "change_percent": 1.68, "volume": 72100000, "market_cap": 3640000000, "high_24h": 1850, "low_24h": 1780, "open_price": 1795, "sector": "Automotive", "sector_fa": "خودرو"},
    {"symbol": "ZINC", "name": "Iran Zinc Mines", "name_fa": "فزر", "current_price": 15680, "previous_close": 15200, "change": 480, "change_percent": 3.16, "volume": 8900000, "market_cap": 1568000000, "high_24h": 15750, "low_24h": 15150, "open_price": 15220, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "MELI", "name": "Mellat Bank", "name_fa": "ملت", "current_price": 2850, "previous_close": 2790, "change": 60, "change_percent": 2.15, "volume": 42100000, "market_cap": 3420000000, "high_24h": 2880, "low_24h": 2760, "open_price": 2795, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "KHAZ", "name": "Khazar Steel", "name_fa": "خزافولاد", "current_price": 5420, "previous_close": 5280, "change": 140, "change_percent": 2.65, "volume": 18500000, "market_cap": 1626000000, "high_24h": 5480, "low_24h": 5240, "open_price": 5300, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "SHSA", "name": "Saderat Bank", "name_fa": "صادرات", "current_price": 1890, "previous_close": 1920, "change": -30, "change_percent": -1.56, "volume": 29800000, "market_cap": 1890000000, "high_24h": 1950, "low_24h": 1860, "open_price": 1910, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "DANA", "name": "Dana Insurance", "name_fa": "دانا", "current_price": 4120, "previous_close": 4080, "change": 40, "change_percent": 0.98, "volume": 12400000, "market_cap": 1236000000, "high_24h": 4180, "low_24h": 4040, "open_price": 4090, "sector": "Insurance", "sector_fa": "بیمه"},
    {"symbol": "BINA", "name": "Bina Investment", "name_fa": "بینا", "current_price": 3250, "previous_close": 3180, "change": 70, "change_percent": 2.20, "volume": 25600000, "market_cap": 1950000000, "high_24h": 3290, "low_24h": 3140, "open_price": 3190, "sector": "Investment", "sector_fa": "سرمایه‌گذاری"},
    {"symbol": "SINA", "name": "Sina Bank", "name_fa": "سینا", "current_price": 2150, "previous_close": 2180, "change": -30, "change_percent": -1.38, "volume": 18700000, "market_cap": 1290000000, "high_24h": 2220, "low_24h": 2120, "open_price": 2170, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "KRAF", "name": "Kraft Paper", "name_fa": "کارتن‌سازی", "current_price": 4850, "previous_close": 4720, "change": 130, "change_percent": 2.75, "volume": 9800000, "market_cap": 1455000000, "high_24h": 4920, "low_24h": 4680, "open_price": 4740, "sector": "Paper", "sector_fa": "کاغذ"},
    {"symbol": "CHML", "name": "Chimeh Steel", "name_fa": "چادرملو", "current_price": 8920, "previous_close": 8750, "change": 170, "change_percent": 1.94, "volume": 14200000, "market_cap": 2676000000, "high_24h": 8980, "low_24h": 8680, "open_price": 8780, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "PARA", "name": "Parsian Bank", "name_fa": "پارسیان", "current_price": 3680, "previous_close": 3620, "change": 60, "change_percent": 1.66, "volume": 22100000, "market_cap": 2944000000, "high_24h": 3720, "low_24h": 3580, "open_price": 3630, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "TEJM", "name": "Tejarat Bank", "name_fa": "تجارت", "current_price": 2450, "previous_close": 2410, "change": 40, "change_percent": 1.66, "volume": 35400000, "market_cap": 2450000000, "high_24h": 2490, "low_24h": 2380, "open_price": 2420, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "SAIP", "name": "Saipa Diesel", "name_fa": "دیزل سایپا", "current_price": 1520, "previous_close": 1480, "change": 40, "change_percent": 2.70, "volume": 18600000, "market_cap": 912000000, "high_24h": 1550, "low_24h": 1460, "open_price": 1490, "sector": "Automotive", "sector_fa": "خودرو"},
]
# fmt: on


class Command(BaseCommand):
    help = "Seed the database with mock data (stocks, users, orders, transactions, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            Notification.objects.all().delete()
            Transaction.objects.all().delete()
            Order.objects.all().delete()
            PortfolioHolding.objects.all().delete()
            PriceHistory.objects.all().delete()
            Stock.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Data flushed."))

        self._create_users()
        self._create_stocks()
        self._create_price_history()
        self._create_orders_and_transactions()
        self._create_portfolio_holdings()
        self._ensure_test_seller_holdings()  # Always ensure seller has stocks (runs even without flush)
        self._ensure_demo_holdings()  # Always ensure demo user has portfolio (fixes empty demo)
        self._ensure_ali_holdings()   # Restore ali portfolio if empty so you can test with both accounts
        self._sync_holdings_from_transactions()  # Fix: buyer portfolio must reflect all confirmed transactions
        self._create_notifications()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _create_users(self):
        """Create test users."""
        # Main user
        if not User.objects.filter(email="ali@example.com").exists():
            user = User.objects.create_user(
                username="ali_rezaei",
                email="ali@example.com",
                password="Test1234!",
                first_name="Ali",
                last_name="Rezaei",
                role="customer",
                wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
                cash_balance=Decimal("5340500.00"),
            )
            self.stdout.write(f"  Created user: {user.email}")

        # Demo user (for you to test the app)
        if not User.objects.filter(email="demo@boursechain.ir").exists():
            User.objects.create_user(
                username="demo_user",
                email="demo@boursechain.ir",
                password="Demo1234!",
                first_name="Demo",
                last_name="User",
                role="customer",
                wallet_address="0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b",
                cash_balance=Decimal("25000000.00"),
            )
            self.stdout.write("  Created demo user: demo@boursechain.ir (Demo1234!)")

        # Admin user
        if not User.objects.filter(email="admin@boursechain.ir").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@boursechain.ir",
                password="Admin1234!",
                first_name="Admin",
                last_name="BourseChain",
                role="admin",
            )
            self.stdout.write(f"  Created admin: {admin.email}")

        # Extra users for transactions
        # Liquidity provider - has cash + shares for Market orders to match
        if not User.objects.filter(email="liquidity@boursechain.ir").exists():
            User.objects.create_user(
                username="liquidity",
                email="liquidity@boursechain.ir",
                password="Test1234!",
                first_name="Liquidity",
                last_name="Provider",
                role="customer",
                cash_balance=Decimal("3000000000.00"),
            )
            self.stdout.write("  Created liquidity provider user.")

        # Test seller - has stocks to sell, for testing buy/sell matching
        if not User.objects.filter(email="seller@test.com").exists():
            User.objects.create_user(
                username="seller_test",
                email="seller@test.com",
                password="Test1234!",
                first_name="Test",
                last_name="Seller",
                role="customer",
                cash_balance=Decimal("5000000.00"),
            )
            self.stdout.write("  Created test seller user (seller@test.com).")

        extra_users = [
            ("user042", "user042@example.com", "Sara", "Mohammadi"),
            ("user015", "user015@example.com", "Reza", "Ahmadi"),
            ("user088", "user088@example.com", "Maryam", "Hosseini"),
            ("user033", "user033@example.com", "Hassan", "Karimi"),
            ("user077", "user077@example.com", "Zahra", "Bahrami"),
            ("user011", "user011@example.com", "Amir", "Nasiri"),
            ("user022", "user022@example.com", "Fatima", "Rahimi"),
            ("user055", "user055@example.com", "Mehdi", "Salehi"),
            ("user066", "user066@example.com", "Narges", "Kazemi"),
            ("user099", "user099@example.com", "Saeed", "Mousavi"),
        ]
        for uname, email, first, last in extra_users:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    username=uname,
                    email=email,
                    password="Test1234!",
                    first_name=first,
                    last_name=last,
                    role="customer",
                    cash_balance=Decimal("10000000.00"),
                )
        self.stdout.write(self.style.SUCCESS("  Users created."))

    def _create_stocks(self):
        """Create the 12 Iranian stocks."""
        for data in STOCKS_DATA:
            Stock.objects.update_or_create(
                symbol=data["symbol"],
                defaults=data,
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(STOCKS_DATA)} stocks created."))

    def _create_price_history(self):
        """Generate 90-day price history for each stock."""
        if PriceHistory.objects.exists():
            self.stdout.write("  Price history already exists, skipping.")
            return

        today = timezone.now().date()
        for stock in Stock.objects.all():
            price = float(stock.current_price) * 0.82
            entries = []
            for i in range(90, -1, -1):
                date = today - timedelta(days=i)
                volatility = 0.03
                change = (random.random() - 0.48) * volatility
                open_p = round(price, 2)
                close_p = round(price * (1 + change), 2)
                high_p = round(max(open_p, close_p) * (1 + random.random() * 0.015), 2)
                low_p = round(min(open_p, close_p) * (1 - random.random() * 0.015), 2)
                volume = random.randint(5_000_000, 55_000_000)

                entries.append(
                    PriceHistory(
                        stock=stock,
                        timestamp=date,
                        open_price=open_p,
                        high=high_p,
                        low=low_p,
                        close=close_p,
                        volume=volume,
                    )
                )
                price = close_p

            PriceHistory.objects.bulk_create(entries)
        self.stdout.write(self.style.SUCCESS("  Price history generated (90 days)."))

    def _create_orders_and_transactions(self):
        """Create mock orders and transactions."""
        if Order.objects.exists():
            self.stdout.write("  Orders already exist, skipping.")
            return

        user = User.objects.get(email="ali@example.com")
        user042 = User.objects.get(email="user042@example.com")
        user015 = User.objects.get(email="user015@example.com")
        user088 = User.objects.get(email="user088@example.com")
        user033 = User.objects.get(email="user033@example.com")
        user077 = User.objects.get(email="user077@example.com")
        user011 = User.objects.get(email="user011@example.com")
        user022 = User.objects.get(email="user022@example.com")
        user055 = User.objects.get(email="user055@example.com")

        now = timezone.now()

        # ORD-001: Buy 200 FOLD @ 8700 - matched
        fold = Stock.objects.get(symbol="FOLD")
        ord1 = Order.objects.create(user=user, stock=fold, type="buy", price=8700, quantity=200, filled_quantity=200, status="matched")

        # ORD-002: Sell 300 SHPN @ 4350 - pending
        shpn = Stock.objects.get(symbol="SHPN")
        Order.objects.create(user=user, stock=shpn, type="sell", price=4350, quantity=300, filled_quantity=0, status="pending")

        # ORD-003: Buy 500 IKCO @ 2100 - partial
        ikco = Stock.objects.get(symbol="IKCO")
        ord3 = Order.objects.create(user=user, stock=ikco, type="buy", price=2100, quantity=500, filled_quantity=350, status="partial")

        # ORD-004: Buy 100 KGDR @ 12300 - matched
        kgdr = Stock.objects.get(symbol="KGDR")
        ord4 = Order.objects.create(user=user, stock=kgdr, type="buy", price=12300, quantity=100, filled_quantity=100, status="matched")

        # ORD-005: Sell 1000 SSAN @ 1900 - cancelled
        ssan = Stock.objects.get(symbol="SSAN")
        Order.objects.create(user=user, stock=ssan, type="sell", price=1900, quantity=1000, filled_quantity=0, status="cancelled")

        # ORD-006: Buy 400 PTRO @ 5400 - pending
        ptro = Stock.objects.get(symbol="PTRO")
        Order.objects.create(user=user, stock=ptro, type="buy", price=5400, quantity=400, filled_quantity=0, status="pending")

        # More orders for main user (richer history)
        fmli = Stock.objects.get(symbol="FMLI")
        zinc = Stock.objects.get(symbol="ZINC")
        meli = Stock.objects.get(symbol="MELI")
        Order.objects.create(user=user, stock=fmli, type="buy", price=6600, quantity=150, filled_quantity=0, status="pending")
        Order.objects.create(user=user, stock=zinc, type="sell", price=15800, quantity=50, filled_quantity=0, status="pending")
        ord_meli_buy = Order.objects.create(user=user, stock=meli, type="buy", price=2800, quantity=400, filled_quantity=400, status="matched")

        # Counter orders for transactions
        sell_ord1 = Order.objects.create(user=user042, stock=fold, type="sell", price=8700, quantity=200, filled_quantity=200, status="matched")
        sell_ord3 = Order.objects.create(user=user015, stock=ikco, type="sell", price=2100, quantity=350, filled_quantity=350, status="matched")
        sell_ord4 = Order.objects.create(user=user088, stock=kgdr, type="sell", price=12300, quantity=100, filled_quantity=100, status="matched")

        tapk = Stock.objects.get(symbol="TAPK")
        buy_ord_tapk = Order.objects.create(user=user, stock=tapk, type="buy", price=9500, quantity=300, filled_quantity=300, status="matched")
        sell_ord_tapk = Order.objects.create(user=user033, stock=tapk, type="sell", price=9500, quantity=300, filled_quantity=300, status="matched")
        sell_ord_meli = Order.objects.create(user=user011, stock=meli, type="sell", price=2800, quantity=400, filled_quantity=400, status="matched")

        buy_ord_shpn = Order.objects.create(user=user, stock=shpn, type="buy", price=4600, quantity=800, filled_quantity=800, status="matched")
        sell_ord_shpn = Order.objects.create(user=user077, stock=shpn, type="sell", price=4600, quantity=800, filled_quantity=800, status="matched")

        # Transactions
        Transaction.objects.create(
            buy_order=ord1, sell_order=sell_ord1, stock=fold,
            price=8700, quantity=200, total_value=1740000,
            buyer=user, seller=user042,
            blockchain_hash="0x8a3bf7c2e4d1a9b3c5e7f2d4a6b8c0e2f4d6a8b0c2e4f6a8b0c2e4f6a8b0f7c2",
            status="confirmed",
        )
        Transaction.objects.create(
            buy_order=ord3, sell_order=sell_ord3, stock=ikco,
            price=2100, quantity=350, total_value=735000,
            buyer=user, seller=user015,
            blockchain_hash="0x2c4ea1d9f3b5c7e9d1a3b5c7e9f1d3a5b7c9e1f3d5a7b9c1e3f5d7a9b1c3a1d9",
            status="confirmed",
        )
        Transaction.objects.create(
            buy_order=ord4, sell_order=sell_ord4, stock=kgdr,
            price=12300, quantity=100, total_value=1230000,
            buyer=user, seller=user088,
            blockchain_hash="0x5f1ac3e8d2b4f6a8c0e2d4f6a8b0c2e4f6a8b0c2e4f6a8b0c2e4f6a8b0c3e8",
            status="confirmed",
        )
        Transaction.objects.create(
            buy_order=buy_ord_tapk, sell_order=sell_ord_tapk, stock=tapk,
            price=9500, quantity=300, total_value=2850000,
            buyer=user, seller=user033,
            blockchain_hash="0x9d7cb4f1a3e5d7b9c1f3a5d7b9e1c3f5a7d9b1e3c5f7a9d1b3e5c7f9a1d3b4f1",
            status="confirmed",
        )
        Transaction.objects.create(
            buy_order=buy_ord_shpn, sell_order=sell_ord_shpn, stock=shpn,
            price=4600, quantity=800, total_value=3680000,
            buyer=user, seller=user077,
            blockchain_hash="0x1e3fd6a2b4c8e0f2a4d6b8c0e2f4a6d8b0c2e4f6a8d0b2c4e6f8a0d2b4c6d6a2",
            status="confirmed",
        )
        Transaction.objects.create(
            buy_order=ord_meli_buy, sell_order=sell_ord_meli, stock=meli,
            price=2800, quantity=400, total_value=1120000,
            buyer=user, seller=user011,
            blockchain_hash="0x7b2e9f4a1c6d8e0b3f5a7c9e1d4b6f8a0c2e5d7b9f1a4c6e8d0b3f5a7c9e2d4",
            status="confirmed",
        )

        # --- Demo user: orders and transactions ---
        demo = User.objects.filter(email="demo@boursechain.ir").first()
        if demo:
            chml = Stock.objects.get(symbol="CHML")
            para = Stock.objects.get(symbol="PARA")
            dana = Stock.objects.get(symbol="DANA")
            # Demo: buy orders (some matched, some pending)
            demo_buy_fold = Order.objects.create(user=demo, stock=fold, type="buy", price=8600, quantity=100, filled_quantity=100, status="matched")
            demo_buy_chml = Order.objects.create(user=demo, stock=chml, type="buy", price=8800, quantity=200, filled_quantity=200, status="matched")
            demo_buy_para = Order.objects.create(user=demo, stock=para, type="buy", price=3650, quantity=500, filled_quantity=0, status="pending")
            Order.objects.create(user=demo, stock=ikco, type="buy", price=2120, quantity=300, filled_quantity=0, status="pending")
            Order.objects.create(user=demo, stock=dana, type="sell", price=4150, quantity=100, filled_quantity=0, status="pending")
            # Counter parties for demo's matched buys
            demo_sell_fold = Order.objects.create(user=user022, stock=fold, type="sell", price=8600, quantity=100, filled_quantity=100, status="matched")
            demo_sell_chml = Order.objects.create(user=user055, stock=chml, type="sell", price=8800, quantity=200, filled_quantity=200, status="matched")
            Transaction.objects.create(
                buy_order=demo_buy_fold, sell_order=demo_sell_fold, stock=fold,
                price=8600, quantity=100, total_value=860000,
                buyer=demo, seller=user022,
                blockchain_hash="0xa1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
                status="confirmed",
            )
            Transaction.objects.create(
                buy_order=demo_buy_chml, sell_order=demo_sell_chml, stock=chml,
                price=8800, quantity=200, total_value=1760000,
                buyer=demo, seller=user055,
                blockchain_hash="0xc3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
                status="confirmed",
            )

        # Liquidity orders - multiple SELL + BUY at different price levels per stock
        # Creates a deep order book so Market orders execute and users can sample many trades
        lp = User.objects.filter(email="liquidity@boursechain.ir").first()
        if lp:
            # Price tiers: sell above market, buy below market (spread simulation)
            sell_tiers = [1.0, 1.005, 1.01, 1.015, 1.02]  # at market, +0.5%, +1%, +1.5%, +2%
            buy_tiers = [1.0, 0.995, 0.99, 0.985, 0.98]   # at market, -0.5%, -1%, -1.5%, -2%
            qty_per_order = 2500

            for stock in Stock.objects.all():
                lp.refresh_from_db()
                base = float(stock.current_price)

                for mult in sell_tiers:
                    price = Decimal(str(round(base * mult, 2)))
                    holding, _ = PortfolioHolding.objects.get_or_create(
                        user=lp, stock=stock,
                        defaults={"quantity": 0, "average_buy_price": Decimal("0")},
                    )
                    if holding.quantity >= qty_per_order:
                        holding.quantity -= qty_per_order
                        holding.save(update_fields=["quantity"])
                        Order.objects.create(
                            user=lp, stock=stock, type="sell",
                            execution_type="limit", price=price, quantity=qty_per_order,
                            status="pending",
                        )

                for mult in buy_tiers:
                    price = Decimal(str(round(base * mult, 2)))
                    total = price * qty_per_order
                    if lp.cash_balance >= total:
                        lp.cash_balance -= total
                        lp.save(update_fields=["cash_balance"])
                        Order.objects.create(
                            user=lp, stock=stock, type="buy",
                            execution_type="limit", price=price, quantity=qty_per_order,
                            status="pending",
                        )
            self.stdout.write("  Liquidity orders created (5 sell + 5 buy tiers per stock).")

        self.stdout.write(self.style.SUCCESS("  Orders & transactions created."))

    def _create_portfolio_holdings(self):
        """Create portfolio holdings for the main user."""
        if PortfolioHolding.objects.exists():
            self.stdout.write("  Holdings already exist, skipping.")
            return

        user = User.objects.get(email="ali@example.com")

        holdings_data = [
            ("FOLD", 500, 8200),
            ("IKCO", 2000, 1950),
            ("SHPN", 800, 4600),
            ("TAPK", 300, 9400),
            ("KGDR", 150, 11800),
            ("FMLI", 300, 6500),
            ("MELI", 500, 2700),
            ("PTRO", 200, 5200),
            ("ZINC", 100, 15000),
        ]

        for symbol, qty, avg_price in holdings_data:
            stock = Stock.objects.get(symbol=symbol)
            PortfolioHolding.objects.create(
                user=user,
                stock=stock,
                quantity=qty,
                average_buy_price=Decimal(str(avg_price)),
            )

        # Liquidity provider holdings - so Market Sell orders can match
        lp = User.objects.filter(email="liquidity@boursechain.ir").first()
        if lp:
            for stock in Stock.objects.all():
                PortfolioHolding.objects.get_or_create(
                    user=lp,
                    stock=stock,
                    defaults={
                        "quantity": 50_000,
                        "average_buy_price": stock.current_price,
                    },
                )

        # Demo user portfolio (so you can see a full portfolio when logged in as demo)
        demo = User.objects.filter(email="demo@boursechain.ir").first()
        if demo:
            demo_holdings = [
                ("FOLD", 100, 8600),
                ("CHML", 200, 8800),
                ("IKCO", 500, 2050),
                ("SHPN", 200, 4300),
                ("MELI", 300, 2780),
                ("ZINC", 80, 15200),
                ("PTRO", 150, 5300),
                ("KGDR", 50, 12200),
                ("TAPK", 100, 9600),
                ("DANA", 150, 4080),
            ]
            for symbol, qty, avg_price in demo_holdings:
                stock = Stock.objects.get(symbol=symbol)
                PortfolioHolding.objects.get_or_create(
                    user=demo,
                    stock=stock,
                    defaults={
                        "quantity": qty,
                        "average_buy_price": Decimal(str(avg_price)),
                    },
                )
            self.stdout.write("  Demo user portfolio created.")

        self.stdout.write(self.style.SUCCESS("  Portfolio holdings created."))

    def _create_notifications(self):
        """Create mock notifications."""
        if Notification.objects.exists():
            self.stdout.write("  Notifications already exist, skipping.")
            return

        user = User.objects.get(email="ali@example.com")

        notifications = [
            {"title": "Order Matched", "title_fa": "سفارش تطبیق شد", "message": "Your buy order for 200 FOLD at 8,700 has been matched.", "message_fa": "سفارش خرید ۲۰۰ سهم فولاد با قیمت ۸,۷۰۰ تطبیق شد.", "type": "order_matched", "read": False},
            {"title": "Partial Fill", "title_fa": "تطبیق جزئی", "message": "350 of 500 shares filled for IKCO buy order at 2,100.", "message_fa": "۳۵۰ از ۵۰۰ سهم ایران خودرو با قیمت ۲,۱۰۰ تطبیق شد.", "type": "order_matched", "read": False},
            {"title": "Transaction Confirmed", "title_fa": "تراکنش تأیید شد", "message": "Transaction TX-001 recorded on blockchain.", "message_fa": "تراکنش TX-001 در بلاکچین ثبت شد.", "type": "transaction", "read": True},
            {"title": "Price Alert", "title_fa": "هشدار قیمت", "message": "ZINC has surged +3.16% today. Current price: 15,680", "message_fa": "فزر امروز ۳.۱۶٪ رشد داشته.", "type": "price_alert", "read": True},
            {"title": "Order Cancelled", "title_fa": "سفارش لغو شد", "message": "Your sell order for 1000 SSAN at 1,900 has been cancelled.", "message_fa": "سفارش فروش ۱,۰۰۰ سهم خساپا لغو شد.", "type": "order_cancelled", "read": True},
            {"title": "Welcome to BourseChain", "title_fa": "به بورسچین خوش آمدید", "message": "Start trading with real-time market data.", "message_fa": "با داده‌های لحظه‌ای معامله کنید.", "type": "system", "read": False},
            {"title": "Portfolio Update", "title_fa": "به‌روزرسانی سبد", "message": "Your portfolio value increased by 2.3% today.", "message_fa": "ارزش سبد شما امروز ۲.۳٪ رشد کرد.", "type": "price_alert", "read": False},
            {"title": "Market Open", "title_fa": "بازگشایی بازار", "message": "Trading session started. Market is now open.", "message_fa": "جلسه معاملاتی آغاز شد.", "type": "system", "read": True},
        ]

        for n in notifications:
            Notification.objects.create(user=user, **n)

        # Notifications for demo user
        demo = User.objects.filter(email="demo@boursechain.ir").first()
        if demo:
            demo_notifications = [
                {"title": "Order Matched", "title_fa": "سفارش تطبیق شد", "message": "Your buy order for 100 FOLD at 8,600 has been matched.", "message_fa": "سفارش خرید ۱۰۰ سهم فولاد با قیمت ۸,۶۰۰ تطبیق شد.", "type": "order_matched", "read": False},
                {"title": "Order Matched", "title_fa": "سفارش تطبیق شد", "message": "Your buy order for 200 CHML at 8,800 has been matched.", "message_fa": "سفارش خرید ۲۰۰ سهم چادرملو تطبیق شد.", "type": "order_matched", "read": False},
                {"title": "Transaction Confirmed", "title_fa": "تراکنش تأیید شد", "message": "Transaction for 100 FOLD recorded on blockchain.", "message_fa": "تراکنش ۱۰۰ سهم فولاد در بلاکچین ثبت شد.", "type": "transaction", "read": True},
                {"title": "Welcome to BourseChain", "title_fa": "به بورسچین خوش آمدید", "message": "You can test the app with this demo account.", "message_fa": "می‌توانید با این حساب دمو برنامه را تست کنید.", "type": "system", "read": False},
                {"title": "Price Alert", "title_fa": "هشدار قیمت", "message": "FOLD is up 2.7% today. Current price: 8,750", "message_fa": "فولاد امروز ۲.۷٪ رشد داشته.", "type": "price_alert", "read": False},
            ]
            for n in demo_notifications:
                Notification.objects.create(user=demo, **n)
            self.stdout.write("  Demo user notifications created.")

        self.stdout.write(self.style.SUCCESS("  Notifications created."))

    def _ensure_test_seller_holdings(self):
        """Ensure test seller has holdings - runs even when other holdings exist."""
        seller = User.objects.filter(email="seller@test.com").first()
        if not seller:
            return
        seller_holdings = [
            ("FOLD", 500, 8500),
            ("IKCO", 1000, 2000),
            ("SHPN", 400, 4200),
            ("FMLI", 200, 6500),
            ("PTRO", 300, 5200),
            ("KGDR", 100, 12000),
        ]
        for symbol, qty, avg_price in seller_holdings:
            try:
                stock = Stock.objects.get(symbol=symbol)
                holding, created = PortfolioHolding.objects.get_or_create(
                    user=seller,
                    stock=stock,
                    defaults={
                        "quantity": qty,
                        "average_buy_price": Decimal(str(avg_price)),
                    },
                )
                if not created and holding.quantity == 0:
                    holding.quantity = qty
                    holding.average_buy_price = Decimal(str(avg_price))
                    holding.save()
            except Stock.DoesNotExist:
                pass
        self.stdout.write("  Test seller holdings ensured (seller@test.com).")

    def _ensure_demo_holdings(self):
        """Ensure demo user has portfolio - runs every time so demo is never empty."""
        demo = User.objects.filter(email="demo@boursechain.ir").first()
        if not demo:
            return
        demo_holdings = [
            ("FOLD", 100, 8600),
            ("CHML", 200, 8800),
            ("IKCO", 500, 2050),
            ("SHPN", 200, 4300),
            ("MELI", 300, 2780),
            ("ZINC", 80, 15200),
            ("PTRO", 150, 5300),
            ("KGDR", 50, 12200),
            ("TAPK", 100, 9600),
            ("DANA", 150, 4080),
        ]
        for symbol, qty, avg_price in demo_holdings:
            try:
                stock = Stock.objects.get(symbol=symbol)
                holding, created = PortfolioHolding.objects.get_or_create(
                    user=demo,
                    stock=stock,
                    defaults={
                        "quantity": qty,
                        "average_buy_price": Decimal(str(avg_price)),
                    },
                )
                if not created and holding.quantity == 0:
                    holding.quantity = qty
                    holding.average_buy_price = Decimal(str(avg_price))
                    holding.save()
            except Stock.DoesNotExist:
                pass
        self.stdout.write("  Demo user portfolio ensured (demo@boursechain.ir).")

    def _ensure_ali_holdings(self):
        """Restore ali's portfolio if empty so both demo and ali can be used for testing."""
        user = User.objects.filter(email="ali@example.com").first()
        if not user:
            return
        ali_holdings = [
            ("FOLD", 500, 8200),
            ("IKCO", 2000, 1950),
            ("SHPN", 800, 4600),
            ("TAPK", 300, 9400),
            ("KGDR", 150, 11800),
            ("FMLI", 300, 6500),
            ("MELI", 500, 2700),
            ("PTRO", 200, 5200),
            ("ZINC", 100, 15000),
        ]
        for symbol, qty, avg_price in ali_holdings:
            try:
                stock = Stock.objects.get(symbol=symbol)
                holding, created = PortfolioHolding.objects.get_or_create(
                    user=user,
                    stock=stock,
                    defaults={
                        "quantity": qty,
                        "average_buy_price": Decimal(str(avg_price)),
                    },
                )
                if not created and holding.quantity == 0:
                    holding.quantity = qty
                    holding.average_buy_price = Decimal(str(avg_price))
                    holding.save()
            except Stock.DoesNotExist:
                pass
        self.stdout.write("  Ali portfolio ensured (ali@example.com).")

    def _sync_holdings_from_transactions(self):
        """
        Ensure every buyer's portfolio reflects confirmed transactions.
        Fixes the case where seed (or matching) created Transaction records
        but the buyer's PortfolioHolding was never updated.
        """
        # Group by (buyer_id, stock_id), sum quantity and total_value
        confirmed = Transaction.objects.filter(status="confirmed")
        seen = set()
        updated = 0
        for tx in confirmed.select_related("buyer", "stock"):
            key = (tx.buyer_id, tx.stock_id)
            if key in seen:
                continue
            seen.add(key)
            agg = confirmed.filter(buyer_id=tx.buyer_id, stock_id=tx.stock_id).aggregate(
                total_qty=Sum("quantity"), total_val=Sum("total_value")
            )
            total_qty = agg["total_qty"] or 0
            total_val = agg["total_val"] or Decimal("0")
            if total_qty <= 0:
                continue
            holding, created = PortfolioHolding.objects.get_or_create(
                user_id=tx.buyer_id,
                stock_id=tx.stock_id,
                defaults={"quantity": 0, "average_buy_price": Decimal("0")},
            )
            if holding.quantity < total_qty:
                holding.quantity = total_qty
                holding.average_buy_price = (total_val / total_qty) if total_qty else Decimal("0")
                holding.save(update_fields=["quantity", "average_buy_price"])
                updated += 1
        if updated:
            self.stdout.write(f"  Synced {updated} holdings from transaction history.")

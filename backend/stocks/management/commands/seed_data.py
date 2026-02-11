"""
Management command to seed the database with mock data.
Mirrors the frontend mockData.ts for consistent data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush  (delete existing data first)
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications.models import Notification
from orders.models import Order, PortfolioHolding
from stocks.models import PriceHistory, Stock
from transactions.models import Transaction

User = get_user_model()

# fmt: off
STOCKS_DATA = [
    {"symbol": "FOLD", "name": "Foolad Mobarakeh", "name_fa": "فولاد مبارکه", "current_price": 8750, "previous_close": 8520, "change": 230, "change_percent": 2.70, "volume": 45200000, "market_cap": 2625000000, "high_24h": 8820, "low_24h": 8490, "open_price": 8530, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "SHPN", "name": "Pars Oil Refinery", "name_fa": "شپنا - پالایش نفت", "current_price": 4320, "previous_close": 4480, "change": -160, "change_percent": -3.57, "volume": 38100000, "market_cap": 1296000000, "high_24h": 4510, "low_24h": 4290, "open_price": 4470, "sector": "Energy", "sector_fa": "انرژی"},
    {"symbol": "KGDR", "name": "Gol Gohar Mining", "name_fa": "کگل - گل‌گهر", "current_price": 12450, "previous_close": 12200, "change": 250, "change_percent": 2.05, "volume": 22800000, "market_cap": 4980000000, "high_24h": 12580, "low_24h": 12180, "open_price": 12220, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "FMLI", "name": "National Copper", "name_fa": "فملی - ملی مس", "current_price": 6780, "previous_close": 6650, "change": 130, "change_percent": 1.95, "volume": 31500000, "market_cap": 3390000000, "high_24h": 6830, "low_24h": 6620, "open_price": 6660, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
    {"symbol": "SHBN", "name": "Bandar Abbas Refinery", "name_fa": "شبندر - پالایش بندرعباس", "current_price": 3890, "previous_close": 4010, "change": -120, "change_percent": -2.99, "volume": 28900000, "market_cap": 1167000000, "high_24h": 4030, "low_24h": 3860, "open_price": 4000, "sector": "Energy", "sector_fa": "انرژی"},
    {"symbol": "IKCO", "name": "Iran Khodro", "name_fa": "خودرو - ایران خودرو", "current_price": 2150, "previous_close": 2080, "change": 70, "change_percent": 3.37, "volume": 89400000, "market_cap": 6450000000, "high_24h": 2190, "low_24h": 2060, "open_price": 2090, "sector": "Automotive", "sector_fa": "خودرو"},
    {"symbol": "SSEP", "name": "Sepah Bank", "name_fa": "وسپه - بانک سپه", "current_price": 1540, "previous_close": 1560, "change": -20, "change_percent": -1.28, "volume": 15600000, "market_cap": 924000000, "high_24h": 1575, "low_24h": 1520, "open_price": 1555, "sector": "Banking", "sector_fa": "بانکداری"},
    {"symbol": "TAPK", "name": "TAPICO Holding", "name_fa": "تاپیکو", "current_price": 9870, "previous_close": 9640, "change": 230, "change_percent": 2.39, "volume": 18200000, "market_cap": 3948000000, "high_24h": 9920, "low_24h": 9600, "open_price": 9650, "sector": "Petrochemical", "sector_fa": "پتروشیمی"},
    {"symbol": "PTRO", "name": "Petrol Group", "name_fa": "پترول - گروه پتروشیمی", "current_price": 5430, "previous_close": 5310, "change": 120, "change_percent": 2.26, "volume": 25700000, "market_cap": 2172000000, "high_24h": 5480, "low_24h": 5280, "open_price": 5320, "sector": "Petrochemical", "sector_fa": "پتروشیمی"},
    {"symbol": "MKBT", "name": "Mobin Telecom", "name_fa": "همراه اول", "current_price": 7250, "previous_close": 7380, "change": -130, "change_percent": -1.76, "volume": 12300000, "market_cap": 4350000000, "high_24h": 7410, "low_24h": 7200, "open_price": 7370, "sector": "Telecom", "sector_fa": "مخابرات"},
    {"symbol": "SSAN", "name": "Saipa Auto", "name_fa": "خساپا - سایپا", "current_price": 1820, "previous_close": 1790, "change": 30, "change_percent": 1.68, "volume": 72100000, "market_cap": 3640000000, "high_24h": 1850, "low_24h": 1780, "open_price": 1795, "sector": "Automotive", "sector_fa": "خودرو"},
    {"symbol": "ZINC", "name": "Iran Zinc Mines", "name_fa": "فزر - زنگان روی", "current_price": 15680, "previous_close": 15200, "change": 480, "change_percent": 3.16, "volume": 8900000, "market_cap": 1568000000, "high_24h": 15750, "low_24h": 15150, "open_price": 15220, "sector": "Metals & Mining", "sector_fa": "فلزات و معادن"},
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
                cash_balance=Decimal("100000000.00"),
            )
            self.stdout.write("  Created liquidity provider user.")

        extra_users = [
            ("user042", "user042@example.com", "Sara", "Mohammadi"),
            ("user015", "user015@example.com", "Reza", "Ahmadi"),
            ("user088", "user088@example.com", "Maryam", "Hosseini"),
            ("user033", "user033@example.com", "Hassan", "Karimi"),
            ("user077", "user077@example.com", "Zahra", "Bahrami"),
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
        """Generate 30-day price history for each stock."""
        if PriceHistory.objects.exists():
            self.stdout.write("  Price history already exists, skipping.")
            return

        today = timezone.now().date()
        for stock in Stock.objects.all():
            price = float(stock.current_price) * 0.85
            entries = []
            for i in range(30, -1, -1):
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
        self.stdout.write(self.style.SUCCESS("  Price history generated (30 days)."))

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

        # Counter orders for transactions
        sell_ord1 = Order.objects.create(user=user042, stock=fold, type="sell", price=8700, quantity=200, filled_quantity=200, status="matched")
        sell_ord3 = Order.objects.create(user=user015, stock=ikco, type="sell", price=2100, quantity=350, filled_quantity=350, status="matched")
        sell_ord4 = Order.objects.create(user=user088, stock=kgdr, type="sell", price=12300, quantity=100, filled_quantity=100, status="matched")

        tapk = Stock.objects.get(symbol="TAPK")
        buy_ord_tapk = Order.objects.create(user=user, stock=tapk, type="buy", price=9500, quantity=300, filled_quantity=300, status="matched")
        sell_ord_tapk = Order.objects.create(user=user033, stock=tapk, type="sell", price=9500, quantity=300, filled_quantity=300, status="matched")

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

        # Liquidity orders - pending SELL + BUY at current price for each stock
        # So Market Buy/Sell orders can execute immediately
        lp = User.objects.filter(email="liquidity@boursechain.ir").first()
        if lp:
            for stock in Stock.objects.all():
                lp.refresh_from_db()
                price = Decimal(str(round(float(stock.current_price), 2)))
                qty = 5000
                # Reserve stock for sell order
                holding, _ = PortfolioHolding.objects.get_or_create(
                    user=lp, stock=stock,
                    defaults={"quantity": 0, "average_buy_price": Decimal("0")},
                )
                if holding.quantity >= qty:
                    holding.quantity -= qty
                    holding.save(update_fields=["quantity"])
                    Order.objects.create(
                        user=lp, stock=stock, type="sell",
                        execution_type="limit", price=price, quantity=qty,
                        status="pending",
                    )
                # Reserve cash for buy order
                total = price * qty
                if lp.cash_balance >= total:
                    lp.cash_balance -= total
                    lp.save(update_fields=["cash_balance"])
                    Order.objects.create(
                        user=lp, stock=stock, type="buy",
                        execution_type="limit", price=price, quantity=qty,
                        status="pending",
                    )
            self.stdout.write("  Liquidity orders created (pending sell+buy per stock).")

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
                        "quantity": 10_000,
                        "average_buy_price": stock.current_price,
                    },
                )

        self.stdout.write(self.style.SUCCESS("  Portfolio holdings created."))

    def _create_notifications(self):
        """Create mock notifications."""
        if Notification.objects.exists():
            self.stdout.write("  Notifications already exist, skipping.")
            return

        user = User.objects.get(email="ali@example.com")

        notifications = [
            {
                "title": "Order Matched",
                "title_fa": "سفارش تطبیق شد",
                "message": "Your buy order for 200 FOLD at 8,700 has been matched.",
                "message_fa": "سفارش خرید ۲۰۰ سهم فولاد با قیمت ۸,۷۰۰ تطبیق شد.",
                "type": "order_matched",
                "read": False,
            },
            {
                "title": "Partial Fill",
                "title_fa": "تطبیق جزئی",
                "message": "350 of 500 shares filled for IKCO buy order at 2,100.",
                "message_fa": "۳۵۰ از ۵۰۰ سهم ایران خودرو با قیمت ۲,۱۰۰ تطبیق شد.",
                "type": "order_matched",
                "read": False,
            },
            {
                "title": "Transaction Confirmed",
                "title_fa": "تراکنش تأیید شد",
                "message": "Transaction TX-001 recorded on blockchain. Hash: 0x8a3b...f7c2",
                "message_fa": "تراکنش TX-001 در بلاکچین ثبت شد. هش: 0x8a3b...f7c2",
                "type": "transaction",
                "read": True,
            },
            {
                "title": "Price Alert",
                "title_fa": "هشدار قیمت",
                "message": "ZINC has surged +3.16% today. Current price: 15,680",
                "message_fa": "فزر امروز ۳.۱۶٪ رشد داشته. قیمت فعلی: ۱۵,۶۸۰",
                "type": "price_alert",
                "read": True,
            },
            {
                "title": "Order Cancelled",
                "title_fa": "سفارش لغو شد",
                "message": "Your sell order for 1000 SSAN at 1,900 has been cancelled.",
                "message_fa": "سفارش فروش ۱,۰۰۰ سهم خساپا با قیمت ۱,۹۰۰ لغو شد.",
                "type": "order_cancelled",
                "read": True,
            },
        ]

        for n in notifications:
            Notification.objects.create(user=user, **n)

        self.stdout.write(self.style.SUCCESS("  Notifications created."))

"""
=============================================================================
BourseChain - تست‌های تراکنش‌ها (Transactions)
=============================================================================
شامل:
  - ساخت تراکنش بعد از match
  - لیست تراکنش‌های کاربر
  - جزئیات تراکنش
  - فرمت پاسخ API

اجرا:
  python manage.py test transactions -v2
=============================================================================
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Notification
from orders.matching import match_order
from orders.models import Order, PortfolioHolding
from stocks.models import Stock

from .models import Transaction

User = get_user_model()


class TransactionTestMixin:
    """داده‌های مشترک."""

    def setUp(self):
        self.stock = Stock.objects.create(
            symbol="FOLD", name="Foolad", name_fa="فولاد مبارکه",
            current_price=Decimal("8750"), previous_close=Decimal("8520"),
            change=Decimal("230"), change_percent=Decimal("2.70"),
            volume=45200000, market_cap=2625000000,
            high_24h=Decimal("8820"), low_24h=Decimal("8490"),
            open_price=Decimal("8530"),
            sector="Metals", sector_fa="فلزات",
        )
        self.buyer = User.objects.create_user(
            username="buyer", email="buyer@test.com",
            password="TestPass1234!", cash_balance=Decimal("50000000"),
        )
        self.seller = User.objects.create_user(
            username="seller", email="seller@test.com",
            password="TestPass1234!", cash_balance=Decimal("10000000"),
        )
        self.seller_holding = PortfolioHolding.objects.create(
            user=self.seller, stock=self.stock,
            quantity=5000, average_buy_price=Decimal("8000"),
        )


# =============================================================================
# 1. تست مدل Transaction
# =============================================================================


class TestTransactionModel(TestCase):
    """تست‌های مدل Transaction."""

    def test_total_value_auto_calculated(self):
        """total_value باید خودکار محاسبه شود."""
        stock = Stock.objects.create(
            symbol="TEST", name="Test", name_fa="تست",
            current_price=1000, previous_close=1000,
            sector="Test", sector_fa="تست",
        )
        buyer = User.objects.create_user(
            username="b", email="b@t.com", password="TestPass1234!",
        )
        seller = User.objects.create_user(
            username="s", email="s@t.com", password="TestPass1234!",
        )
        buy_order = Order.objects.create(
            user=buyer, stock=stock, type="buy",
            price=Decimal("1000"), quantity=100,
        )
        sell_order = Order.objects.create(
            user=seller, stock=stock, type="sell",
            price=Decimal("1000"), quantity=100,
        )
        tx = Transaction.objects.create(
            buy_order=buy_order, sell_order=sell_order,
            stock=stock, price=Decimal("1000"), quantity=100,
            buyer=buyer, seller=seller,
        )

        self.assertEqual(tx.total_value, Decimal("100000"))

    def test_transaction_default_status(self):
        """وضعیت پیش‌فرض تراکنش pending است."""
        stock = Stock.objects.create(
            symbol="TST", name="T", name_fa="ت",
            current_price=100, previous_close=100,
            sector="T", sector_fa="ت",
        )
        buyer = User.objects.create_user(
            username="b2", email="b2@t.com", password="TestPass1234!",
        )
        seller = User.objects.create_user(
            username="s2", email="s2@t.com", password="TestPass1234!",
        )
        buy_order = Order.objects.create(
            user=buyer, stock=stock, type="buy",
            price=100, quantity=10,
        )
        sell_order = Order.objects.create(
            user=seller, stock=stock, type="sell",
            price=100, quantity=10,
        )
        tx = Transaction.objects.create(
            buy_order=buy_order, sell_order=sell_order,
            stock=stock, price=100, quantity=10,
            buyer=buyer, seller=seller,
        )
        self.assertEqual(tx.status, "pending")


# =============================================================================
# 2. تست تراکنش بعد از Match
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestTransactionAfterMatch(TransactionTestMixin, TestCase):
    """تست: Matching Engine باید Transaction صحیح بسازد."""

    def test_transaction_created_on_match(self):
        """بعد از match، Transaction ساخته شود."""
        # رزرو و ساخت سفارشات
        self.seller_holding.quantity -= 100
        self.seller_holding.save()
        sell = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self.buyer.cash_balance -= Decimal("8500") * 100
        self.buyer.save()
        buy = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy.id))

        self.assertEqual(Transaction.objects.count(), 1)
        tx = Transaction.objects.first()
        self.assertEqual(tx.buyer, self.buyer)
        self.assertEqual(tx.seller, self.seller)
        self.assertEqual(tx.stock, self.stock)
        self.assertEqual(tx.quantity, 100)
        self.assertEqual(tx.price, Decimal("8500"))
        self.assertEqual(tx.status, "confirmed")

    def test_multiple_transactions_from_partial_matches(self):
        """Partial matches باید چند Transaction بسازند."""
        for qty in [30, 40, 50]:
            self.seller_holding.quantity -= qty
            self.seller_holding.save()
            Order.objects.create(
                user=self.seller, stock=self.stock,
                type="sell", price=Decimal("8500"), quantity=qty,
            )

        self.buyer.cash_balance -= Decimal("8500") * 100
        self.buyer.save()
        buy = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy.id))

        # 30 + 40 + 30 (از 50) = 100
        self.assertEqual(Transaction.objects.count(), 3)
        total_qty = sum(tx.quantity for tx in Transaction.objects.all())
        self.assertEqual(total_qty, 100)


# =============================================================================
# 3. تست API لیست تراکنش‌ها
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestTransactionListAPI(TransactionTestMixin, APITestCase):
    """تست‌های endpoint لیست تراکنش‌ها."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def _login(self, user):
        response = self.client.post("/api/v1/auth/login/", {
            "email": user.email, "password": "TestPass1234!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def _create_match(self):
        """ساخت یک match تست."""
        self.seller_holding.quantity -= 100
        self.seller_holding.save()
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )
        self.buyer.cash_balance -= Decimal("850000")
        self.buyer.save()
        buy = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )
        match_order(str(buy.id))

    def test_buyer_sees_transactions(self):
        """خریدار تراکنش‌های خودش را ببیند."""
        self._create_match()
        self._login(self.buyer)

        response = self.client.get("/api/v1/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_seller_sees_transactions(self):
        """فروشنده تراکنش‌های خودش را ببیند."""
        self._create_match()
        self._login(self.seller)

        response = self.client.get("/api/v1/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_transaction_response_format(self):
        """فرمت پاسخ تراکنش باید camelCase باشد."""
        self._create_match()
        self._login(self.buyer)

        response = self.client.get("/api/v1/transactions/")
        tx = response.data["results"][0]

        self.assertIn("id", tx)
        self.assertIn("stockSymbol", tx)
        self.assertIn("stockName", tx)
        self.assertIn("totalValue", tx)
        self.assertIn("executedAt", tx)
        self.assertIn("buyerId", tx)
        self.assertIn("sellerId", tx)

    def test_unauthenticated_cannot_view_transactions(self):
        """کاربر بدون لاگین نمی‌تواند تراکنش ببیند."""
        response = self.client.get("/api/v1/transactions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

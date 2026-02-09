"""
=============================================================================
BourseChain - Sprint 3 Tests: Matching Engine + Order System
=============================================================================
تست‌های جامع برای موتور تطبیق سفارشات (Matching Engine)

شامل:
  - تست مدل‌ها (Order, PortfolioHolding)
  - تست الگوریتم Matching Engine (price-time priority)
  - تست API سفارش‌گذاری (ساخت، لغو، لیست)
  - تست API پورتفولیو و دفتر سفارشات

اجرا:
  $env:USE_SQLITE="True"; $env:USE_LOCMEM_CACHE="True"
  python manage.py test orders -v2
  python manage.py test orders.tests.TestMatchingEngine -v2   # فقط matching
=============================================================================
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Notification
from stocks.models import Stock
from transactions.models import Transaction

from .matching import match_order
from .models import Order, PortfolioHolding

User = get_user_model()


# =============================================================================
# Helper Mixin: ساخت داده‌های تست مشترک
# =============================================================================


class OrderTestMixin:
    """داده‌های مشترک برای تمام تست‌ها."""

    def setUp(self):
        """ساخت کاربران و سهام تست."""
        # سهام تست
        self.stock = Stock.objects.create(
            symbol="FOLD",
            name="Foolad Mobarakeh",
            name_fa="فولاد مبارکه",
            current_price=Decimal("8750"),
            previous_close=Decimal("8520"),
            change=Decimal("230"),
            change_percent=Decimal("2.70"),
            volume=45200000,
            market_cap=2625000000,
            high_24h=Decimal("8820"),
            low_24h=Decimal("8490"),
            open_price=Decimal("8530"),
            sector="Metals & Mining",
            sector_fa="فلزات و معادن",
        )

        # خریدار - با موجودی نقدی
        self.buyer = User.objects.create_user(
            username="buyer",
            email="buyer@test.com",
            password="TestPass1234!",
            first_name="Ali",
            last_name="Buyer",
            cash_balance=Decimal("50000000"),  # 50 میلیون ریال
        )

        # فروشنده - با سهام در پورتفولیو
        self.seller = User.objects.create_user(
            username="seller",
            email="seller@test.com",
            password="TestPass1234!",
            first_name="Sara",
            last_name="Seller",
            cash_balance=Decimal("10000000"),  # 10 میلیون ریال
        )

        # دادن سهام به فروشنده
        self.seller_holding = PortfolioHolding.objects.create(
            user=self.seller,
            stock=self.stock,
            quantity=5000,
            average_buy_price=Decimal("8000"),
        )


# =============================================================================
# 1. تست مدل‌ها
# =============================================================================


class TestOrderModel(OrderTestMixin, TestCase):
    """تست‌های مدل Order."""

    def test_remaining_quantity(self):
        """remaining_quantity باید quantity - filled_quantity باشد."""
        order = Order.objects.create(
            user=self.buyer,
            stock=self.stock,
            type="buy",
            price=Decimal("8500"),
            quantity=200,
            filled_quantity=75,
        )
        self.assertEqual(order.remaining_quantity, 125)

    def test_is_fully_filled(self):
        """is_fully_filled وقتی filled >= quantity باید True باشد."""
        order = Order.objects.create(
            user=self.buyer,
            stock=self.stock,
            type="buy",
            price=Decimal("8500"),
            quantity=100,
            filled_quantity=100,
        )
        self.assertTrue(order.is_fully_filled)

    def test_is_not_fully_filled(self):
        """is_fully_filled وقتی filled < quantity باید False باشد."""
        order = Order.objects.create(
            user=self.buyer,
            stock=self.stock,
            type="buy",
            price=Decimal("8500"),
            quantity=100,
            filled_quantity=50,
        )
        self.assertFalse(order.is_fully_filled)

    def test_order_default_status_is_pending(self):
        """وضعیت پیش‌فرض سفارش باید pending باشد."""
        order = Order.objects.create(
            user=self.buyer,
            stock=self.stock,
            type="buy",
            price=Decimal("8500"),
            quantity=100,
        )
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.filled_quantity, 0)

    def test_order_str_representation(self):
        """تست __str__ مدل Order."""
        order = Order.objects.create(
            user=self.buyer,
            stock=self.stock,
            type="buy",
            price=Decimal("8500"),
            quantity=100,
        )
        self.assertIn("Buy", str(order))
        self.assertIn("FOLD", str(order))


class TestPortfolioHoldingModel(OrderTestMixin, TestCase):
    """تست‌های مدل PortfolioHolding."""

    def test_total_value(self):
        """ارزش کل = تعداد × قیمت فعلی سهم."""
        expected = self.seller_holding.quantity * self.stock.current_price
        self.assertEqual(self.seller_holding.total_value, expected)

    def test_profit_loss(self):
        """سود/زیان = ارزش فعلی - سرمایه‌گذاری."""
        total_value = self.seller_holding.quantity * self.stock.current_price
        total_invested = self.seller_holding.quantity * self.seller_holding.average_buy_price
        expected_pl = total_value - total_invested
        self.assertEqual(self.seller_holding.profit_loss, expected_pl)

    def test_profit_loss_percent(self):
        """درصد سود/زیان باید درست محاسبه شود."""
        self.assertGreater(self.seller_holding.profit_loss_percent, 0)


# =============================================================================
# 2. تست Matching Engine - هسته اصلی Sprint 3
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestMatchingEngine(OrderTestMixin, TestCase):
    """
    تست‌های الگوریتم Price-Time Priority Matching Engine.

    الگوریتم:
    - خرید: ابتدا ارزان‌ترین سفارشات فروش match می‌شوند
    - فروش: ابتدا گران‌ترین سفارشات خرید match می‌شوند
    - در قیمت یکسان: سفارش قدیمی‌تر اولویت دارد (FIFO)
    """

    def _reserve_cash(self, user, price, quantity):
        """شبیه‌سازی رزرو پول خریدار."""
        user.cash_balance -= price * quantity
        user.save(update_fields=["cash_balance"])

    def _reserve_stock(self, holding, quantity):
        """شبیه‌سازی رزرو سهام فروشنده."""
        holding.quantity -= quantity
        holding.save(update_fields=["quantity"])

    # ── تست ۱: تطبیق کامل (Exact Match) ──

    def test_exact_match_creates_transaction(self):
        """وقتی خرید و فروش با قیمت و تعداد یکسان وجود دارد، Transaction ساخته شود."""
        # فروشنده: سفارش فروش 100 سهم @ 8500
        self._reserve_stock(self.seller_holding, 100)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        # خریدار: سفارش خرید 100 سهم @ 8500
        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        # اجرای موتور تطبیق
        transactions = match_order(str(buy_order.id))

        # بررسی: یک تراکنش ساخته شده
        self.assertEqual(len(transactions), 1)
        tx = transactions[0]
        self.assertEqual(tx.quantity, 100)
        self.assertEqual(tx.price, Decimal("8500"))
        self.assertEqual(tx.total_value, Decimal("850000"))
        self.assertEqual(tx.status, "confirmed")
        self.assertEqual(tx.buyer, self.buyer)
        self.assertEqual(tx.seller, self.seller)

    def test_exact_match_updates_order_status(self):
        """بعد از تطبیق کامل، هر دو سفارش باید status=matched بشوند."""
        self._reserve_stock(self.seller_holding, 100)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        buy_order.refresh_from_db()
        sell_order.refresh_from_db()
        self.assertEqual(buy_order.status, "matched")
        self.assertEqual(sell_order.status, "matched")
        self.assertEqual(buy_order.filled_quantity, 100)
        self.assertEqual(sell_order.filled_quantity, 100)

    def test_exact_match_updates_cash_balances(self):
        """بعد از تطبیق، پول فروشنده زیاد شود."""
        seller_cash_before = self.seller.cash_balance

        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        self.seller.refresh_from_db()
        expected = seller_cash_before + Decimal("850000")
        self.assertEqual(self.seller.cash_balance, expected)

    def test_exact_match_updates_buyer_portfolio(self):
        """بعد از تطبیق، خریدار سهام را در پورتفولیو دریافت کند."""
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        holding = PortfolioHolding.objects.get(user=self.buyer, stock=self.stock)
        self.assertEqual(holding.quantity, 100)
        self.assertEqual(holding.average_buy_price, Decimal("8500"))

    def test_exact_match_updates_stock_price(self):
        """بعد از تطبیق، قیمت سهم باید به قیمت معامله آپدیت شود."""
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_price, Decimal("8500"))

    def test_exact_match_sends_notifications(self):
        """بعد از تطبیق، به هر دو طرف Notification ارسال شود."""
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        buyer_notifs = Notification.objects.filter(
            user=self.buyer, type="order_matched"
        )
        seller_notifs = Notification.objects.filter(
            user=self.seller, type="order_matched"
        )
        self.assertEqual(buyer_notifs.count(), 1)
        self.assertEqual(seller_notifs.count(), 1)
        # بررسی دوزبانه بودن
        self.assertIn("Bought", buyer_notifs.first().title)
        self.assertIn("خرید", buyer_notifs.first().title_fa)
        self.assertIn("Sold", seller_notifs.first().title)
        self.assertIn("فروش", seller_notifs.first().title_fa)

    # ── تست ۲: تطبیق جزئی (Partial Fill) ──

    def test_partial_fill_buy_larger_than_sell(self):
        """وقتی سفارش خرید بزرگ‌تر از فروش است، فقط بخشی fill شود."""
        self._reserve_stock(self.seller_holding, 50)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=50,
        )

        self._reserve_cash(self.buyer, Decimal("8600"), 200)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8600"), quantity=200,
        )

        transactions = match_order(str(buy_order.id))

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].quantity, 50)

        buy_order.refresh_from_db()
        self.assertEqual(buy_order.status, "partial")
        self.assertEqual(buy_order.filled_quantity, 50)
        self.assertEqual(buy_order.remaining_quantity, 150)

    def test_partial_fill_sell_larger_than_buy(self):
        """وقتی سفارش فروش بزرگ‌تر از خرید است."""
        self._reserve_cash(self.buyer, Decimal("8600"), 30)
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8600"), quantity=30,
        )

        self._reserve_stock(self.seller_holding, 100)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=100,
        )

        transactions = match_order(str(sell_order.id))

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].quantity, 30)

        sell_order.refresh_from_db()
        self.assertEqual(sell_order.status, "partial")
        self.assertEqual(sell_order.filled_quantity, 30)

    # ── تست ۳: عدم تطبیق (No Match) ──

    def test_no_match_when_price_gap(self):
        """وقتی قیمت خرید کمتر از قیمت فروش است، match نباید رخ دهد."""
        # فروشنده: 9000 ریال
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("9000"), quantity=100,
        )

        # خریدار: فقط 8000 ریال
        self._reserve_cash(self.buyer, Decimal("8000"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8000"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))

        self.assertEqual(len(transactions), 0)

        buy_order.refresh_from_db()
        self.assertEqual(buy_order.status, "pending")
        self.assertEqual(buy_order.filled_quantity, 0)

    def test_no_match_when_no_opposing_orders(self):
        """وقتی هیچ سفارش مقابلی وجود ندارد."""
        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))

        self.assertEqual(len(transactions), 0)

    # ── تست ۴: تطبیق چندگانه (Multiple Matches) ──

    def test_one_buy_matches_multiple_sells(self):
        """یک سفارش خرید بزرگ با چند سفارش فروش کوچک match شود."""
        # سه سفارش فروش: 30@8400 + 50@8450 + 40@8500
        for price, qty in [(8400, 30), (8450, 50), (8500, 40)]:
            self._reserve_stock(self.seller_holding, qty)
            Order.objects.create(
                user=self.seller, stock=self.stock,
                type="sell", price=Decimal(str(price)), quantity=qty,
            )

        # سفارش خرید 100 سهم @ 8500 (کل فروش: 120 سهم)
        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))

        # باید 3 تراکنش باشد: 30 + 50 + 20 = 100
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0].quantity, 30)  # 30 @ 8400
        self.assertEqual(transactions[1].quantity, 50)  # 50 @ 8450
        self.assertEqual(transactions[2].quantity, 20)  # 20 @ 8500

        buy_order.refresh_from_db()
        self.assertEqual(buy_order.status, "matched")
        self.assertEqual(buy_order.filled_quantity, 100)

    def test_one_sell_matches_multiple_buys(self):
        """یک سفارش فروش بزرگ با چند سفارش خرید match شود."""
        # سه سفارش خرید (گران‌ترین اول): 40@8700 + 30@8650 + 50@8600
        for price, qty in [(8700, 40), (8650, 30), (8600, 50)]:
            self._reserve_cash(self.buyer, Decimal(str(price)), qty)
            Order.objects.create(
                user=self.buyer, stock=self.stock,
                type="buy", price=Decimal(str(price)), quantity=qty,
            )

        # سفارش فروش 100 سهم @ 8600
        self._reserve_stock(self.seller_holding, 100)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=100,
        )

        transactions = match_order(str(sell_order.id))

        # باید 3 تراکنش: 40 + 30 + 30 = 100
        self.assertEqual(len(transactions), 3)
        total_filled = sum(tx.quantity for tx in transactions)
        self.assertEqual(total_filled, 100)

        sell_order.refresh_from_db()
        self.assertEqual(sell_order.status, "matched")

    # ── تست ۵: اولویت قیمت-زمان (Price-Time Priority) ──

    def test_cheapest_sell_matched_first(self):
        """ارزان‌ترین سفارش فروش اول match شود."""
        # فروش گران‌تر اول ثبت شده
        self._reserve_stock(self.seller_holding, 100)
        expensive_sell = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=100,
        )

        # فروش ارزان‌تر بعد ثبت شده
        self._reserve_stock(self.seller_holding, 100)
        cheap_sell = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8400"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8700"), 50)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8700"), quantity=50,
        )

        transactions = match_order(str(buy_order.id))

        # باید با ارزان‌ترین (8400) match بشه
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].price, Decimal("8400"))

        # فروش ارزان fill شده، گران نشده
        cheap_sell.refresh_from_db()
        expensive_sell.refresh_from_db()
        self.assertEqual(cheap_sell.filled_quantity, 50)
        self.assertEqual(expensive_sell.filled_quantity, 0)

    def test_highest_buy_matched_first(self):
        """گران‌ترین سفارش خرید اول match شود."""
        # خرید ارزان اول
        self._reserve_cash(self.buyer, Decimal("8400"), 100)
        low_buy = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8400"), quantity=100,
        )

        # خرید گران بعد
        self._reserve_cash(self.buyer, Decimal("8700"), 100)
        high_buy = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8700"), quantity=100,
        )

        self._reserve_stock(self.seller_holding, 50)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8300"), quantity=50,
        )

        transactions = match_order(str(sell_order.id))

        # باید با گران‌ترین (8700) match بشه
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].price, Decimal("8700"))

        high_buy.refresh_from_db()
        low_buy.refresh_from_db()
        self.assertEqual(high_buy.filled_quantity, 50)
        self.assertEqual(low_buy.filled_quantity, 0)

    # ── تست ۶: جلوگیری از معامله با خود (Self-Trade Prevention) ──

    def test_self_trade_prevention(self):
        """کاربر نمی‌تواند با خودش معامله کند."""
        # خریدار هم سهام دارد
        PortfolioHolding.objects.create(
            user=self.buyer,
            stock=self.stock,
            quantity=500,
            average_buy_price=Decimal("8000"),
        )

        # خریدار یک سفارش فروش و یک سفارش خرید ثبت می‌کند
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))

        # نباید match بشه
        self.assertEqual(len(transactions), 0)

    # ── تست ۷: Execution Price (قیمت maker) ──

    def test_execution_price_is_maker_price(self):
        """قیمت اجرا باید قیمت maker (سفارش قدیمی‌تر) باشد."""
        # فروشنده اول ثبت (maker) @ 8400
        self._reserve_stock(self.seller_holding, 100)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8400"), quantity=100,
        )

        # خریدار بعد ثبت (taker) @ 8700
        self._reserve_cash(self.buyer, Decimal("8700"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8700"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))

        # قیمت اجرا = قیمت فروشنده (maker) = 8400
        self.assertEqual(transactions[0].price, Decimal("8400"))

    def test_buyer_gets_refund_when_execution_price_lower(self):
        """وقتی قیمت اجرا کمتر از قیمت خرید است، مابه‌التفاوت برگشت بشه."""
        buyer_cash_before = self.buyer.cash_balance

        # فروش @ 8400 (maker)
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8400"), quantity=100,
        )

        # خرید @ 8700 → رزرو 8700×100 = 870,000
        self._reserve_cash(self.buyer, Decimal("8700"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8700"), quantity=100,
        )

        match_order(str(buy_order.id))

        self.buyer.refresh_from_db()
        # خریدار: 870,000 رزرو شد - اجرا 840,000 = 30,000 برگشت
        # نهایی: buyer_cash_before - 870,000 + 30,000 = buyer_cash_before - 840,000
        expected = buyer_cash_before - Decimal("840000")
        self.assertEqual(self.buyer.cash_balance, expected)

    # ── تست ۸: تطبیق با سفارشات مختلف سهام ──

    def test_no_cross_stock_matching(self):
        """سفارشات سهام‌های مختلف نباید با هم match شوند."""
        other_stock = Stock.objects.create(
            symbol="SHPN",
            name="Pars Oil",
            name_fa="شپنا",
            current_price=Decimal("4320"),
            previous_close=Decimal("4480"),
            sector="Energy",
            sector_fa="انرژی",
        )

        # فروش سهم دیگر
        PortfolioHolding.objects.create(
            user=self.seller, stock=other_stock,
            quantity=1000, average_buy_price=Decimal("4000"),
        )
        Order.objects.create(
            user=self.seller, stock=other_stock,
            type="sell", price=Decimal("4300"), quantity=100,
        )

        # خرید FOLD (نه SHPN)
        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        transactions = match_order(str(buy_order.id))
        self.assertEqual(len(transactions), 0)

    # ── تست ۹: حجم معاملات (Volume Update) ──

    def test_stock_volume_updated_after_match(self):
        """حجم معاملات سهم باید بعد از match افزایش یابد."""
        volume_before = self.stock.volume

        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8500"), quantity=100,
        )

        self._reserve_cash(self.buyer, Decimal("8500"), 100)
        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )

        match_order(str(buy_order.id))

        self.stock.refresh_from_db()
        self.assertEqual(self.stock.volume, volume_before + 100)

    # ── تست ۱۰: Weighted Average Price ──

    def test_buyer_holding_weighted_average_price(self):
        """میانگین وزنی قیمت خرید باید درست محاسبه شود."""
        # خرید اول: 100 @ 8400
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8400"), quantity=100,
        )
        self._reserve_cash(self.buyer, Decimal("8400"), 100)
        buy1 = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8400"), quantity=100,
        )
        match_order(str(buy1.id))

        # خرید دوم: 100 @ 8600
        self._reserve_stock(self.seller_holding, 100)
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=100,
        )
        self._reserve_cash(self.buyer, Decimal("8600"), 100)
        buy2 = Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8600"), quantity=100,
        )
        match_order(str(buy2.id))

        holding = PortfolioHolding.objects.get(user=self.buyer, stock=self.stock)
        self.assertEqual(holding.quantity, 200)
        # میانگین وزنی: (100×8400 + 100×8600) / 200 = 8500
        self.assertEqual(holding.average_buy_price, Decimal("8500"))


# =============================================================================
# 3. تست API سفارش‌گذاری
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderCreateAPI(OrderTestMixin, APITestCase):
    """تست‌های API ساخت سفارش از طریق endpoint."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def _login(self, user):
        """گرفتن JWT token و تنظیم در client."""
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TestPass1234!"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_buy_order_reserves_cash(self):
        """ساخت سفارش خرید باید پول را رزرو (کسر) کند."""
        self._login(self.buyer)
        cash_before = self.buyer.cash_balance

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.buyer.refresh_from_db()
        expected = cash_before - Decimal("850000")
        self.assertEqual(self.buyer.cash_balance, expected)

    def test_create_sell_order_reserves_stock(self):
        """ساخت سفارش فروش باید سهام را رزرو (کسر) کند."""
        self._login(self.seller)
        holding_before = self.seller_holding.quantity

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "8800.00",
            "quantity": 200,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.seller_holding.refresh_from_db()
        self.assertEqual(self.seller_holding.quantity, holding_before - 200)

    def test_buy_order_insufficient_cash(self):
        """سفارش خرید با موجودی ناکافی باید خطا بدهد."""
        self._login(self.buyer)

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100000,  # 850,000,000 > 50,000,000
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_sell_order_insufficient_holdings(self):
        """سفارش فروش بیشتر از موجودی سهام باید خطا بدهد."""
        self._login(self.seller)

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "8800.00",
            "quantity": 99999,  # بیشتر از 5000
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_order_invalid_stock(self):
        """سفارش برای سهام نامعتبر باید 404 بدهد."""
        self._login(self.buyer)

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "INVALID",
            "type": "buy",
            "price": "1000.00",
            "quantity": 10,
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_triggers_matching(self):
        """ساخت سفارش باید Matching Engine را trigger کند."""
        # فروشنده سفارش فروش ثبت کرده
        self._login(self.seller)
        self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "8500.00",
            "quantity": 100,
        })

        # خریدار سفارش خرید ثبت می‌کند → باید auto-match بشه
        self._login(self.buyer)
        self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })

        # بررسی: Transaction ساخته شده
        self.assertEqual(Transaction.objects.count(), 1)
        tx = Transaction.objects.first()
        self.assertEqual(tx.quantity, 100)

    def test_unauthenticated_cannot_create_order(self):
        """کاربر بدون لاگین نمی‌تواند سفارش ثبت کند."""
        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_response_format(self):
        """پاسخ API باید camelCase و فرمت صحیح داشته باشد."""
        self._login(self.buyer)

        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })

        data = response.data
        self.assertIn("id", data)
        self.assertIn("stockSymbol", data)
        self.assertIn("filledQuantity", data)
        self.assertIn("createdAt", data)
        self.assertEqual(data["stockSymbol"], "FOLD")
        self.assertEqual(data["type"], "buy")
        self.assertEqual(data["status"], "pending")


# =============================================================================
# 4. تست API لغو سفارش و بازگشت پول/سهام
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderCancelAPI(OrderTestMixin, APITestCase):
    """تست‌های لغو سفارش و refund."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def _login(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TestPass1234!"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_cancel_buy_order_refunds_cash(self):
        """لغو سفارش خرید باید پول رزرو شده را برگرداند."""
        self._login(self.buyer)
        cash_before = self.buyer.cash_balance

        # ساخت سفارش
        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })
        order_id = response.data["id"]

        # لغو سفارش
        cancel_resp = self.client.put(f"/api/v1/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_resp.data["status"], "cancelled")

        # بررسی: پول برگشت داده شده
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.cash_balance, cash_before)

    def test_cancel_sell_order_returns_stock(self):
        """لغو سفارش فروش باید سهام رزرو شده را برگرداند."""
        self._login(self.seller)
        holding_before = self.seller_holding.quantity

        # ساخت سفارش فروش
        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "9000.00",
            "quantity": 200,
        })
        order_id = response.data["id"]

        # لغو
        self.client.put(f"/api/v1/orders/{order_id}/cancel/")

        self.seller_holding.refresh_from_db()
        self.assertEqual(self.seller_holding.quantity, holding_before)

    def test_cannot_cancel_matched_order(self):
        """سفارش matched نباید قابل لغو باشد."""
        self._login(self.seller)
        self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "8500.00",
            "quantity": 100,
        })

        self._login(self.buyer)
        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })
        order_id = response.data["id"]

        # تلاش لغو سفارش matched
        cancel_resp = self.client.put(f"/api/v1/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_cancel_other_users_order(self):
        """هر کاربر فقط سفارش خودش را لغو کند."""
        self._login(self.buyer)
        response = self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })
        order_id = response.data["id"]

        # فروشنده تلاش لغو سفارش خریدار
        self._login(self.seller)
        cancel_resp = self.client.put(f"/api/v1/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, status.HTTP_404_NOT_FOUND)


# =============================================================================
# 5. تست API لیست سفارشات
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderListAPI(OrderTestMixin, APITestCase):
    """تست‌های لیست سفارشات."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def _login(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TestPass1234!"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_own_orders_only(self):
        """هر کاربر فقط سفارشات خودش را ببیند."""
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8800"), quantity=50,
        )

        self._login(self.buyer)
        response = self.client.get("/api/v1/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_orders_by_type(self):
        """فیلتر سفارشات بر اساس نوع (buy/sell)."""
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
        )
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8600"), quantity=50,
        )

        self._login(self.buyer)
        response = self.client.get("/api/v1/orders/?type=buy")
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_orders_by_status(self):
        """فیلتر سفارشات بر اساس وضعیت."""
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=100,
            status="pending",
        )
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8600"), quantity=50,
            status="matched", filled_quantity=50,
        )

        self._login(self.buyer)

        pending = self.client.get("/api/v1/orders/?status=pending")
        self.assertEqual(len(pending.data["results"]), 1)

        matched = self.client.get("/api/v1/orders/?status=matched")
        self.assertEqual(len(matched.data["results"]), 1)


# =============================================================================
# 6. تست API پورتفولیو
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestPortfolioAPI(OrderTestMixin, APITestCase):
    """تست‌های API پورتفولیو."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def _login(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "TestPass1234!"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_portfolio_response_structure(self):
        """ساختار پاسخ portfolio باید صحیح باشد."""
        self._login(self.seller)
        response = self.client.get("/api/v1/orders/portfolio/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("userId", data)
        self.assertIn("holdings", data)
        self.assertIn("totalValue", data)
        self.assertIn("totalInvested", data)
        self.assertIn("totalProfitLoss", data)
        self.assertIn("cashBalance", data)

    def test_portfolio_shows_holdings(self):
        """پورتفولیو باید سهام‌دار را نشان دهد."""
        self._login(self.seller)
        response = self.client.get("/api/v1/orders/portfolio/")

        self.assertEqual(len(response.data["holdings"]), 1)
        holding = response.data["holdings"][0]
        self.assertEqual(holding["stockSymbol"], "FOLD")
        self.assertEqual(holding["quantity"], 5000)

    def test_portfolio_updates_after_match(self):
        """پورتفولیو باید بعد از match آپدیت شود."""
        # فروشنده 100 سهم می‌فروشد
        self._login(self.seller)
        self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "sell",
            "price": "8500.00",
            "quantity": 100,
        })

        # خریدار 100 سهم می‌خرد
        self._login(self.buyer)
        self.client.post("/api/v1/orders/create/", {
            "stock_symbol": "FOLD",
            "type": "buy",
            "price": "8500.00",
            "quantity": 100,
        })

        # بررسی پورتفولیو خریدار
        response = self.client.get("/api/v1/orders/portfolio/")
        holdings = response.data["holdings"]
        self.assertTrue(any(h["stockSymbol"] == "FOLD" for h in holdings))


# =============================================================================
# 7. تست API دفتر سفارشات (Order Book)
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderBookAPI(OrderTestMixin, APITestCase):
    """تست‌های API دفتر سفارشات."""

    def test_order_book_structure(self):
        """ساختار Order Book باید صحیح باشد."""
        response = self.client.get(f"/api/v1/orders/book/{self.stock.symbol}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("symbol", data)
        self.assertIn("bids", data)
        self.assertIn("asks", data)
        self.assertIn("spread", data)
        self.assertIn("spreadPercent", data)
        self.assertEqual(data["symbol"], "FOLD")

    def test_order_book_shows_pending_orders(self):
        """Order Book باید سفارشات pending را نشان دهد."""
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8400"), quantity=100,
        )
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=200,
        )

        response = self.client.get(f"/api/v1/orders/book/{self.stock.symbol}/")
        data = response.data

        self.assertEqual(len(data["bids"]), 1)
        self.assertEqual(len(data["asks"]), 1)
        self.assertEqual(data["bids"][0]["quantity"], 100)
        self.assertEqual(data["asks"][0]["quantity"], 200)

    def test_order_book_shows_remaining_quantity(self):
        """Order Book باید مقدار باقی‌مانده (remaining) را نشان دهد."""
        # سفارشی با partial fill
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8500"), quantity=200,
            filled_quantity=80, status="partial",
        )

        response = self.client.get(f"/api/v1/orders/book/{self.stock.symbol}/")
        bids = response.data["bids"]

        self.assertEqual(len(bids), 1)
        self.assertEqual(bids[0]["quantity"], 120)  # 200 - 80 = 120

    def test_order_book_invalid_stock(self):
        """Order Book برای سهام نامعتبر باید 404 بدهد."""
        response = self.client.get("/api/v1/orders/book/INVALID/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_book_spread_calculation(self):
        """Spread باید فاصله بین بهترین bid و ask باشد."""
        Order.objects.create(
            user=self.buyer, stock=self.stock,
            type="buy", price=Decimal("8400"), quantity=100,
        )
        Order.objects.create(
            user=self.seller, stock=self.stock,
            type="sell", price=Decimal("8600"), quantity=100,
        )

        response = self.client.get(f"/api/v1/orders/book/{self.stock.symbol}/")
        data = response.data

        self.assertEqual(data["spread"], 200.0)  # 8600 - 8400

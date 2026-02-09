"""
=============================================================================
BourseChain - تست‌های اعلان‌ها (Notifications)
=============================================================================
شامل:
  - اعلان بعد از match (دوزبانه FA/EN)
  - لیست اعلان‌ها
  - علامت‌گذاری خوانده شده
  - شمارش خوانده نشده

اجرا:
  python manage.py test notifications -v2
=============================================================================
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from orders.matching import match_order
from orders.models import Order, PortfolioHolding
from stocks.models import Stock

from .models import Notification

User = get_user_model()


class NotificationTestMixin:
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
# 1. تست مدل Notification
# =============================================================================


class TestNotificationModel(TestCase):
    """تست‌های مدل Notification."""

    def test_notification_creation(self):
        """ساخت اعلان دوزبانه."""
        user = User.objects.create_user(
            username="notifuser", email="n@test.com",
            password="TestPass1234!",
        )
        notif = Notification.objects.create(
            user=user,
            title="Order Matched",
            title_fa="سفارش تطبیق شد",
            message="Your order was matched.",
            message_fa="سفارش شما تطبیق شد.",
            type="order_matched",
        )

        self.assertFalse(notif.read)
        self.assertEqual(notif.type, "order_matched")
        self.assertIn("تطبیق", notif.title_fa)

    def test_notification_default_unread(self):
        """اعلان جدید باید خوانده نشده باشد."""
        user = User.objects.create_user(
            username="nu", email="nu@t.com", password="TestPass1234!",
        )
        notif = Notification.objects.create(
            user=user,
            title="Test", title_fa="تست",
            message="Test", message_fa="تست",
            type="system",
        )
        self.assertFalse(notif.read)


# =============================================================================
# 2. تست اعلان بعد از Match
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestNotificationAfterMatch(NotificationTestMixin, TestCase):
    """تست: بعد از match، اعلان دوزبانه به هر دو طرف ارسال شود."""

    def _create_match(self):
        """ساخت یک match."""
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

    def test_buyer_receives_notification(self):
        """خریدار بعد از match اعلان دریافت کند."""
        self._create_match()

        notifs = Notification.objects.filter(user=self.buyer, type="order_matched")
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Bought", notifs.first().title)
        self.assertIn("100", notifs.first().title)

    def test_seller_receives_notification(self):
        """فروشنده بعد از match اعلان دریافت کند."""
        self._create_match()

        notifs = Notification.objects.filter(user=self.seller, type="order_matched")
        self.assertEqual(notifs.count(), 1)
        self.assertIn("Sold", notifs.first().title)

    def test_notifications_are_bilingual(self):
        """اعلان‌ها باید دوزبانه (FA/EN) باشند."""
        self._create_match()

        notif = Notification.objects.filter(user=self.buyer).first()
        # انگلیسی
        self.assertTrue(len(notif.title) > 0)
        self.assertTrue(len(notif.message) > 0)
        # فارسی
        self.assertTrue(len(notif.title_fa) > 0)
        self.assertTrue(len(notif.message_fa) > 0)
        self.assertIn("خرید", notif.title_fa)
        self.assertIn("فولاد", notif.message_fa)

    def test_notifications_are_unread_by_default(self):
        """اعلان‌های match باید خوانده نشده باشند."""
        self._create_match()

        for notif in Notification.objects.all():
            self.assertFalse(notif.read)


# =============================================================================
# 3. تست API اعلان‌ها
# =============================================================================


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestNotificationAPI(NotificationTestMixin, APITestCase):
    """تست‌های endpoint اعلان‌ها."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # ساخت چند اعلان تست
        for i in range(3):
            Notification.objects.create(
                user=self.buyer,
                title=f"Test Notification {i}",
                title_fa=f"اعلان تست {i}",
                message=f"Message {i}",
                message_fa=f"پیام {i}",
                type="system",
                read=(i == 0),  # اولی خوانده شده
            )

    def _login(self, user):
        response = self.client.post("/api/v1/auth/login/", {
            "email": user.email, "password": "TestPass1234!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_list_notifications(self):
        """لیست اعلان‌های کاربر."""
        self._login(self.buyer)
        response = self.client.get("/api/v1/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_unread_count(self):
        """شمارش اعلان‌های خوانده نشده."""
        self._login(self.buyer)
        response = self.client.get("/api/v1/notifications/unread-count/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unreadCount"], 2)

    def test_mark_all_read(self):
        """علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده."""
        self._login(self.buyer)
        response = self.client.post("/api/v1/notifications/mark-all-read/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # بررسی: همه خوانده شده
        unread = Notification.objects.filter(user=self.buyer, read=False).count()
        self.assertEqual(unread, 0)

    def test_notification_response_format(self):
        """فرمت پاسخ اعلان باید camelCase باشد."""
        self._login(self.buyer)
        response = self.client.get("/api/v1/notifications/")
        notif = response.data["results"][0]

        self.assertIn("id", notif)
        self.assertIn("title", notif)
        self.assertIn("titleFa", notif)
        self.assertIn("message", notif)
        self.assertIn("messageFa", notif)
        self.assertIn("type", notif)
        self.assertIn("read", notif)
        self.assertIn("createdAt", notif)

    def test_only_own_notifications(self):
        """هر کاربر فقط اعلان‌های خودش را ببیند."""
        self._login(self.seller)
        response = self.client.get("/api/v1/notifications/")

        # فروشنده اعلانی ندارد
        self.assertEqual(len(response.data["results"]), 0)

    def test_unauthenticated_cannot_view(self):
        """کاربر بدون لاگین نمی‌تواند اعلان ببیند."""
        response = self.client.get("/api/v1/notifications/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

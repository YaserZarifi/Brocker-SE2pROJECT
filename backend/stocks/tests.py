"""
=============================================================================
BourseChain - تست‌های سهام (Stocks)
=============================================================================
شامل:
  - لیست سهام
  - جزئیات سهام
  - آمار بازار
  - آپدیت قیمت

اجرا:
  python manage.py test stocks -v2
=============================================================================
"""

from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import PriceHistory, Stock


# =============================================================================
# 1. تست مدل Stock
# =============================================================================


class TestStockModel(TestCase):
    """تست‌های مدل Stock."""

    def setUp(self):
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

    def test_stock_creation(self):
        """ساخت سهام با اطلاعات صحیح."""
        self.assertEqual(self.stock.symbol, "FOLD")
        self.assertEqual(self.stock.current_price, Decimal("8750"))
        self.assertTrue(self.stock.is_active)

    def test_stock_str(self):
        """تست __str__ مدل Stock."""
        self.assertIn("FOLD", str(self.stock))
        self.assertIn("Foolad", str(self.stock))

    def test_update_price(self):
        """تست آپدیت قیمت سهم."""
        old_price = self.stock.current_price
        self.stock.update_price(Decimal("9000"))

        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_price, Decimal("9000"))
        self.assertEqual(self.stock.previous_close, old_price)
        self.assertEqual(self.stock.change, Decimal("250"))  # 9000 - 8750

    def test_update_price_calculates_percent(self):
        """درصد تغییر قیمت باید درست محاسبه شود."""
        self.stock.update_price(Decimal("9000"))
        self.stock.refresh_from_db()

        # change_percent = (9000-8750)/8750 * 100 ≈ 2.857%
        expected_pct = (Decimal("250") / Decimal("8750")) * 100
        self.assertAlmostEqual(
            float(self.stock.change_percent),
            float(expected_pct),
            places=2,
        )

    def test_symbol_is_unique(self):
        """نماد سهم باید یکتا باشد."""
        with self.assertRaises(Exception):
            Stock.objects.create(
                symbol="FOLD",
                name="Duplicate",
                name_fa="تکراری",
                current_price=1000,
                previous_close=1000,
                sector="Test",
                sector_fa="تست",
            )


# =============================================================================
# 2. تست API لیست سهام
# =============================================================================


class TestStockListAPI(APITestCase):
    """تست‌های endpoint لیست سهام."""

    def setUp(self):
        Stock.objects.create(
            symbol="FOLD", name="Foolad Mobarakeh", name_fa="فولاد مبارکه",
            current_price=8750, previous_close=8520, change=230,
            change_percent=2.70, volume=45200000, market_cap=2625000000,
            sector="Metals", sector_fa="فلزات",
        )
        Stock.objects.create(
            symbol="SHPN", name="Pars Oil", name_fa="شپنا",
            current_price=4320, previous_close=4480, change=-160,
            change_percent=-3.57, volume=38100000, market_cap=1296000000,
            sector="Energy", sector_fa="انرژی",
        )

    def test_list_stocks_no_auth_required(self):
        """لیست سهام نیاز به لاگین ندارد."""
        response = self.client.get("/api/v1/stocks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_stocks_returns_all(self):
        """لیست باید همه سهام فعال را برگرداند."""
        response = self.client.get("/api/v1/stocks/")
        self.assertEqual(len(response.data), 2)

    def test_list_stocks_hides_inactive(self):
        """سهام غیرفعال در لیست نباید باشد."""
        Stock.objects.create(
            symbol="DEAD", name="Inactive", name_fa="غیرفعال",
            current_price=0, previous_close=0,
            sector="Test", sector_fa="تست", is_active=False,
        )

        response = self.client.get("/api/v1/stocks/")
        symbols = [s["symbol"] for s in response.data]
        self.assertNotIn("DEAD", symbols)

    def test_stock_response_format_camelcase(self):
        """پاسخ API باید camelCase باشد."""
        response = self.client.get("/api/v1/stocks/")
        stock = response.data[0]
        self.assertIn("symbol", stock)
        self.assertIn("currentPrice", stock)
        self.assertIn("changePercent", stock)


# =============================================================================
# 3. تست API جزئیات سهم
# =============================================================================


class TestStockDetailAPI(APITestCase):
    """تست‌های endpoint جزئیات سهم."""

    def setUp(self):
        Stock.objects.create(
            symbol="FOLD", name="Foolad Mobarakeh", name_fa="فولاد مبارکه",
            current_price=8750, previous_close=8520, change=230,
            change_percent=2.70, volume=45200000, market_cap=2625000000,
            sector="Metals", sector_fa="فلزات",
        )

    def test_get_stock_detail(self):
        """دریافت جزئیات سهم با نماد."""
        response = self.client.get("/api/v1/stocks/FOLD/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "FOLD")

    def test_stock_not_found(self):
        """سهم ناموجود باید 404 بدهد."""
        response = self.client.get("/api/v1/stocks/INVALID/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# =============================================================================
# 4. تست API آمار بازار
# =============================================================================


class TestMarketStatsAPI(APITestCase):
    """تست‌های endpoint آمار بازار."""

    def setUp(self):
        Stock.objects.create(
            symbol="FOLD", name="Foolad", name_fa="فولاد",
            current_price=8750, previous_close=8520, change=230,
            change_percent=2.70, volume=45200000, market_cap=2625000000,
            sector="Metals", sector_fa="فلزات",
        )
        Stock.objects.create(
            symbol="SHPN", name="Pars Oil", name_fa="شپنا",
            current_price=4320, previous_close=4480, change=-160,
            change_percent=-3.57, volume=38100000, market_cap=1296000000,
            sector="Energy", sector_fa="انرژی",
        )

    def test_market_stats_no_auth(self):
        """آمار بازار نیاز به لاگین ندارد."""
        response = self.client.get("/api/v1/stocks/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_market_stats_structure(self):
        """ساختار آمار بازار."""
        response = self.client.get("/api/v1/stocks/stats/")
        data = response.data

        self.assertIn("totalStocks", data)
        self.assertIn("gainers", data)
        self.assertIn("losers", data)
        self.assertIn("totalVolume", data)
        self.assertEqual(data["totalStocks"], 2)
        self.assertEqual(data["gainers"], 1)   # FOLD
        self.assertEqual(data["losers"], 1)    # SHPN


# =============================================================================
# 5. تست WebSocket Consumer سهام (Sprint 5)
# =============================================================================


from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TransactionTestCase, override_settings


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
class TestStockPriceWebSocket(TransactionTestCase):
    """تست‌های WebSocket consumer قیمت سهام (Sprint 5)."""

    async def _get_communicator(self):
        from stocks.consumers import StockPriceConsumer
        from channels.routing import URLRouter
        from django.urls import path

        app = URLRouter([path("ws/stocks/", StockPriceConsumer.as_asgi())])
        return WebsocketCommunicator(app, "/ws/stocks/")

    async def test_public_connection(self):
        """هر کسی بدون احراز هویت باید بتواند وصل شود."""
        communicator = await self._get_communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_receive_stock_price_update(self):
        """آپدیت قیمت سهم از طریق channel layer باید به client برسد."""
        communicator = await self._get_communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Broadcast stock price update via channel layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "stock_prices",
            {
                "type": "stock.price.update",
                "data": {
                    "symbol": "FOLD",
                    "currentPrice": 9000.0,
                    "previousClose": 8750.0,
                    "change": 250.0,
                    "changePercent": 2.86,
                    "volume": 46000000,
                    "high24h": 9050.0,
                    "low24h": 8600.0,
                },
            },
        )

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "stock_update")
        self.assertEqual(response["data"]["symbol"], "FOLD")
        self.assertEqual(response["data"]["currentPrice"], 9000.0)
        self.assertEqual(response["data"]["change"], 250.0)

        await communicator.disconnect()

    async def test_multiple_clients_receive_update(self):
        """چند client باید همزمان آپدیت دریافت کنند."""
        comm1 = await self._get_communicator()
        comm2 = await self._get_communicator()

        connected1, _ = await comm1.connect()
        connected2, _ = await comm2.connect()
        self.assertTrue(connected1)
        self.assertTrue(connected2)

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "stock_prices",
            {
                "type": "stock.price.update",
                "data": {"symbol": "SHPN", "currentPrice": 4500.0},
            },
        )

        resp1 = await comm1.receive_json_from()
        resp2 = await comm2.receive_json_from()

        self.assertEqual(resp1["data"]["symbol"], "SHPN")
        self.assertEqual(resp2["data"]["symbol"], "SHPN")

        await comm1.disconnect()
        await comm2.disconnect()


# =============================================================================
# 6. تست broadcast utility سهام (Sprint 5)
# =============================================================================


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
)
class TestStockPriceBroadcast(TestCase):
    """تست broadcast قیمت سهم از طریق utility function."""

    def setUp(self):
        self.stock = Stock.objects.create(
            symbol="FOLD", name="Foolad", name_fa="فولاد مبارکه",
            current_price=Decimal("9000"), previous_close=Decimal("8750"),
            change=Decimal("250"), change_percent=Decimal("2.86"),
            volume=46000000, market_cap=2700000000,
            high_24h=Decimal("9050"), low_24h=Decimal("8600"),
            open_price=Decimal("8530"),
            sector="Metals", sector_fa="فلزات",
        )

    def test_broadcast_stock_price_does_not_raise(self):
        """broadcast_stock_price نباید exception ایجاد کند."""
        from stocks.utils import broadcast_stock_price
        broadcast_stock_price(self.stock)

    def test_broadcast_returns_without_error(self):
        """broadcast حتی بدون consumer متصل باید بدون خطا اجرا شود."""
        from stocks.utils import broadcast_stock_price
        try:
            broadcast_stock_price(self.stock)
        except Exception:
            self.fail("broadcast_stock_price raised an exception")

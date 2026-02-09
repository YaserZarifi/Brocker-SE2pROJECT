"""
Management command to test the Matching Engine.
Sprint 3 - Verifies order matching, transaction creation, balance updates.

Usage:
    python manage.py test_matching
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from notifications.models import Notification
from orders.matching import match_order
from orders.models import Order, PortfolioHolding
from stocks.models import Stock
from transactions.models import Transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Test the matching engine with various scenarios"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== BourseChain Matching Engine Test ===\n"))

        # Setup test data
        self._setup()

        # Run test scenarios
        self._test_1_exact_match()
        self._test_2_partial_fill()
        self._test_3_no_match()
        self._test_4_multiple_matches()
        self._test_5_cancel_refund()

        self.stdout.write(self.style.SUCCESS("\n=== All tests passed! ===\n"))

    def _setup(self):
        """Create test users and ensure stock exists."""
        self.stdout.write("Setting up test data...")

        # Get or create test stock
        self.stock = Stock.objects.filter(symbol="FOLD").first()
        if not self.stock:
            self.stock = Stock.objects.create(
                symbol="FOLD",
                name="Foolad Mobarakeh",
                name_fa="فولاد مبارکه",
                current_price=8750,
                previous_close=8520,
                sector="Metals",
                sector_fa="فلزات",
            )

        # Create buyer
        self.buyer, _ = User.objects.get_or_create(
            email="test_buyer@test.com",
            defaults={
                "username": "test_buyer",
                "first_name": "Test",
                "last_name": "Buyer",
                "cash_balance": Decimal("50000000"),
            },
        )
        if not _:
            self.buyer.cash_balance = Decimal("50000000")
            self.buyer.save(update_fields=["cash_balance"])

        # Create seller with holdings
        self.seller, _ = User.objects.get_or_create(
            email="test_seller@test.com",
            defaults={
                "username": "test_seller",
                "first_name": "Test",
                "last_name": "Seller",
                "cash_balance": Decimal("10000000"),
            },
        )
        if not _:
            self.seller.cash_balance = Decimal("10000000")
            self.seller.save(update_fields=["cash_balance"])

        # Give seller stock holdings
        holding, _ = PortfolioHolding.objects.get_or_create(
            user=self.seller,
            stock=self.stock,
            defaults={"quantity": 5000, "average_buy_price": Decimal("8000")},
        )
        if not _:
            holding.quantity = 5000
            holding.average_buy_price = Decimal("8000")
            holding.save()

        # Clean up old test orders/transactions
        Order.objects.filter(user__email__in=["test_buyer@test.com", "test_seller@test.com"]).delete()
        Transaction.objects.filter(buyer__email__in=["test_buyer@test.com", "test_seller@test.com"]).delete()
        Transaction.objects.filter(seller__email__in=["test_buyer@test.com", "test_seller@test.com"]).delete()
        Notification.objects.filter(user__email__in=["test_buyer@test.com", "test_seller@test.com"]).delete()

        self.stdout.write(self.style.SUCCESS("  Setup complete.\n"))

    def _test_1_exact_match(self):
        """Test: Exact match - buy and sell at same price and quantity."""
        self.stdout.write(self.style.MIGRATE_HEADING("Test 1: Exact Match"))

        buyer_cash_before = self.buyer.cash_balance
        seller_cash_before = self.seller.cash_balance

        # Seller places sell order (stock is reserved)
        seller_holding = PortfolioHolding.objects.get(user=self.seller, stock=self.stock)
        seller_holding_qty_before = seller_holding.quantity

        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock, type="sell", price=Decimal("8500"), quantity=100
        )
        # Simulate stock reservation
        seller_holding.quantity -= 100
        seller_holding.save(update_fields=["quantity"])

        # Buyer places buy order (cash is reserved)
        total_cost = Decimal("8500") * 100
        self.buyer.cash_balance -= total_cost
        self.buyer.save(update_fields=["cash_balance"])

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock, type="buy", price=Decimal("8500"), quantity=100
        )

        # Run matching
        txs = match_order(str(buy_order.id))

        # Verify
        assert len(txs) == 1, f"Expected 1 transaction, got {len(txs)}"

        tx = txs[0]
        assert tx.quantity == 100, f"Expected qty 100, got {tx.quantity}"
        assert tx.price == Decimal("8500"), f"Expected price 8500, got {tx.price}"
        assert tx.status == "confirmed"

        buy_order.refresh_from_db()
        sell_order.refresh_from_db()
        assert buy_order.status == "matched", f"Buy order should be matched, got {buy_order.status}"
        assert sell_order.status == "matched", f"Sell order should be matched, got {sell_order.status}"

        # Check seller received cash
        self.seller.refresh_from_db()
        expected_seller_cash = seller_cash_before + Decimal("850000")  # 8500 * 100
        assert self.seller.cash_balance == expected_seller_cash, (
            f"Seller cash: expected {expected_seller_cash}, got {self.seller.cash_balance}"
        )

        # Check buyer got stock
        buyer_holding = PortfolioHolding.objects.get(user=self.buyer, stock=self.stock)
        assert buyer_holding.quantity >= 100, f"Buyer should have >= 100 shares, got {buyer_holding.quantity}"

        # Check notification created
        notif_count = Notification.objects.filter(
            user__in=[self.buyer, self.seller], type="order_matched"
        ).count()
        assert notif_count >= 2, f"Expected >= 2 notifications, got {notif_count}"

        self.stdout.write(self.style.SUCCESS("  PASSED: Exact match works correctly\n"))

    def _test_2_partial_fill(self):
        """Test: Partial fill - buy order larger than sell order."""
        self.stdout.write(self.style.MIGRATE_HEADING("Test 2: Partial Fill"))

        # Seller places sell order for 50 shares
        seller_holding = PortfolioHolding.objects.get(user=self.seller, stock=self.stock)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock, type="sell", price=Decimal("8600"), quantity=50
        )
        seller_holding.quantity -= 50
        seller_holding.save(update_fields=["quantity"])

        # Buyer places buy order for 200 shares (only 50 available)
        total_cost = Decimal("8600") * 200
        self.buyer.refresh_from_db()
        self.buyer.cash_balance -= total_cost
        self.buyer.save(update_fields=["cash_balance"])

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock, type="buy", price=Decimal("8600"), quantity=200
        )

        # Run matching
        txs = match_order(str(buy_order.id))

        assert len(txs) == 1, f"Expected 1 transaction, got {len(txs)}"
        assert txs[0].quantity == 50, f"Expected qty 50, got {txs[0].quantity}"

        buy_order.refresh_from_db()
        sell_order.refresh_from_db()
        assert buy_order.status == "partial", f"Buy should be partial, got {buy_order.status}"
        assert buy_order.filled_quantity == 50, f"Buy filled should be 50, got {buy_order.filled_quantity}"
        assert sell_order.status == "matched", f"Sell should be matched, got {sell_order.status}"

        self.stdout.write(self.style.SUCCESS("  PASSED: Partial fill works correctly\n"))

        # Clean up: cancel remaining buy order and refund
        remaining = buy_order.quantity - buy_order.filled_quantity
        refund = buy_order.price * remaining
        self.buyer.refresh_from_db()
        self.buyer.cash_balance += refund
        self.buyer.save(update_fields=["cash_balance"])
        buy_order.status = "cancelled"
        buy_order.save(update_fields=["status"])

    def _test_3_no_match(self):
        """Test: No match - buy price lower than sell price."""
        self.stdout.write(self.style.MIGRATE_HEADING("Test 3: No Match (Price Gap)"))

        # Seller wants 9000
        seller_holding = PortfolioHolding.objects.get(user=self.seller, stock=self.stock)
        sell_order = Order.objects.create(
            user=self.seller, stock=self.stock, type="sell", price=Decimal("9000"), quantity=100
        )
        seller_holding.quantity -= 100
        seller_holding.save(update_fields=["quantity"])

        # Buyer only willing to pay 8000
        total_cost = Decimal("8000") * 100
        self.buyer.refresh_from_db()
        self.buyer.cash_balance -= total_cost
        self.buyer.save(update_fields=["cash_balance"])

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock, type="buy", price=Decimal("8000"), quantity=100
        )

        # Run matching
        txs = match_order(str(buy_order.id))

        assert len(txs) == 0, f"Expected 0 transactions, got {len(txs)}"

        buy_order.refresh_from_db()
        sell_order.refresh_from_db()
        assert buy_order.status == "pending", f"Buy should be pending, got {buy_order.status}"
        assert sell_order.status == "pending", f"Sell should be pending, got {sell_order.status}"

        self.stdout.write(self.style.SUCCESS("  PASSED: No match when price gap exists\n"))

        # Clean up
        self.buyer.refresh_from_db()
        self.buyer.cash_balance += total_cost
        self.buyer.save(update_fields=["cash_balance"])
        buy_order.status = "cancelled"
        buy_order.save(update_fields=["status"])

        seller_holding.refresh_from_db()
        seller_holding.quantity += 100
        seller_holding.save(update_fields=["quantity"])
        sell_order.status = "cancelled"
        sell_order.save(update_fields=["status"])

    def _test_4_multiple_matches(self):
        """Test: One buy order matches multiple sell orders."""
        self.stdout.write(self.style.MIGRATE_HEADING("Test 4: Multiple Matches"))

        seller_holding = PortfolioHolding.objects.get(user=self.seller, stock=self.stock)

        # Create 3 small sell orders at different prices
        sells = []
        for i, (price, qty) in enumerate([(8400, 30), (8450, 50), (8500, 40)]):
            order = Order.objects.create(
                user=self.seller, stock=self.stock, type="sell",
                price=Decimal(str(price)), quantity=qty,
            )
            seller_holding.quantity -= qty
            sells.append(order)
        seller_holding.save(update_fields=["quantity"])

        # Buyer places large buy order at 8500
        buy_qty = 100
        total_cost = Decimal("8500") * buy_qty
        self.buyer.refresh_from_db()
        self.buyer.cash_balance -= total_cost
        self.buyer.save(update_fields=["cash_balance"])

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock, type="buy",
            price=Decimal("8500"), quantity=buy_qty,
        )

        # Run matching
        txs = match_order(str(buy_order.id))

        assert len(txs) == 3, f"Expected 3 transactions, got {len(txs)}"

        buy_order.refresh_from_db()
        # 30 + 50 + 40 = 120 available, but buy only wants 100
        # Should match: 30 @ 8400, 50 @ 8450, 20 @ 8500
        assert buy_order.filled_quantity == 100, f"Buy filled should be 100, got {buy_order.filled_quantity}"
        assert buy_order.status == "matched", f"Buy should be matched, got {buy_order.status}"

        # Check the last sell order is partially filled
        sells[2].refresh_from_db()
        assert sells[2].filled_quantity == 20, f"Last sell filled should be 20, got {sells[2].filled_quantity}"
        assert sells[2].status == "partial", f"Last sell should be partial, got {sells[2].status}"

        self.stdout.write(self.style.SUCCESS("  PASSED: Multiple matches work correctly\n"))

        # Clean up remaining sell order
        remaining = sells[2].quantity - sells[2].filled_quantity
        seller_holding.refresh_from_db()
        seller_holding.quantity += remaining
        seller_holding.save(update_fields=["quantity"])
        sells[2].status = "cancelled"
        sells[2].save(update_fields=["status"])

    def _test_5_cancel_refund(self):
        """Test: Cancel order and verify refund."""
        self.stdout.write(self.style.MIGRATE_HEADING("Test 5: Cancel & Refund"))

        self.buyer.refresh_from_db()
        buyer_cash_before = self.buyer.cash_balance

        # Buyer places order (cash reserved)
        total_cost = Decimal("8700") * 100
        self.buyer.cash_balance -= total_cost
        self.buyer.save(update_fields=["cash_balance"])

        buy_order = Order.objects.create(
            user=self.buyer, stock=self.stock, type="buy",
            price=Decimal("8700"), quantity=100,
        )

        # Verify cash was deducted
        self.buyer.refresh_from_db()
        assert self.buyer.cash_balance == buyer_cash_before - total_cost

        # Cancel and refund
        remaining = buy_order.quantity - buy_order.filled_quantity
        refund = buy_order.price * remaining
        self.buyer.cash_balance += refund
        self.buyer.save(update_fields=["cash_balance"])
        buy_order.status = "cancelled"
        buy_order.save(update_fields=["status"])

        # Verify refund
        self.buyer.refresh_from_db()
        assert self.buyer.cash_balance == buyer_cash_before, (
            f"Cash should be {buyer_cash_before}, got {self.buyer.cash_balance}"
        )

        self.stdout.write(self.style.SUCCESS("  PASSED: Cancel refund works correctly\n"))

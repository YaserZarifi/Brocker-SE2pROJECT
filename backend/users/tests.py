"""
=============================================================================
BourseChain - تست‌های کاربران و احراز هویت (Authentication)
=============================================================================
شامل:
  - ثبت‌نام (Registration)
  - ورود با JWT (Login)
  - پروفایل کاربر (Profile)
  - تغییر رمز عبور
  - مدیریت ادمین
  - Sprint 5: SIWE (Sign-In with Ethereum) - EIP-4361

اجرا:
  python manage.py test users -v2
=============================================================================
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


# =============================================================================
# 1. تست مدل User
# =============================================================================


class TestUserModel(TestCase):
    """تست‌های مدل User سفارشی BourseChain."""

    def test_create_user(self):
        """ساخت کاربر عادی."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass1234!",
            first_name="Ali",
            last_name="Rezaei",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "customer")
        self.assertTrue(user.check_password("TestPass1234!"))

    def test_user_default_cash_balance(self):
        """موجودی نقدی پیش‌فرض 10,000,000 ریال."""
        user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="TestPass1234!",
        )
        self.assertEqual(user.cash_balance, Decimal("10000000"))

    def test_email_is_unique(self):
        """ایمیل باید یکتا باشد."""
        User.objects.create_user(
            username="user1",
            email="same@example.com",
            password="TestPass1234!",
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2",
                email="same@example.com",
                password="TestPass1234!",
            )

    def test_login_field_is_email(self):
        """فیلد لاگین باید email باشد (نه username)."""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_user_uuid_primary_key(self):
        """Primary key باید UUID باشد."""
        user = User.objects.create_user(
            username="uuidtest",
            email="uuid@example.com",
            password="TestPass1234!",
        )
        self.assertEqual(len(str(user.id)), 36)  # UUID format


# =============================================================================
# 2. تست API ثبت‌نام (Registration)
# =============================================================================


class TestRegistrationAPI(APITestCase):
    """تست‌های endpoint ثبت‌نام."""

    def test_register_success(self):
        """ثبت‌نام موفق."""
        response = self.client.post("/api/v1/auth/register/", {
            "email": "new@example.com",
            "username": "newuser",
            "password": "SecurePass1234!",
            "password_confirm": "SecurePass1234!",
            "first_name": "Ali",
            "last_name": "Test",
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "new@example.com")

    def test_register_password_mismatch(self):
        """رمز عبور و تکرار آن باید یکسان باشند."""
        response = self.client.post("/api/v1/auth/register/", {
            "email": "new@example.com",
            "username": "newuser",
            "password": "SecurePass1234!",
            "password_confirm": "DifferentPass!",
            "first_name": "Ali",
            "last_name": "Test",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """ثبت‌نام با ایمیل تکراری باید خطا بدهد."""
        User.objects.create_user(
            username="existing",
            email="taken@example.com",
            password="TestPass1234!",
        )

        response = self.client.post("/api/v1/auth/register/", {
            "email": "taken@example.com",
            "username": "newuser",
            "password": "SecurePass1234!",
            "password_confirm": "SecurePass1234!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        """رمز عبور کوتاه‌تر از ۸ کاراکتر باید رد شود."""
        response = self.client.post("/api/v1/auth/register/", {
            "email": "new@example.com",
            "username": "newuser",
            "password": "short",
            "password_confirm": "short",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =============================================================================
# 3. تست API ورود (Login / JWT)
# =============================================================================


class TestLoginAPI(APITestCase):
    """تست‌های endpoint ورود با JWT."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass1234!",
            first_name="Ali",
            last_name="Rezaei",
        )

    def test_login_success(self):
        """ورود موفق: دریافت access و refresh token."""
        response = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass1234!",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """ورود با رمز اشتباه باید خطا بدهد."""
        response = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "WrongPassword!",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """ورود با ایمیل ناموجود."""
        response = self.client.post("/api/v1/auth/login/", {
            "email": "nonexistent@example.com",
            "password": "TestPass1234!",
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """تجدید token با refresh token."""
        login = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass1234!",
        })

        response = self.client.post("/api/v1/auth/refresh/", {
            "refresh": login.data["refresh"],
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


# =============================================================================
# 4. تست API پروفایل (Profile)
# =============================================================================


class TestProfileAPI(APITestCase):
    """تست‌های endpoint پروفایل."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass1234!",
            first_name="Ali",
            last_name="Rezaei",
        )
        self.client = APIClient()
        login = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass1234!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_get_profile(self):
        """دریافت اطلاعات پروفایل."""
        response = self.client.get("/api/v1/auth/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["name"], "Ali Rezaei")

    def test_update_profile(self):
        """آپدیت نام و اطلاعات پروفایل."""
        response = self.client.patch("/api/v1/auth/profile/", {
            "first_name": "Reza",
            "last_name": "Updated",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Reza")

    def test_unauthenticated_cannot_access_profile(self):
        """کاربر بدون لاگین نمی‌تواند پروفایل ببیند."""
        client = APIClient()
        response = client.get("/api/v1/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_contains_cash_balance(self):
        """پروفایل باید شامل موجودی نقدی باشد."""
        response = self.client.get("/api/v1/auth/profile/")
        self.assertIn("cash_balance", response.data)


# =============================================================================
# 5. تست تغییر رمز عبور
# =============================================================================


class TestChangePasswordAPI(APITestCase):
    """تست‌های تغییر رمز عبور."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="OldPass1234!",
        )
        self.client = APIClient()
        login = self.client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "OldPass1234!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_change_password_success(self):
        """تغییر رمز عبور با رمز قدیمی صحیح."""
        response = self.client.put("/api/v1/auth/change-password/", {
            "old_password": "OldPass1234!",
            "new_password": "NewPass5678!",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # تست لاگین با رمز جدید
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass5678!"))

    def test_change_password_wrong_old(self):
        """رمز قدیمی اشتباه باید خطا بدهد."""
        response = self.client.put("/api/v1/auth/change-password/", {
            "old_password": "WrongOldPass!",
            "new_password": "NewPass5678!",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =============================================================================
# 6. تست SIWE (Sign-In with Ethereum) - Sprint 5
# =============================================================================


from django.core.cache import cache
from eth_account import Account
from eth_account.messages import encode_defunct


class TestSIWENonceAPI(APITestCase):
    """تست‌های endpoint دریافت nonce برای SIWE."""

    def test_get_nonce(self):
        """دریافت nonce جدید."""
        response = self.client.get("/api/v1/auth/siwe/nonce/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("nonce", response.data)
        self.assertTrue(len(response.data["nonce"]) > 0)

    def test_nonce_is_unique(self):
        """هر بار nonce متفاوت باید تولید شود."""
        r1 = self.client.get("/api/v1/auth/siwe/nonce/")
        r2 = self.client.get("/api/v1/auth/siwe/nonce/")
        self.assertNotEqual(r1.data["nonce"], r2.data["nonce"])

    def test_nonce_cached(self):
        """nonce باید در cache ذخیره شود."""
        response = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = response.data["nonce"]
        self.assertTrue(cache.get(f"siwe_nonce_{nonce}"))


class TestSIWEVerifyAPI(APITestCase):
    """تست‌های endpoint تأیید SIWE (Sign-In with Ethereum)."""

    def _create_siwe_message(self, address, nonce):
        """ساخت پیام EIP-4361."""
        domain = "localhost"
        origin = "http://localhost:5173"
        from datetime import datetime
        issued_at = datetime.utcnow().isoformat() + "Z"
        return (
            f"{domain} wants you to sign in with your Ethereum account:\n"
            f"{address}\n\n"
            f"Sign in to BourseChain - Online Stock Brokerage Platform\n\n"
            f"URI: {origin}\n"
            f"Version: 1\n"
            f"Chain ID: 1\n"
            f"Nonce: {nonce}\n"
            f"Issued At: {issued_at}"
        )

    def _sign_message(self, message, private_key):
        """امضای پیام با کلید خصوصی اتریوم."""
        from web3 import Web3
        w3 = Web3()
        encoded = encode_defunct(text=message)
        signed = w3.eth.account.sign_message(encoded, private_key=private_key)
        return signed.signature.hex()

    def test_verify_valid_signature(self):
        """تأیید امضای معتبر SIWE و دریافت JWT."""
        # Generate a random Ethereum account
        account = Account.create()

        # Get nonce from backend
        nonce_resp = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = nonce_resp.data["nonce"]

        # Create EIP-4361 message
        message = self._create_siwe_message(account.address, nonce)

        # Sign message
        signature = self._sign_message(message, account.key.hex())

        # Verify with backend
        response = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message,
            "signature": signature,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_verify_creates_user(self):
        """اولین لاگین با SIWE باید کاربر جدید بسازد."""
        account = Account.create()
        nonce_resp = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = nonce_resp.data["nonce"]

        message = self._create_siwe_message(account.address, nonce)
        signature = self._sign_message(message, account.key.hex())

        response = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message, "signature": signature,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was created with wallet address
        from eth_utils import to_checksum_address
        checksum_addr = to_checksum_address(account.address)
        user = User.objects.get(wallet_address=checksum_addr)
        self.assertIsNotNone(user)
        self.assertEqual(user.wallet_address, checksum_addr)

    def test_verify_existing_wallet_user(self):
        """لاگین دوباره با wallet قبلی باید همان کاربر را برگرداند."""
        account = Account.create()
        from eth_utils import to_checksum_address

        # Create user with wallet address
        user = User.objects.create_user(
            username="ethuser",
            email="eth@test.com",
            password="TestPass1234!",
            wallet_address=to_checksum_address(account.address),
        )

        nonce_resp = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = nonce_resp.data["nonce"]

        message = self._create_siwe_message(account.address, nonce)
        signature = self._sign_message(message, account.key.hex())

        response = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message, "signature": signature,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["id"], str(user.id))

    def test_verify_invalid_signature(self):
        """امضای نامعتبر باید خطا بدهد."""
        nonce_resp = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = nonce_resp.data["nonce"]

        account = Account.create()
        message = self._create_siwe_message(account.address, nonce)

        response = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message,
            "signature": "0x" + "00" * 65,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_missing_fields(self):
        """بدون message یا signature باید خطا بدهد."""
        response = self.client.post("/api/v1/auth/siwe/verify/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_expired_nonce(self):
        """nonce استفاده شده نباید دوباره قابل استفاده باشد."""
        account = Account.create()
        nonce_resp = self.client.get("/api/v1/auth/siwe/nonce/")
        nonce = nonce_resp.data["nonce"]

        message = self._create_siwe_message(account.address, nonce)
        signature = self._sign_message(message, account.key.hex())

        # First verify: should succeed
        r1 = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message, "signature": signature,
        })
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # Second verify with same nonce: should fail
        r2 = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message, "signature": signature,
        })
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_nonce_not_from_backend(self):
        """nonce نامعتبر (ساخته نشده توسط backend) باید خطا بدهد."""
        account = Account.create()

        message = self._create_siwe_message(account.address, "fake_nonce_12345")
        signature = self._sign_message(message, account.key.hex())

        response = self.client.post("/api/v1/auth/siwe/verify/", {
            "message": message, "signature": signature,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

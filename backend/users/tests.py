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

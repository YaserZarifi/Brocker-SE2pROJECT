# Incident Postmortem #2: تداخل Migration در Celery و Backend

**پروژه**: BourseChain  
**تاریخ**: بهمن ۱۴۰۴  
**شدت**: متوسط (Celery crash)  

---

## ۱. خلاصه

Celery worker با خطای `MigrationSchemaMissing` و `duplicate key value violates unique constraint` متوقف شد.

---

## ۲. Timeline

| زمان | رویداد |
|------|--------|
| T0 | Backend و Celery همزمان start شدند |
| T1 | هر دو entrypoint.sh را اجرا کردند (wait → migrate → collectstatic) |
| T2 | هر دو همزمان `python manage.py migrate` اجرا کردند |
| T3 | race condition → خطای duplicate key در pg_class |
| T4 | Celery exit با کد 1 |

---

## ۳. Root Cause

- Backend و Celery هر دو از **همان Dockerfile** و **همان entrypoint** استفاده می‌کردند
- entrypoint شامل `migrate` بود
- دو process همزمان روی schema دیتابیس کار کردند → conflict

---

## ۴. Impact

- Celery worker شروع نشد
- وظایف async (matching، blockchain recording) اجرا نشدند
- سفارش‌ها match نمی‌شدند

---

## ۵. Resolution

در docker-compose.yml برای Celery:

```yaml
celery:
  entrypoint: []
  command: celery -A config worker -l info --concurrency=2
  depends_on:
    backend:
      condition: service_healthy
```

- `entrypoint: []` → entrypoint غیرفعال، migrate اجرا نمی‌شود
- `depends_on: backend` → Celery فقط بعد از healthy شدن Backend (که migrate را انجام داده) start می‌شود

---

## ۶. اقدامات پیشگیرانه

1. فقط یک سرویس مسئول migrate باشد (Backend)
2. سرویس‌های وابسته (Celery، setup) به `backend: healthy` وابسته باشند
3. در documentation ذکر شود که migration فقط در Backend اجرا می‌شود

# Incident Postmortem #3: محدودیت Docker Hub در ایران

**پروژه**: BourseChain  
**تاریخ**: بهمن ۱۴۰۴  
**شدت**: بالا (عدم امکان pull image)  

---

## ۱. خلاصه

Docker نتوانست image ها را از `registry-1.docker.io` دانلود کند و خطای `403 Forbidden` یا `EOF` برگرداند.

---

## ۲. Timeline

| زمان | رویداد |
|------|--------|
| T0 | `docker compose up -d --build` اجرا شد |
| T1 | Pull از docker.io برای grafana، postgres، redis، rabbitmq شروع شد |
| T2 | خطا: `403 Forbidden` یا `failed to copy: ... EOF` |
| T3 | Build متوقف شد |

---

## ۳. Root Cause

- دسترسی به Docker Hub از ایران با محدودیت یا rate limit مواجه است
- بعضی درخواست‌ها 403 Forbidden یا EOF (قطع اتصال) برمی‌گردانند
- Mirror های ایرانی این مشکل را حل می‌کنند

---

## ۴. Impact

- عدم امکان اجرای `docker compose up` بدون دسترسی به image ها
- توسعه‌دهندگان در ایران نمی‌توانستند پروژه را اجرا کنند

---

## ۵. Resolution

1. **استفاده از Mirror**: تمام image ها به `docker.arvancloud.ir` تغییر داده شدند:
   - `postgres:16-alpine` → `docker.arvancloud.ir/postgres:16-alpine`
   - `redis:7-alpine` → `docker.arvancloud.ir/redis:7-alpine`
   - و غیره

2. **Pull دستی**: در صورت EOF، کاربر می‌تواند image را به صورت دستی pull کند:
   ```powershell
   docker pull docker.arvancloud.ir/rabbitmq:3-management-alpine
   ```

3. **Docker daemon.json** (اختیاری): تنظیم `registry-mirrors` برای استفاده خودکار از mirror

---

## ۶. اقدامات پیشگیرانه

1. در README و CONTEXT.md ذکر شود که برای کاربران ایران از mirror استفاده شود
2. فهرست image های مورد نیاز و دستورات pull دستی در docs قرار گیرد
3. یا استفاده از private registry داخلی برای تیم

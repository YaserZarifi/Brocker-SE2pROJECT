# Incident Postmortem #1: خطای CRLF در entrypoint.sh

**پروژه**: BourseChain  
**تاریخ**: بهمن ۱۴۰۴  
**شدت**: بالا (Backend container crash)  

---

## ۱. خلاصه

Backend container بلافاصله بعد از start با خطای `exec /entrypoint.sh: no such file or directory` متوقف شد.

---

## ۲. Timeline

| زمان | رویداد |
|------|--------|
| T0 | `docker compose up -d --build` اجرا شد |
| T1 | Build موفق. Backend container start شد |
| T2 | Container بلافاصله exit کرد با کد 255 |
| T3 | لاگ: `exec /entrypoint.sh: no such file or directory` |

---

## ۳. Root Cause

فایل `entrypoint.sh` با **line ending ویندوز (CRLF)** ایجاد شده بود. در لینوکس:

- Shebang `#!/bin/bash\r` به جای `#!/bin/bash` خوانده می‌شد
- کرنل مسیر `/bin/bash\r` را پیدا نمی‌کرد
- در نتیجه: `no such file or directory`

---

## ۴. Impact

- Backend container شروع نشد
- Frontend به backend دسترسی نداشت (host not found)
- Celery هم به خاطر استفاده از همان entrypoint دچار مشکل شد

---

## ۵. Resolution

در Dockerfile اضافه شد:

```dockerfile
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
```

این دستور قبل از `chmod` تمام `\r` را حذف می‌کند (تبدیل CRLF به LF).

---

## ۶. اقدامات پیشگیرانه

1. استفاده از `.gitattributes`: `*.sh text eol=lf` برای فایل‌های shell
2. در CI/CD بررسی line ending قبل از build
3. ذکر در CONTEXT.md برای توسعه‌دهندگان آینده

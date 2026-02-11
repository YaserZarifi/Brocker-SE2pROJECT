# BourseChain - Burndown Chart

**پروژه**: سامانه کارگزاری بورس آنلاین  
**دانشگاه**: امیرکبیر - درس مهندسی نرم‌افزار ۲  
**تاریخ**: بهمن ۱۴۰۴  

---

## ۱. تعریف Story Points (تقریبی)

| Sprint | موارد | Story Points | وضعیت |
|--------|-------|--------------|-------|
| Sprint 1 | Frontend + UI + Mock | 13 | ✅ Done |
| Sprint 2 | Backend API + DB + Integration | 21 | ✅ Done |
| Sprint 3 | Matching Engine + Celery | 21 | ✅ Done |
| Sprint 4 | Blockchain (Hardhat + Web3) | 13 | ✅ Done |
| Sprint 5 | WebSocket + SIWE | 13 | ✅ Done |
| Sprint 6 | Docker + K8s + Monitoring + Terraform + Docs | 21 | ✅ Done |
| **جمع** | | **102** | |

---

## ۲. Burndown Chart (مفهومی)

```
Story Points
    ^
102 |●
    | \
 80 |  \●
    |   \
 60 |    \●
    |     \
 40 |      \●
    |       \
 20 |        \●
    |         \●
  0 +----------+----+----+----+----+----> روز
       S1   S2   S3   S4   S5   S6
```

### توضیح
- **محور عمودی**: کار باقی‌مانده (Story Points)
- **محور افقی**: زمان (Sprint ها)
- **خط نزولی**: کار انجام شده در هر Sprint
- **نقطه پایان**: تمام ۱۰۲ SP تحویل شده

---

## ۳. Velocity (سرعت تیم)

| Sprint | SP تحویل شده | Cumulative |
|--------|--------------|------------|
| S1 | 13 | 13 |
| S2 | 21 | 34 |
| S3 | 21 | 55 |
| S4 | 13 | 68 |
| S5 | 13 | 81 |
| S6 | 21 | 102 |

**میانگین Velocity**: ~17 SP در هر Sprint

---

## ۴. جمع‌بندی

- پروژه طبق برنامه و بدون backlog باقی‌مانده تحویل شد
- Burndown منحنی نزولی سالم دارد
- هیچ کار ناتمامی در Sprint های قبلی باقی نمانده

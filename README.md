# Dars Jarayonida Tinglovchilar Faolligini Avtomatik Baholash

Ushbu loyiha universitet auditoriyasidagi kamera oqimi orqali dars jarayonida tinglovchilar faolligini real vaqt rejimida kuzatish va sessiya yakunida natijalarni bazaga saqlash uchun yaratilgan.

## Sahifalar

- `/` - bosh sahifa. Faqat loyiha haqida ma'lumot beradi, bu yerda ma'lumot kiritish yoki monitoring boshqarish yo'q.
- `/admin` - admin panel. Kamera sozlamalari, default kamera tanlash va talabalar bazasi shu yerda boshqariladi.
- `/events` - hodisa kuzatuvi. Jonli video, monitoring tugmalari, ballar, hodisa indikatorlari, tracklar va sessiyalar shu sahifada ko'rsatiladi.

## Admin Kirish

Standart admin parol:

```text
admin123
```

Parolni almashtirish uchun dasturni ishga tushirishdan oldin `ADMIN_PASSWORD` muhit o'zgaruvchisini bering.

## Asosiy Imkoniyatlar

- universitet/IP kamera yoki webcam orqali video oqim olish;
- default kameralar ro'yxatidan tanlash;
- kamera sozlamasini bazada saqlab qolish;
- talabalar bazasini admin panelda jadval ko'rinishida yuritish;
- yuz aniqlash orqali anonim tracklarni kuzatish;
- trackni talabalar bazasidagi talaba bilan bog'lash;
- mavjudlik, diqqat, harakat va umumiy ballni hisoblash;
- telefon ehtimoli, savol/qo'l ishorasi, uyquchanlik va chalg'ish signallarini ko'rsatish;
- sessiyalarni SQLite bazasiga saqlash;
- sessiya natijalarini CSV formatda eksport qilish.

## Hodisa Kuzatuvi Nima Qiladi?

`Hodisa kuzatuvi` sahifasi tizimning asosiy ish oynasi hisoblanadi. U quyidagilarni bir joyda kuzatadi:

- jonli kamera oqimi;
- monitoringni boshlash, to'xtatish va statistikani tozalash;
- joriy ball, mavjudlik, diqqat va harakat foizlari;
- anonim tracklar va ularning individual statistikasi;
- talabalar bazasidan talaba tanlab trackga biriktirish;
- telefon ehtimoli, savol/qo'l ishorasi, uyquchanlik va chalg'ish hisoblagichlari;
- saqlangan monitoring sessiyalari.

Hodisa indikatorlari qat'iy hukm emas. Ular video oqimdan olingan ehtimoliy signallar bo'lib, o'qituvchiga e'tibor berish kerak bo'lgan holatlarni ko'rsatadi.

## Talabalar Bazasi

Talabalar `student_roster` jadvalida saqlanadi. Bosh sahifada talaba qo'shish yo'q. Talabalar faqat admin panel orqali qo'shiladi va hodisa kuzatuvi sahifasida shu bazadan tanlanadi.

## Default Kameralar

Admin panelda quyidagi tayyor variantlar mavjud:

- `Webcam 0`
- `Webcam 1`
- `Webcam 2`
- `Ochiq RTSP test`
- `Ochiq HLS test`

Universitet kamerasi uchun RTSP format namunasi:

```text
rtsp://login:parol@IP:554/stream1
```

## O'rnatish

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ishga Tushirish

```bash
python app.py
```

Brauzerda oching:

```text
http://127.0.0.1:5000
```

Boshqa portda ishga tushirish:

```bash
set PORT=5001
python app.py
```

## Texnologiyalar

- Python
- Flask
- OpenCV
- NumPy
- SQLite
- HTML, CSS, JavaScript

## Loyiha Tuzilmasi

- `app.py` - Flask serverni ishga tushirish fayli
- `activity_system/` - backend modullar
- `templates/` - sahifalar
- `static/` - CSS va JavaScript
- `data/activity.db` - SQLite baza
- `exports/` - CSV eksport fayllari
- `docs/` - loyiha hujjatlari

## Muhim Eslatma

Tizim shaxsni tanish uchun mo'ljallanmagan. Natijalar anonim tracklar, ehtimoliy hodisalar va umumiy monitoring statistikasi sifatida ishlatiladi.

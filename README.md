# Dars Jarayonida Tinglovchilar Faolligini Avtomatik Baholash

Ushbu loyiha masofaviy talabalar uchun Zoom platformasidagi onlayn darslarni kuzatish, talabaning darsga nisbatan diqqat va faolligini multimodal indikatorlar orqali avtomatik baholash hamda o'qituvchiga yordamchi dashboard berish uchun yaratilgan.

## Sahifalar

- `/` - bosh sahifa. Faqat loyiha haqida ma'lumot beradi, bu yerda ma'lumot kiritish yoki monitoring boshqarish yo'q.
- `/admin` - admin panel. Zoom linki, ekran manbasi va virtual kamera tanlash shu yerda boshqariladi.
- `/events` - live jarayonni kuzatish sahifasi. Jonli video, monitoring tugmalari, live ballar, Zoomdan OCR orqali olingan ismlar va hodisa indikatorlari shu sahifada ko'rsatiladi.
- `/results` - natijalar sahifasi. Har bir saqlangan sessiya va shu sessiyadagi talabalar ballari shu yerda turadi.

## Admin Kirish

Standart admin parol:

```text
admin123
```

Parolni almashtirish uchun dasturni ishga tushirishdan oldin `ADMIN_PASSWORD` muhit o'zgaruvchisini bering.

## Asosiy Imkoniyatlar

- Zoom oynasini ekran capture orqali kuzatish;
- OBS/Zoom virtual kamerasi orqali video oqim olish;
- Zoom invitation matnidan link, Meeting ID, Passcode va Topicni avtomatik ajratish;
- `Zoomni boshlash` yoki `Monitoringni boshlash` bosilganda saqlangan Zoom linkini ochish;
- Zoom manbasi sozlamasini bazada saqlab qolish;
- Zoom linkini saqlash va admin paneldan Zoomni ochish;
- monitoring paytida audio oqimni `.wav` faylga yozish;
- yuz aniqlash va Zoom oynasidagi ko'rinib turgan ismlarni OCR orqali avtomatik bog'lash;
- mavjudlik, diqqat, harakat va umumiy ballni hisoblash;
- telefon ehtimoli, savol/qo'l ishorasi, uyquchanlik va chalg'ish signallarini ko'rsatish;
- sessiyalarni SQLite bazasiga saqlash;
- `To'xtatish va saqlash` bosilganda natijalar sahifasiga avtomatik o'tish;
- sessiyani bosganda o'sha darsdagi talabalar ballarini ko'rsatish;
- sessiya natijalarini CSV formatda eksport qilish.

## Hodisa Kuzatuvi Nima Qiladi?

Live jarayon va ballarni kuzatish joyi: `http://127.0.0.1:5000/events`.
Saqlangan natijalarni ko'rish joyi: `http://127.0.0.1:5000/results`.

`Hodisa kuzatuvi` sahifasi tizimning asosiy ish oynasi hisoblanadi. U quyidagilarni bir joyda kuzatadi:

- jonli Zoom oqimi;
- monitoringni boshlash, to'xtatish va statistikani tozalash;
- joriy ball, mavjudlik, diqqat va harakat foizlari;
- Zoom oynasida ko'ringan ismlar va ularning individual statistikasi;
- Zoomdagi ko'rinib turgan ismni avtomatik OCR orqali biriktirishga urinish;
- telefon ehtimoli, savol/qo'l ishorasi, uyquchanlik va chalg'ish hisoblagichlari;
- saqlangan monitoring sessiyalari.

Hodisa indikatorlari qat'iy hukm emas. Ular video oqimdan olingan ehtimoliy signallar bo'lib, o'qituvchiga e'tibor berish kerak bo'lgan holatlarni ko'rsatadi.

## Zoom Manbalari

Admin panelda quyidagi tayyor variantlar mavjud:

- `Zoom ekrani` - `screen:1`, asosiy monitorni oladi;
- `Virtual kamera 0` - OBS Virtual Camera yoki boshqa virtual qurilma 0-indeksda bo'lsa;
- `Virtual kamera 1` - virtual qurilma 1-indeksda bo'lsa.

Zoom linkini berish joyi:

- `/admin` sahifasiga kiring.
- Zoom invitation matnini `Zoom invitation matni` maydoniga paste qiling.
- `Invitationdan olish` tugmasini bosing.
- Tizim `Topic`, `Zoom linki`, `Meeting ID` va `Passcode` ni ajratib beradi.
- `Zoom manbasini saqlash` tugmasini bosing.
- `Zoomni ochish` tugmasi saqlangan linkni ochadi.

Zoom bilan ishlatish:

```text
1. Admin panelga Zoom linkini kiriting.
2. "Zoomni ochish" tugmasi orqali meetingga kiring.
3. Zoom oynasini asosiy monitorda ochiq qoldiring.
4. Manba sifatida "Zoom ekrani" yoki "screen:1" ni saqlang.
5. Hodisa kuzatuvi sahifasida monitoringni boshlang.
```

Faqat Zoom linkini berishning o'zi yetmaydi. Link meetingni ochadi, lekin video tahlil uchun Zoom oynasi ekranda ko'rinib turishi va tizimga `screen:1` yoki `screen:2` kabi ekran manbasi berilishi kerak.

Zoomdagi ismlar masalasi: tizim Zoom oynasidagi yuzlarni tahlil qiladi va Tesseract OCR orqali yuz yonidagi ko'rinib turgan ism yozuvini o'qib avtomatik biriktirishga urinadi. Ismlar va ballar `/events` sahifasidagi `Zoom ismlari va ballar` bo'limida chiqadi.

Tesseract OCR kerak bo'lsa Windows uchun o'rnatiladi va PATH'ga qo'shiladi. Faqat `pytesseract` Python paketi yetmaydi; Tesseract dasturining o'zi ham tizimda bo'lishi kerak.

## Multimodal Baholash Maqsadi

Loyihaning ilmiy maqsadi zamonaviy ta'limda talabaning onlayn darsdagi ishtirokini bulutli texnologiyalar asosida multimodal yondashuv bilan baholashdir. Platforma quyidagi signallarni yagona `Diqqat va Faollik Indeksi`ga jamlashga mo'ljallangan:

- vizual ishtirok: yuz mavjudligi, bosh holati, qarash yo'nalishi va ekrandagi faollik;
- mimika va harakat: yuz ifodasi, ko'z-bosh harakati, savol berish yoki chalg'ish signallari;
- audio faoliyat: dars davomida ovoz yozuvi, keyingi bosqichda wav2vec2 asosida emotsiya va nutq faolligini baholash;
- pedagogik indikatorlar: diqqat barqarorligi, emotsional fon, kognitiv reaksiya tezligi va umumiy engagement profili.

Joriy versiyada video tahlil OpenCV asosida ishlaydi, audio esa sessiya bilan birga `.wav` formatida saqlanadi. MediaPipe FaceMesh, Head Pose Estimation va wav2vec2 Emotion Recognition modellarini ulash keyingi rivojlantirish bosqichi sifatida ajratilgan.

## Audio Yozish

Monitoring boshlanganda audio yozish ham ishga tushadi va fayllar `exports/audio/` papkasiga saqlanadi. Zoom ovozini yozish uchun kompyuterda Zoom audio chiqishi yozib olinadigan input sifatida ko'rinishi kerak:

- Windows `Stereo Mix` yoqilgan bo'lishi mumkin;
- yoki VB-CABLE/virtual audio cable ishlatiladi;
- faqat mikrofon tanlangan bo'lsa, dastur asosan xona/mikrofon ovozini yozadi, Zoom ichki ovozini emas.

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

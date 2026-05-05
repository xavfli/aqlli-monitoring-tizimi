# Kurs Ishining Izohi

## Mavzu

Dars jarayonida tinglovchilarning ishtirok faolligini avtomatik baholash uchun dasturiy ta'minot ishlab chiqish.

## Muammo bayoni

An'anaviy dars jarayonida tinglovchi faolligini baholash ko'pincha o'qituvchining shaxsiy kuzatuviga bog'liq bo'ladi. Bu esa subyektivlik, vaqt sarfi va natijalarni saqlashdagi noqulayliklarga olib keladi. Mazkur loyiha shu muammoni kamaytirish uchun kamera, kompyuter ko'rishi va ma'lumotlar bazasi asosida avtomatlashtirilgan tizim taklif qiladi.

## Maqsad

Python va OpenCV asosida real vaqt rejimida ishlovchi, tinglovchi ishtirokini nazorat qiluvchi, statistikani hisoblaydigan va natijalarni saqlaydigan dasturiy tizim yaratish.

## Vazifalar

1. Kameradan video oqim olish.
2. Video kadrlarida yuzni aniqlash.
3. Tinglovchining mavjudligini kuzatish.
4. Faollik uchun baholash mezonlarini ishlab chiqish.
5. Natijalarni SQLite bazasiga saqlash.
6. O'qituvchi uchun qulay web interfeys tayyorlash.
7. Sessiyalar hisobotini CSV ko'rinishida eksport qilish.

## Tizimning ishlash algoritmi

1. O'qituvchi web panel orqali monitoringni ishga tushiradi.
2. Tizim kompyuter kamerasiga ulanadi.
3. Har bir kadr `Haar Cascade` algoritmi yordamida qayta ishlanadi.
4. Eng katta yuz hududi asosiy tinglovchi sifatida olinadi.
5. Tinglovchining markazga yaqinligi diqqat ko'rsatkichi sifatida baholanadi.
6. Kadrlar orasidagi farq orqali tabiiy harakat darajasi hisoblanadi.
7. Joriy ball, mavjudlik foizi, diqqat va harakat ulushi dashboardga chiqariladi.
8. Sessiya tugatilganda natijalar ma'lumotlar bazasiga saqlanadi.

## Faollikni baholash mezonlari

- Kamera oldida mavjudlik.
- Yuzning ekran markaziga nisbatan joylashuvi.
- Yuz sohasidagi tabiiy harakat.
- Sessiya davomida umumiy o'rtacha ball.

## Foydalanilgan texnologiyalar

- `Python`
- `OpenCV`
- `NumPy`
- `Flask`
- `SQLite`
- `HTML`, `CSS`, `JavaScript`

## Amaliy ahamiyati

Mazkur tizim:

- darsdagi ishtirokni nazorat qilishni avtomatlashtiradi;
- o'qituvchining vaqtini tejaydi;
- natijalarni saqlash va keyinchalik tahlil qilish imkonini beradi;
- keyinchalik sun'iy intellekt modullari bilan kengaytirilishi mumkin.

## Xulosa

Loyiha ta'lim jarayonida tinglovchi faolligini real vaqt rejimida avtomatik baholash imkonini beradi. Tizim amaliy jihatdan sodda, ishlashga tayyor va keyingi rivojlantirish uchun mustahkam asos yaratadi.

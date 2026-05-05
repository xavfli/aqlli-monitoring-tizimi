# LOYIHA TEXNIK ZADANIYESI

## 1. Loyiha nomi

Dars jarayonida tinglovchilarning ishtirok faolligini avtomatik baholash uchun dasturiy ta'minot ishlab chiqish

## 2. Loyiha buyurtmachisi

Ta'lim muassasasi, o'qituvchi yoki dars jarayonini nazorat qiluvchi mas'ul shaxs.

## 3. Loyiha ijrochisi

Talaba tomonidan ishlab chiqiladigan dasturiy tizim.

## 4. Loyihaning maqsadi

Ushbu loyihaning asosiy maqsadi dars jarayonida tinglovchilarning ishtirok faolligini avtomatik ravishda aniqlash, baholash va natijalarni saqlashdan iborat. Tizim kamera orqali real vaqt rejimida video oqimni qabul qiladi, tinglovchini aniqlaydi, uning darsdagi mavjudligi, diqqat holati va harakatini hisobga olib faollik ko'rsatkichini shakllantiradi.

## 5. Loyihaning dolzarbligi

Hozirgi vaqtda ta'lim jarayonida tinglovchilar faolligini baholash ko'p hollarda o'qituvchi kuzatuviga asoslanadi. Bu esa subyektivlikka, vaqt yo'qotilishiga va natijalarni tizimli saqlashdagi muammolarga olib keladi. Kompyuter ko'rishi va sun'iy intellekt elementlari yordamida ushbu jarayonni avtomatlashtirish:

- inson omilini kamaytiradi;
- baholash aniqligini oshiradi;
- real vaqt rejimida monitoring olib borishga imkon beradi;
- natijalarni tahlil qilish va saqlashni soddalashtiradi.

## 6. Loyihaning asosiy vazifalari

1. Kamera orqali video oqimini real vaqt rejimida qabul qilish.
2. Video kadrlarida yuzni aniqlash.
3. Tinglovchining kamera oldida mavjudligini aniqlash.
4. Tinglovchining markazga nisbatan joylashuvi orqali diqqat ko'rsatkichini baholash.
5. Kadrlar orasidagi o'zgarishlarni aniqlash orqali harakat va ishtirok darajasini baholash.
6. Faollik bo'yicha umumiy ballni hisoblash.
7. Natijalarni ma'lumotlar bazasiga saqlash.
8. O'qituvchi uchun qulay boshqaruv paneli yaratish.
9. Sessiyalar bo'yicha hisobot va eksport imkoniyatini taqdim etish.

## 7. Loyiha obyekti

Dars jarayonida qatnashayotgan tinglovchilarning video kuzatuv asosidagi faollik darajasi.

## 8. Loyiha predmeti

Kamera, kompyuter ko'rishi algoritmlari, ma'lumotlar bazasi va web interfeys asosida tinglovchilar faolligini avtomatik nazorat qilish jarayoni.

## 9. Tizimga qo'yiladigan funksional talablar

Tizim quyidagi funksiyalarni bajarishi kerak:

1. Kompyuter kamerasiga ulanish va video oqimni olish.
2. Har bir video kadrni qayta ishlash.
3. Yuzni aniqlash algoritmi yordamida tinglovchini topish.
4. Tinglovchi aniqlangan holatda uning koordinatalarini belgilash.
5. Tinglovchining kadr markaziga nisbatan joylashuvini aniqlash.
6. Ketma-ket kadrlar farqini hisoblash orqali harakat darajasini topish.
7. Mavjudlik, diqqat va harakat asosida joriy faollik ballini hisoblash.
8. Sessiya davomida umumiy statistika yuritish.
9. Sessiya tugagach natijalarni saqlash.
10. Avvalgi sessiyalar ro'yxatini ko'rsatish.
11. Natijalarni CSV formatga eksport qilish.

## 10. Nofunksional talablar

Tizim quyidagi nofunksional talablarga javob berishi kerak:

- real vaqt rejimida ishlashi;
- foydalanuvchi interfeysi sodda va tushunarli bo'lishi;
- o'rnatish va ishga tushirish jarayoni yengil bo'lishi;
- resurslardan samarali foydalanishi;
- kengaytirishga qulay arxitekturaga ega bo'lishi;
- ma'lumotlarni ishonchli saqlashi.

## 11. Tizim arxitekturasi

Tizim quyidagi asosiy modullardan tashkil topadi:

### 11.1. Video qabul qilish moduli

- kompyuter kamerasidan video oqimni olish;
- kadrlarni real vaqt rejimida uzatish;
- video parametrlarini boshqarish.

### 11.2. Kompyuter ko'rishi moduli

- yuzni aniqlash;
- yuz hududini belgilash;
- harakatni hisoblash;
- faollik mezonlarini shakllantirish.

### 11.3. Baholash moduli

- joriy ballni hisoblash;
- o'rtacha ballni hisoblash;
- maksimal ballni aniqlash;
- mavjudlik foizini shakllantirish.

### 11.4. Ma'lumotlar bazasi moduli

- sessiya ma'lumotlarini saqlash;
- sessiyalar tarixini yuritish;
- statistik hisobot tayyorlash.

### 11.5. Web interfeys moduli

- monitoringni boshlash va to'xtatish;
- joriy natijalarni ekranga chiqarish;
- sessiyalar jadvalini ko'rsatish;
- eksport funksiyasini taqdim etish.

## 12. Faollikni baholash mezonlari

Faollik quyidagi mezonlar asosida aniqlanadi:

1. Kamera oldida mavjudlik.
2. Tinglovchining ekran markaziga yaqinligi.
3. Tabiiy harakat mavjudligi.
4. Sessiya davomida umumiy qatnashish ko'rsatkichi.

Baholash 0 dan 100 gacha bo'lgan diapazonda amalga oshiriladi.

## 13. Foydalanuvchilar toifasi

Tizimdan quyidagi foydalanuvchilar foydalanadi:

- o'qituvchi;
- administrator;
- dars monitoringini olib boruvchi mas'ul shaxs.

## 14. Dasturiy vositalar va texnologiyalar

Loyiha quyidagi texnologiyalar asosida ishlab chiqiladi:

- `Python` dasturlash tili;
- `OpenCV` kutubxonasi;
- `NumPy` kutubxonasi;
- `Flask` web freymvorki;
- `SQLite` ma'lumotlar bazasi;
- `HTML`, `CSS`, `JavaScript` texnologiyalari.

## 15. Apparatura talablari

Tizimni ishga tushirish uchun quyidagi texnik vositalar talab etiladi:

- kamera mavjud kompyuter yoki noutbuk;
- kamida 4 GB tezkor xotira;
- kamida 2 yadroli protsessor;
- Windows operatsion tizimi;
- internet majburiy emas, lokal rejimda ishlashi mumkin.

## 16. Kiruvchi ma'lumotlar

Tizimga kiruvchi ma'lumotlar:

- kamera orqali olinadigan video oqim;
- foydalanuvchi tomonidan kiritiladigan sessiya nomi;
- kamera indeksi.

## 17. Chiquvchi ma'lumotlar

Tizim quyidagi natijalarni chiqaradi:

- joriy faollik balli;
- mavjudlik foizi;
- diqqat ko'rsatkichi;
- harakat ko'rsatkichi;
- umumiy sessiya natijalari;
- sessiyalar tarixi;
- CSV hisobot fayli.

## 18. Xavfsizlik talablari

- foydalanuvchi ma'lumotlari lokal muhitda saqlanishi kerak;
- tizim kamera bilan ishlashda ruxsat etilgan qurilmadan foydalanishi kerak;
- ma'lumotlar bazasidagi natijalar tasodifiy yo'qolishining oldi olinishi kerak;
- tizim noto'g'ri ma'lumot kiritilganda xatolik haqida foydalanuvchiga xabar berishi kerak.

## 19. Loyihani ishlab chiqish bosqichlari

1. Predmet sohasini tahlil qilish.
2. Texnik topshiriqni ishlab chiqish.
3. Tizim arxitekturasini loyihalash.
4. Kamera bilan ishlovchi modulni yaratish.
5. Yuzni aniqlash va baholash modulini ishlab chiqish.
6. Ma'lumotlar bazasini yaratish.
7. Web interfeysni ishlab chiqish.
8. Tizimni testdan o'tkazish.
9. Yakuniy hujjatlarni tayyorlash.

## 20. Kutilayotgan natijalar

Loyiha yakunida quyidagi natijalarga erishilishi kerak:

- ishlaydigan real-time monitoring tizimi;
- tinglovchi faolligini avtomatik baholovchi dastur;
- statistikani saqlovchi ma'lumotlar bazasi;
- o'qituvchi uchun qulay web dashboard;
- kurs ishi yoki bitiruv loyihasi sifatida taqdim etishga tayyor mahsulot.

## 21. Xulosa

Mazkur texnik zadaniye dars jarayonida tinglovchilar faolligini avtomatik baholovchi dasturiy tizimni yaratish uchun asosiy talablarni belgilaydi. Tizim zamonaviy kompyuter ko'rishi texnologiyalaridan foydalangan holda ta'lim jarayonini raqamlashtirishga, monitoringni soddalashtirishga va baholash aniqligini oshirishga xizmat qiladi.

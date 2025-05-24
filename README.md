# 🚗 Araç Kiralama Web Uygulaması

Bu proje, Flask ile geliştirilmiş kullanıcı dostu bir **Araç Kiralama Takip Sistemi**dir. Kullanıcılar sisteme giriş yaparak araç kiralayabilir, yöneticiler ise araç ve kiralama işlemlerini kolayca yönetebilir.

## 🔧 Özellikler

- 🔐 Kullanıcı Girişi ve Çıkışı (Login / Logout)
- 🚘 Araç Ekleme, Listeleme, Güncelleme, Silme (CRUD)
- 📆 Kiralama Süresine Göre Otomatik Ücret Hesaplama
- 📋 Admin Paneli ile Araç ve Müşteri Yönetimi

## 🛠️ Kullanılan Teknolojiler

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF
- Bootstrap
- SQLite (Varsayılan veritabanı)

## 📁 Proje Yapısı

```text
AracKiralama_Final/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── arac_listele.html
│   ├── arac_ekle.html
│   ├── kiralama_ekle.html
│   └── ...
└── static/
    ├── css/
    └── js/
```

## 🚀 Kurulum

1. **Projeyi klonlayın:**
   ```bash
   git clone https://github.com/fevvat/AracKiralama_Final.git
   cd AracKiralama_Final
   ```

2. **Sanal ortam oluşturun:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Gerekli bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Veritabanını başlatın:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. **Uygulamayı çalıştırın:**
   ```bash
   flask run
   ```

## 📌 Notlar

- Uygulama varsayılan olarak `SQLite` kullanır, istenirse farklı bir veritabanına uyarlanabilir.
- Admin paneli üzerinden tüm kiralama ve araç işlemleri yönetilebilir.
- Modern ve responsive bir arayüz için Bootstrap tercih edilmiştir.
- Render Bağlantısı: https://arackiralama-final-1.onrender.com
 
---

👨‍💻 **Geliştirici:** [fevvat](https://github.com/fevvat)

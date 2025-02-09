# Akademik Takip Sistemi

Bu proje, öğrenci, öğretmen ve rehber öğretmenlerin akademik performanslarını takip edebileceği bir web uygulamasıdır. Flask kullanılarak geliştirilmiştir ve SQL tabanlı bir veritabanı ile çalışmaktadır.

---

## **Proje Özeti**
- **Öğrenciler:** 
  - Günlük çözdükleri soru sayılarını ve deneme sınavı sonuçlarını sisteme girebilir.
  - Verilerini görüntüleyebilir, güncelleyebilir veya silebilir.
  - Danışman öğretmen ve rehber öğretmen ile mesajlaşabilir.

- **Öğretmenler:** 
  - Kendilerine atanmış öğrencilerin verilerini görüntüleyebilir.
  - Öğrencilere mesaj gönderip geri bildirim sağlayabilir.

- **Rehber Öğretmenler:**
  - Tüm öğrenci ve öğretmenlerin kayıtlarını yönetebilir.
  - Öğrenci-öğretmen atamalarını gerçekleştirebilir.
  - Sistemdeki veriler üzerinde tam yetkiye sahiptir.

---

## **Proje Yapısı**

```plaintext
AkademikTakip/
├── app.py               # Uygulama giriş noktası
├── config.py            # Konfigürasyon ayarları
├── database/
│   ├── __init__.py      # Veritabanı bağlantısı
│   └── setup.py         # Veritabanı tablolarının oluşturulması
├── models/
│   ├── __init__.py      # Model bazında veritabanı tanımları
│   ├── kullanici.py     # Kullanıcı modeli
│   └── veri.py          # Öğrenci verileri modeli
├── routes/
│   ├── __init__.py      # Yönlendirme modülü
│   ├── ogrenci.py       # Öğrenci işlemleri için rotalar
│   ├── ogretmen.py      # Öğretmen işlemleri için rotalar
│   └── rehber.py        # Rehber işlemleri için rotalar
├── services/
│   ├── ogrenci_service.py # Öğrenci işlevleri
│   ├── ogretmen_service.py # Öğretmen işlevleri
│   └── rehber_service.py   # Rehber işlevleri
├── static/
│   ├── css/
│   │   ├── dashboard.css # Dashboard tasarımı
│   │   └── utilities.css # Genel stiller
│   ├── js/
│   │   └── main.js       # JS işlevselliği
│   └── images/           # Görseller
├── templates/
│   ├── base.html         # Ana şablon
│   ├── dashboard.html    # Genel dashboard
│   ├── login.html        # Giriş sayfası
│   ├── register.html     # Kayıt sayfası
│   ├── ogrenci/          # Öğrenci sayfaları
│   ├── ogretmen/         # Öğretmen sayfaları
│   └── rehber/           # Rehber sayfaları
└── README.md             # Proje bilgileri

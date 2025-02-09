from database import veritabani
from models.kullanici import Kullanici
from models.veri import GunlukVeri
from models.deneme import DenemeSonucu


def tablo_olustur():
    """
    Veritabanındaki tabloları oluşturur.
    """
    veritabani.create_all()
    print("Veritabanı tabloları başarıyla oluşturuldu.")

def tablo_sil():
    """
    Veritabanındaki tüm tabloları siler.
    """
    veritabani.drop_all()
    print("Veritabanı tabloları başarıyla silindi.")

if __name__ == "__main__":
    from app import app

    with app.app_context():
        secim = input("Tablo oluşturmak için '1', silmek için '2' girin: ")
        if secim == '1':
            tablo_olustur()
        elif secim == '2':
            tablo_sil()
        else:
            print("Geçersiz seçim.")

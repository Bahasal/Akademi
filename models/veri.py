from database import db  # SQLAlchemy veritabanı nesnesi
from datetime import datetime, date

class GunlukVeri(db.Model):
    """
    Öğrencilerin günlük çalışmaları için veri modeli.
    """
    __tablename__ = 'gunluk_veriler'

    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    tarih = db.Column(db.Date, nullable=False, default=date.today)
    namaz = db.Column(db.Integer, default=0)
    kuran = db.Column(db.Integer, default=0)
    matematik = db.Column(db.Integer, default=0)
    fen = db.Column(db.Integer, default=0)
    turkce = db.Column(db.Integer, default=0)
    sosyal = db.Column(db.Integer, default=0)
    ingilizce = db.Column(db.Integer, default=0)
    din = db.Column(db.Integer, default=0)
    kitap_okuma = db.Column(db.Integer, default=0)

    ogrenci = db.relationship('Kullanici', back_populates='gunluk_veriler')
    
    __table_args__ = (db.UniqueConstraint('ogrenci_id', 'tarih', name='unique_ogrenci_tarih'),)

    def toplam_ders_soru_sayisi(self):
        return self.matematik + self.fen + self.turkce + self.sosyal + self.ingilizce + self.din + self.kuran + self.kitap_okuma

    def __repr__(self):
        return f"<GunlukVeri {self.tarih} - Öğrenci ID: {self.ogrenci_id}>"


class DenemeSonucu(db.Model):
    """
    Deneme sonuçlarını saklayan model.
    """
    __tablename__ = 'deneme_sonuclari'

    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    tarih = db.Column(db.Date, default=date.today, nullable=False)
    dogru_matematik = db.Column(db.Integer, default=0)
    yanlis_matematik = db.Column(db.Integer, default=0)
    net_matematik = db.Column(db.Float, default=0.0)
    dogru_fen = db.Column(db.Integer, default=0)
    yanlis_fen = db.Column(db.Integer, default=0)
    net_fen = db.Column(db.Float, default=0.0)
    dogru_turkce = db.Column(db.Integer, default=0)
    yanlis_turkce = db.Column(db.Integer, default=0)
    net_turkce = db.Column(db.Float, default=0.0)
    dogru_sosyal = db.Column(db.Integer, default=0)
    yanlis_sosyal = db.Column(db.Integer, default=0)
    net_sosyal = db.Column(db.Float, default=0.0)
    dogru_ingilizce = db.Column(db.Integer, default=0)
    yanlis_ingilizce = db.Column(db.Integer, default=0)
    net_ingilizce = db.Column(db.Float, default=0.0)
    dogru_din = db.Column(db.Integer, default=0)
    yanlis_din = db.Column(db.Integer, default=0)
    net_din = db.Column(db.Float, default=0.0)
    toplam_net = db.Column(db.Float, default=0.0)

    ogrenci = db.relationship('Kullanici', back_populates='deneme_sonuclari')

    def __repr__(self):
        return f"<DenemeSonucu {self.id} - Net: {self.toplam_net}>"
    
    
    
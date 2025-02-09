from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database import db

class Kullanici(UserMixin, db.Model):
    """
    Kullanıcı modelini temsil eder: Rehber, Öğretmen, Öğrenci.
    """
    __tablename__ = 'kullanicilar'

    id = db.Column(db.Integer, primary_key=True)
    kurum_kodu = db.Column(db.String(50), nullable=True)
    kullanici_adi = db.Column(db.String(64), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # rehber, ogretmen, ogrenci
    foto = db.Column(db.String(255), nullable=True)
    aciklama = db.Column(db.Text, nullable=True)

    rehber_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    rehber = db.relationship('Kullanici', remote_side=[id], foreign_keys=[rehber_id], back_populates='rehber_ogrencileri')
    rehber_ogrencileri = db.relationship('Kullanici', back_populates='rehber', foreign_keys=[rehber_id])

    ogretmen_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    ogretmen = db.relationship('Kullanici', remote_side=[id], foreign_keys=[ogretmen_id], back_populates='ogretmen_ogrencileri')
    ogretmen_ogrencileri = db.relationship('Kullanici', back_populates='ogretmen', foreign_keys=[ogretmen_id])

    sinif = db.Column(db.String(10), nullable=True)
    okul_no = db.Column(db.String(20), nullable=True)

    deneme_sonuclari = db.relationship('DenemeSonucu', back_populates='ogrenci', lazy='dynamic')
    gunluk_veriler = db.relationship('GunlukVeri', back_populates='ogrenci', lazy='dynamic')

    def set_password(self, password):
        self.sifre_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.sifre_hash, password)

    def is_rehber(self):
        return self.rol == 'rehber'

    def is_ogretmen(self):
        return self.rol == 'ogretmen'

    def is_ogrenci(self):
        return self.rol == 'ogrenci'

    def __repr__(self):
        return f"<Kullanici {self.kullanici_adi} - Rol: {self.rol}>"
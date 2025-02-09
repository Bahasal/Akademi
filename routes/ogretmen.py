from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from models.kullanici import Kullanici
from models.veri import DenemeSonucu, GunlukVeri
from werkzeug.security import generate_password_hash
from database import db
from routes import ogretmen_bp
from flask import jsonify  # Flask içinden jsonify fonksiyonunu içe aktar
import os

# Öğretmen Dashboard Rotası
@ogretmen_bp.route('/dashboard', endpoint='ogretmen_dashboard')
@login_required
def ogretmen_dashboard():
    if current_user.rol != 'ogretmen':
        flash('Bu sayfaya erişim izniniz yok.', 'danger')
        return redirect(url_for('ogretmen.giris'))

    return render_template('ogretmen/ogretmen_dashboard.html')


# Öğretmen Profil Görüntüleme
@ogretmen_bp.route('/profil')
@login_required
def profil():
    return render_template('ogretmen/profil.html', user=current_user)

# Öğretmen Profil Güncelleme
@ogretmen_bp.route('/profil_guncelle', methods=['POST'])
@login_required
def profil_guncelle():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not username or not password:
        flash("Kullanıcı adı ve şifre boş bırakılamaz.", "danger")
        return redirect(url_for('ogretmen.profil'))  # Profil sayfasına yönlendir

    if password != confirm_password:
        flash("Şifreler uyuşmuyor.", "danger")
        return redirect(url_for('ogretmen.profil'))  # Profil sayfasına yönlendir

    # Kullanıcı bilgilerini güncelle
    current_user.username = username
    current_user.sifre_hash = generate_password_hash(password)  # Şifreyi hashle

    db.session.commit()

    flash("Profil bilgileri başarıyla güncellendi. Lütfen tekrar giriş yapın.", "success")

    logout_user()  # Kullanıcıyı çıkış yaptır
    return redirect(url_for('login'))  # Giriş sayfasına yönlendir



# Öğrenci Listesi
@ogretmen_bp.route('/ogrenci_listesi', methods=['GET'])
@login_required
def ogrenci_listesi():
    if current_user.rol != 'ogretmen':
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('main.index'))
    
    ogrenciler = Kullanici.query.filter_by(ogretmen_id=current_user.id, rol='ogrenci').all()
    return render_template('ogretmen/ogrenci_listesi.html', ogrenciler=ogrenciler)

# Öğrenci Silme
@ogretmen_bp.route('/ogrenci_sil/<int:ogrenci_id>', methods=['POST'])
@login_required
def ogrenci_sil(ogrenci_id):
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, rol='ogrenci', ogretmen_id=current_user.id).first()
    if not ogrenci:
        flash('Geçersiz öğrenci.', 'danger')
        return redirect(url_for('ogretmen.ogrenci_listesi'))
    
    db.session.delete(ogrenci)
    db.session.commit()
    flash(f"{ogrenci.kullanici_adi} adlı öğrenci başarıyla silindi.", 'success')
    return redirect(url_for('ogretmen.ogrenci_listesi'))

#Öğretmen Öğrencinin Dashboardına erişir
@ogretmen_bp.route('/ogrenci/<int:ogrenci_id>/dashboard')
@login_required
def ogrenci_dashboard(ogrenci_id):
    # Öğretmen mi kontrolü
    if current_user.rol != 'ogretmen':
        abort(403)
    
    # Öğrenciyi çek ve öğretmen-öğrenci eşleşmesini kontrol et
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, ogretmen_id=current_user.id).first()
    
    if not ogrenci:
        flash('Öğrenci bulunamadı', 'danger')
        return redirect(url_for('ogretmen.ogrenci_listesi'))
    
    # Öğrencinin dashboard sayfasını render et
    return render_template('ogrenci/ogrenci_dashboard.html', ogrenci=ogrenci)


# Öğretmen öğrencinin günlük çalışmasını görür
@ogretmen_bp.route('/ogrenci/<int:ogrenci_id>/gunluk_veriler')
@login_required
def ogrenci_gunluk_veriler(ogrenci_id):
    # Öğretmenin öğrenciyi görmeye yetkisi olup olmadığını kontrol et
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, ogretmen_id=current_user.id).first()
    if not ogrenci:
        flash("Bu öğrenci sizin listenizde bulunmamaktadır.", "danger")
        return redirect(url_for('ogretmen.ogrenci_listesi'))

    # Günlük verileri çek
    gunluk_verileri = GunlukVeri.query.filter_by(ogrenci_id=ogrenci_id).order_by(GunlukVeri.tarih.desc()).all()

    # Eğer veriler varsa toplamları hesapla
    toplamlar = {
        "namaz": sum([v.namaz for v in gunluk_verileri]),
        "kuran": sum([v.kuran for v in gunluk_verileri]),
        "matematik": sum([v.matematik for v in gunluk_verileri]),
        "fen": sum([v.fen for v in gunluk_verileri]),
        "turkce": sum([v.turkce for v in gunluk_verileri]),
        "sosyal": sum([v.sosyal for v in gunluk_verileri]),
        "ingilizce": sum([v.ingilizce for v in gunluk_verileri]),
        "din": sum([v.din for v in gunluk_verileri]),
        "kitap_okuma": sum([v.kitap_okuma for v in gunluk_verileri]),
    }

    return render_template('ogretmen/ogrenci_gunluk_veriler.html', ogrenci=ogrenci, gunluk_verileri=gunluk_verileri, toplamlar=toplamlar)


# Öğretmen öğrencinin deneme sonuçlarına ulaşır.
@ogretmen_bp.route('/ogrenci/<int:ogrenci_id>/deneme_verileri')
@login_required
def ogrenci_deneme_verileri(ogrenci_id):
    # Öğretmenin öğrenciyi görmeye yetkisi olup olmadığını kontrol et
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, ogretmen_id=current_user.id).first()
    if not ogrenci:
        flash("Bu öğrenci sizin listenizde bulunmamaktadır.", "danger")
        return redirect(url_for('ogretmen.ogrenci_listesi'))

    # Deneme verilerini çek
    deneme_verileri = DenemeSonucu.query.filter_by(ogrenci_id=ogrenci.id).order_by(DenemeSonucu.tarih.desc()).all()

    # Eğer veriler yoksa bir mesaj gösterebiliriz
    if not deneme_verileri:
        flash("Bu öğrencinin deneme sonuçları bulunmamaktadır.", "warning")

    return render_template('ogretmen/ogrenci_deneme_verileri.html', ogrenci=ogrenci, deneme_verileri=deneme_verileri)

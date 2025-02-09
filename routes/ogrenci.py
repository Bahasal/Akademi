from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta


ogrenci_bp = Blueprint("ogrenci", __name__)

# Veritabanı ve modeller
from database import db
from models.veri import GunlukVeri, DenemeSonucu
from models.kullanici import Kullanici

# Formlar
from forms.forms import DenemeSonucuForm

import sqlite3  # SQLite kütüphanesi (gerekli değilse kaldırılabilir)

ogrenci_bp = Blueprint('ogrenci', __name__, url_prefix='/ogrenci')

# Profil Görüntüleme
@ogrenci_bp.route('/profil', methods=['GET'])
@login_required
def profil():
    return render_template('ogrenci/profil.html')

# Profil Güncelleme
@ogrenci_bp.route('/profil_guncelle', methods=['POST'])
@login_required
def profil_guncelle():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not username or not password:
        flash("Kullanıcı adı ve şifre boş bırakılamaz.", "danger")
        return redirect(url_for('ogrenci.profil'))

    if password != confirm_password:
        flash("Şifreler uyuşmuyor.", "danger")
        return redirect(url_for('ogrenci.profil'))

    print(f"Eski Hash: {current_user.sifre_hash}")  # Eski şifre hash'ini kontrol et

    # Kullanıcı bilgilerini güncelle
    current_user.username = username
    current_user.sifre_hash = generate_password_hash(password)  # Doğru alanı kullan

    print(f"Yeni Hash: {current_user.sifre_hash}")  # Yeni hash'i kontrol et

    db.session.commit()

    flash("Profil bilgileri başarıyla güncellendi. Lütfen tekrar giriş yapın.", "success")
    
    logout_user()  # Kullanıcıyı çıkış yaptır
    return redirect(url_for('login'))  # Giriş sayfasına yönlendir

# Giriş İşlemi
@ogrenci_bp.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')

        kullanici = Kullanici.query.filter_by(username=kullanici_adi, rol='ogrenci').first()

        if kullanici and kullanici.check_password(sifre):
            login_user(kullanici)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('ogrenci.ogrenci_dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')

    return render_template('ogrenci/ogrenci_dashboard.html')

# Öğrenci Dashboard
@ogrenci_bp.route('/dashboard/<int:ogrenci_id>', methods=['GET'], endpoint='ogrenci_dashboard')
@login_required
def ogrenci_dashboard(ogrenci_id):
    # Veritabanından öğrenci bilgilerini al
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, rol='ogrenci').first()

    # Eğer öğrenci bulunamazsa, hata mesajı ver ve giriş sayfasına yönlendir
    if not ogrenci:
        flash('Öğrenci bulunamadı.', 'danger')
        return redirect(url_for('ogrenci.giris'))  # Bu rotanın tanımlı olduğundan emin olun!

    # Öğretmen veya rehber mi kontrol et
    if current_user.is_ogretmen():
        # Öğrenci öğretmenin atanmış öğrencisi mi?
        if not current_user.ogretmen_ogrencileri.filter_by(id=ogrenci.id).first():
            flash('Bu öğrenciye erişim izniniz yok.', 'danger')
            return redirect(url_for('ogrenci.giris'))  # Yetkisiz erişimi engelle

    elif current_user.is_rehber():
        # Öğrenci rehberin atanmış öğrencisi mi?
        if not current_user.rehber_ogrencileri.filter_by(id=ogrenci.id).first():
            flash('Bu öğrenciye erişim izniniz yok.', 'danger')
            return redirect(url_for('ogrenci.giris'))  # Yetkisiz erişimi engelle

    # Öğrenciye ait günlük verileri ve deneme sonuçlarını getir
    gunluk_veriler = GunlukVeri.query.filter_by(ogrenci_id=ogrenci.id).order_by(GunlukVeri.tarih.desc()).all()
    deneme_sonuclari = DenemeSonucu.query.filter_by(ogrenci_id=ogrenci.id).order_by(DenemeSonucu.tarih.desc()).all()

    # Şablona öğrenci bilgileri ve verileri ilet
    return render_template(
        'ogrenci/ogrenci_dashboard.html',
        gunluk_veriler=gunluk_veriler,
        deneme_sonuclari=deneme_sonuclari,
        ogrenci=ogrenci
    )

# Çıkış İşlemi
@ogrenci_bp.route('/cikis', methods=['GET'])
@login_required
def cikis():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('ogrenci.giris'))

# Eksik günleri sıfır ile dolduran fonksiyon
def eksik_gunleri_doldur(ogrenci_id):
    bugun = datetime.today().date()
    son_veri = GunlukVeri.query.filter_by(ogrenci_id=ogrenci_id).order_by(GunlukVeri.tarih.desc()).first()

    if son_veri:
        son_tarih = son_veri.tarih
    else:
        son_tarih = bugun - timedelta(days=1)

    while son_tarih < bugun:
        son_tarih += timedelta(days=1)
        if not GunlukVeri.query.filter_by(ogrenci_id=ogrenci_id, tarih=son_tarih).first():
            yeni_kayit = GunlukVeri(
                ogrenci_id=ogrenci_id, tarih=son_tarih,
                namaz=0, kuran=0, matematik=0, fen=0, turkce=0, sosyal=0, 
                ingilizce=0, din=0, kitap_okuma=0
            )
            db.session.add(yeni_kayit)
    
    db.session.commit()

# Günlük Veri Ekleme veya Güncelleme
@ogrenci_bp.route('/gunluk_veri_ekle', methods=['GET', 'POST'])
@login_required
def gunluk_veri_ekle():
    if not (current_user.is_ogrenci() or current_user.is_ogretmen()):
        flash('Bu sayfaya erişim izniniz yok.', 'danger')
        return redirect(url_for('ogrenci.giris'))

    bugun = datetime.today().date()

    if request.method == 'POST':
        tarih_str = request.form.get("tarih")
        tarih = datetime.strptime(tarih_str, "%Y-%m-%d").date() if tarih_str else bugun

        # Sadece son 3 gün güncellenebilir
        if (bugun - tarih).days > 3:
            flash("Sadece son 3 günün verilerini güncelleyebilirsiniz!", "danger")
            return redirect(url_for("ogrenci.gunluk_veri_ekle"))

        mevcut_kayit = GunlukVeri.query.filter_by(ogrenci_id=current_user.id, tarih=tarih).first()
        veri = mevcut_kayit or GunlukVeri(ogrenci_id=current_user.id, tarih=tarih)

        for alan in ['namaz', 'kuran', 'matematik', 'fen', 'turkce', 'sosyal', 'ingilizce', 'din', 'kitap_okuma']:
            setattr(veri, alan, int(request.form.get(alan, 0)))

        if not mevcut_kayit:
            db.session.add(veri)

        db.session.commit()
        flash('Günlük veri başarıyla kaydedildi!', 'success')
        return redirect(url_for('ogrenci.gunluk_veri_ekle'))

    # Eksik günleri doldur
    eksik_gunleri_doldur(current_user.id)

    # Öğrencinin verilerini al
    veriler = GunlukVeri.query.filter_by(ogrenci_id=current_user.id).order_by(GunlukVeri.tarih.desc()).all()

    toplamlar = {alan: sum(getattr(veri, alan) for veri in veriler) for alan in [
        'namaz', 'kuran', 'matematik', 'fen', 'turkce', 'sosyal', 'ingilizce', 'din', 'kitap_okuma']}

    return render_template('ogrenci/gunluk_veri_ekle.html', veriler=veriler, toplamlar=toplamlar, bugun=bugun)

def hesapla_net(dogru, yanlis):
    return dogru - (yanlis / 3)

@ogrenci_bp.route('/deneme_sonucu_ekle', methods=['GET', 'POST'])
@login_required
def deneme_sonucu_ekle():
    form = DenemeSonucuForm()
    if form.validate_on_submit():
        toplam_net = 0
        dersler = ['matematik', 'fen', 'turkce', 'sosyal', 'ingilizce', 'din']
        kayit_yapildi = False

        for ders in dersler:
            dogru = getattr(form, f'dogru_{ders}').data
            yanlis = getattr(form, f'yanlis_{ders}').data
            
            if dogru == 0 and yanlis == 0:
                continue

            net = hesapla_net(dogru, yanlis)
            toplam_net += net
            kayit_yapildi = True

        if not kayit_yapildi:
            flash('En az bir ders için doğru veya yanlış girmelisiniz.', 'danger')
            return render_template('ogrenci/deneme_sonucu_ekle.html', form=form)

        yeni_deneme = DenemeSonucu(
            ogrenci_id=current_user.id,
            tarih=date.today(),
            dogru_matematik=form.dogru_matematik.data,
            yanlis_matematik=form.yanlis_matematik.data,
            net_matematik=hesapla_net(form.dogru_matematik.data, form.yanlis_matematik.data),
            # Diğer dersler için de benzer şekilde
            toplam_net=toplam_net,
        )
        
        try:
            db.session.add(yeni_deneme)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Bir hata oluştu, lütfen tekrar deneyin.', 'danger')
            return redirect(url_for('ogrenci.deneme_sonucu_ekle'))

        flash(f"Deneme başarıyla kaydedildi! Toplam net: {toplam_net:.2f}", "success")
        return redirect(url_for('ogrenci.deneme_sonucu_ekle'))

    # Form geçersiz olduğunda veya ilk kez yükleniyorsa mevcut sonuçları çekin
    mevcut_sonuclar = DenemeSonucu.query.filter_by(ogrenci_id=current_user.id).all()

    return render_template('ogrenci/deneme_sonucu_ekle.html', form=form, mevcut_sonuclar=mevcut_sonuclar)


#Öğrenci deneme sonucunu günceller
@ogrenci_bp.route('/deneme_sonucu_guncelle/<int:sonuc_id>', methods=['GET', 'POST'])
@login_required
def deneme_sonucu_guncelle(sonuc_id):
    sonuc = DenemeSonucu.query.get_or_404(sonuc_id)

    if sonuc.ogrenci_id != current_user.id:
        abort(403)

    form = DenemeSonucuForm(obj=sonuc)

    if form.validate_on_submit():
        form.populate_obj(sonuc)

        # Her ders için net hesapla ve güncelle
        dersler = ['matematik', 'fen', 'turkce', 'sosyal', 'ingilizce', 'din']
        toplam_net = 0  # Toplam neti sıfırla

        for ders in dersler:
            dogru = getattr(form, f'dogru_{ders}').data
            yanlis = getattr(form, f'yanlis_{ders}').data
            
            # Net hesaplama fonksiyonunu kullanarak net değerini güncelle
            net = hesapla_net(dogru, yanlis)
            setattr(sonuc, f'net_{ders}', net)

            # Toplam neti güncelle
            toplam_net += net

        # Toplam neti güncelle
        sonuc.toplam_net = toplam_net

        # Veritabanında güncellemeleri kaydet
        db.session.commit()
        flash('Güncelleme başarılı!', 'success')
        return redirect(url_for('ogrenci.deneme_sonucu_ekle'))

    return render_template('ogrenci/deneme_guncelle.html', form=form)


# Öğrenci deneme sonuçlarını siler.
@ogrenci_bp.route('/deneme_sonucu_sil/<int:sonuc_id>', methods=['POST'])
@login_required
def deneme_sonucu_sil(sonuc_id):
    sonuc = DenemeSonucu.query.get_or_404(sonuc_id)
    
    # Yetki kontrolü
    if sonuc.ogrenci_id != current_user.id:
        abort(403)
    
    db.session.delete(sonuc)
    db.session.commit()
    flash('Deneme sonucu başarıyla silindi!', 'success')
    return redirect(url_for('ogrenci.deneme_sonucu_ekle'))


from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user, login_user
from models.kullanici import Kullanici
from werkzeug.security import generate_password_hash
from database import db
from datetime import datetime

rehber_bp = Blueprint('rehber', __name__)

# Kullanıcı Girişi
@rehber_bp.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')

        if not kullanici_adi or not sifre:
            flash('Kullanıcı adı ve şifre boş bırakılamaz.', 'danger')
            return render_template('login.html')

        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()

        if kullanici and kullanici.check_password(sifre):
            if kullanici.rol == 'rehber':
                login_user(kullanici)
                flash('Giriş başarılı!', 'success')
                return redirect(url_for('rehber.dashboard'))
            else:
                flash('Bu kullanıcı rolü için yetkiniz yok.', 'danger')
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')

    return render_template('login.html')

# Rehber Dashboard
@rehber_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.rol != 'rehber':
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('rehber.giris'))

    return render_template('rehber/rehber_dashboard.html')

# Ana Sayfa
@rehber_bp.route('/anasayfa', methods=['GET'])
@login_required
def anasayfa():
    if current_user.rol != 'rehber':
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('rehber.dashboard'))

    ogretmenler = Kullanici.query.filter_by(rol='ogretmen', kurum_kodu=current_user.kurum_kodu).all()
    ogrenciler = Kullanici.query.filter_by(rol='ogrenci', kurum_kodu=current_user.kurum_kodu).all()

    return render_template('rehber/anasayfa.html', ogretmenler=ogretmenler, ogrenciler=ogrenciler)

# Öğrenci Listesi
@rehber_bp.route('/ogrenci_listesi', methods=['GET'])
@login_required
def ogrenci_listesi():
    if current_user.rol != 'rehber':
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('main.index'))

    ogrenciler = Kullanici.query.filter_by(rehber_id=current_user.id, rol='ogrenci').all()
    return render_template('rehber/ogrenci_listesi.html', ogrenciler=ogrenciler)

# Öğrenci Silme
@rehber_bp.route('/ogrenci_sil/<int:ogrenci_id>', methods=['POST'])
@login_required
def ogrenci_sil(ogrenci_id):
    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, rol='ogrenci').first()
    if not ogrenci or ogrenci.rehber_id != current_user.id:
        flash('Geçersiz öğrenci.', 'danger')
        return redirect(url_for('rehber.ogrenci_listesi'))

    db.session.delete(ogrenci)
    db.session.commit()
    flash(f"{ogrenci.kullanici_adi} adlı öğrenci başarıyla silindi.", 'success')
    return redirect(url_for('rehber.ogrenci_listesi'))

# Öğrenci Dashboard
@rehber_bp.route('/ogrenci_dashboard/<int:ogrenci_id>', methods=['GET'])
@login_required
def rehber_ogrenci_dashboard(ogrenci_id):
    if current_user.rol != 'rehber':
        flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
        return redirect(url_for('rehber.dashboard'))

    ogrenci = Kullanici.query.filter_by(id=ogrenci_id, rol='ogrenci').first()
    if not ogrenci:
        flash('Geçersiz öğrenci seçimi.', 'danger')
        return redirect(url_for('rehber.ogrenci_listesi'))

    deneme_verileri = ogrenci.deneme_sonuclari.all()
    gunluk_verileri = ogrenci.gunluk_veriler.all()

    return render_template(
        'rehber/ogrenci_dashboard.html',
        ogrenci=ogrenci,
        deneme_verileri=deneme_verileri,
        gunluk_verileri=gunluk_verileri
    )
# Öğretmen Listesi
@rehber_bp.route('/ogretmen_listesi', methods=['GET'])
@login_required
def ogretmen_listesi():
    ogretmenler = Kullanici.query.filter(
        Kullanici.rol == 'ogretmen',
        Kullanici.kurum_kodu == current_user.kurum_kodu,
        Kullanici.rehber_id == current_user.id
    ).all()
    return render_template('rehber/ogretmen_listesi.html', ogretmenler=ogretmenler)

#Öğretmen Silme
@rehber_bp.route('/ogretmen_sil/<int:ogretmen_id>', methods=['GET', 'POST'])
@login_required
def ogretmen_sil(ogretmen_id):
    if current_user.rol != 'rehber':
        flash('Bu işlemi gerçekleştirme yetkiniz yok.', 'danger')
        return redirect(url_for('rehber.dashboard'))

    ogretmen = Kullanici.query.get_or_404(ogretmen_id)
    if ogretmen.rol != 'ogretmen':
        flash('Geçersiz öğretmen.', 'danger')
        return redirect(url_for('rehber.ogretmen_listesi'))

    # Öğretmenin öğrencilere atanmış olup olmadığını kontrol et
    for ogrenci in ogretmen.ogretmen_ogrencileri:
        ogrenci.ogretmen_id = None  # Öğrencilerin öğretmeni sıfırlanır
    db.session.delete(ogretmen)
    db.session.commit()
    
    flash(f"{ogretmen.kullanici_adi} adlı öğretmen başarıyla silindi.", 'success')
    return redirect(url_for('rehber.ogretmen_listesi'))


# Atama İşlemleri
@rehber_bp.route('/atama', methods=['GET', 'POST'])
@login_required
def atama():
    tum_ogrenciler = Kullanici.query.filter_by(rehber_id=current_user.id, rol='ogrenci').all()
    ogretmenler = Kullanici.query.filter_by(rehber_id=current_user.id, rol='ogretmen').all()

    if request.method == 'POST':
        ogrenci_id = request.form.get('ogrenci_id')
        ogretmen_id = request.form.get('ogretmen_id')

        if not ogrenci_id or not ogretmen_id:
            flash("Lütfen hem bir öğrenci hem de bir öğretmen seçin.", "warning")
            return redirect(url_for('rehber.atama'))

        ogrenci = Kullanici.query.get(ogrenci_id)
        ogretmen = Kullanici.query.get(ogretmen_id)

        if ogrenci and ogretmen:
            ogrenci.ogretmen_id = ogretmen.id
            db.session.commit()
            flash("Öğrenci başarıyla öğretmene atandı!", "success")
        else:
            flash("Geçersiz seçim yaptınız.", "danger")

        return redirect(url_for('rehber.atama'))

    return render_template('rehber/atama.html', tum_ogrenciler=tum_ogrenciler, ogretmenler=ogretmenler)

# Atama Silme
@rehber_bp.route('/atama_sil/<int:ogrenci_id>', methods=['POST'])
@login_required
def atama_sil(ogrenci_id):
    ogrenci = Kullanici.query.get_or_404(ogrenci_id)
    ogrenci.ogretmen_id = None
    db.session.commit()
    flash('Atama başarıyla silindi!', 'success')
    return redirect(url_for('rehber.atama'))

# Öğretmene ait öğrencileri listeleme
@rehber_bp.route('/ogretmen/<int:ogretmen_id>/ogrenciler', methods=['GET'])
@login_required
def ogretmen_ogrenciler(ogretmen_id):
    ogretmen = Kullanici.query.get_or_404(ogretmen_id)
    ogrenciler = ogretmen.ogretmen_ogrencileri  # Doğrudan liste olarak kullan
    return render_template('rehber/ogretmen_ogrencileri.html', ogretmen=ogretmen, ogrenciler=ogrenciler)

# Profil
@rehber_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    rehber = current_user
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')

        rehber.kullanici_adi = kullanici_adi
        rehber.sifre_hash = generate_password_hash(sifre)
        db.session.commit()

        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('rehber.profil'))

    return render_template('rehber/profil.html', rehber=rehber)



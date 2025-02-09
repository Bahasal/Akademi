from flask import Flask, redirect, url_for, render_template, request, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from database import db, migrate  # Veritabanı nesnesi burada gelir
from models.kullanici import Kullanici  # Kullanıcı modeli
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename  
from routes.ogrenci import ogrenci_bp
from routes.rehber import rehber_bp 
from routes.ogretmen import ogretmen_bp 

def allowed_file(filename):
    """Yalnızca izin verilen uzantılara sahip dosyaların yüklenmesine izin verir."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def create_app():
    # Flask uygulama nesnesini oluştur
    app = Flask(__name__)
    app.secret_key = 'secret-key'  # Flash mesajları için gizli anahtar
    
    # Blueprint'leri kaydedin
    app.register_blueprint(ogrenci_bp, url_prefix='/ogrenci')
    app.register_blueprint(ogretmen_bp, url_prefix='/ogretmen')
    app.register_blueprint(rehber_bp, url_prefix='/rehber')

    # Uygulama yapılandırmasını yükle
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
    
    # Uzantıları uygulamaya bağla
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login yapılandırması
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Lütfen önce giriş yapınız.'

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login için oturumdan kullanıcıyı yükle."""
        return Kullanici.query.get(int(user_id))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        rehberler = Kullanici.query.filter_by(rol='rehber').all()

        if request.method == 'POST':
            kurum_kodu = request.form.get('kurum_kodu')
            kullanici_adi = request.form.get('kullanici_adi')
            sifre = request.form.get('sifre')
            sifre_tekrar = request.form.get('sifre_tekrar')
            rol = request.form.get('rol')
            rehber_id = request.form.get('rehber_id')
            sinif = request.form.get('sinif')
            okul_no = request.form.get('okul_no')

            # Doğrulamalar
            if not kurum_kodu or not kullanici_adi:
                flash("Kurum kodu ve kullanıcı adı gereklidir.", "danger")
                return redirect(url_for('register'))
            
            # Sunucu tarafı kontrolü
            if rol == 'ogrenci' and (not sinif or not okul_no):
                flash('Sınıf ve okul numarası zorunludur!', 'danger')
                return redirect(url_for('register'))

            if sifre != sifre_tekrar:
                flash("Şifreler eşleşmiyor!", "danger")
                return redirect(url_for('register'))

            if rol == 'ogrenci' and (not rehber_id or not sinif or not okul_no):
                flash("Öğrenci kaydı için tüm alanları doldurmanız gereklidir.", "danger")
                return redirect(url_for('register'))

            mevcut_kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
            if mevcut_kullanici:
                flash("Bu kullanıcı adı zaten alınmış!", "danger")
                return redirect(url_for('register'))

            # Kullanıcı oluşturma
            yeni_kullanici = Kullanici(
                kurum_kodu=kurum_kodu,
                kullanici_adi=kullanici_adi,
                sifre_hash=generate_password_hash(sifre),
                rol=rol,
                rehber_id=int(rehber_id) if rehber_id else None,
                sinif=sinif,
                okul_no=okul_no
            )
            try:
                db.session.add(yeni_kullanici)
                db.session.commit()
                flash("Kayıt başarılı!", "success")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash("Kayıt sırasında bir hata oluştu: " + str(e), "danger")
                return redirect(url_for('register'))

        return render_template('register.html', rehberler=rehberler)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            flash('Zaten giriş yaptınız!', 'info')
            return redirect(url_for('index'))

        if request.method == 'POST':
            kullanici_adi = request.form.get('kullanici_adi')
            sifre = request.form.get('sifre')

            kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
            
            if kullanici and check_password_hash(kullanici.sifre_hash, sifre):
                login_user(kullanici)
                flash('Başarıyla giriş yaptınız!', 'success')

                # Kullanıcı rollerine göre yönlendirme yap
                if kullanici.rol == 'ogrenci':
                    return redirect(url_for('ogrenci.ogrenci_dashboard', ogrenci_id=kullanici.id))
                elif kullanici.rol == 'ogretmen':
                    return redirect(url_for('ogretmen.ogretmen_dashboard'))
                elif kullanici.rol == 'rehber':
                    return redirect(url_for('rehber.dashboard'))
                else:
                    flash('Rol bulunamadı, ana sayfaya yönlendirildiniz.', 'warning')
                    return redirect(url_for('index'))  

            else:
                flash('Kullanıcı adı veya şifre hatalı!', 'danger')

        return render_template('login.html')

        

    # Çıkış rotası
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Başarıyla çıkış yaptınız!', 'info')
        return redirect(url_for('anasayfa'))

    # Ana sayfa rotası
    @app.route('/')
    def index():
        return redirect(url_for('anasayfa'))

    @app.route('/anasayfa')
    def anasayfa():
        return render_template('anasayfa.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

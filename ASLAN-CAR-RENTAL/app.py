import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy import extract



app = Flask(__name__)
app.secret_key = 'cok_gizli_anahtar'  # Güvenli anahtar önerilir

basedir = os.path.abspath(os.path.dirname(__file__))

# Veritabanı ayarı aynı kaldı
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'veritabani.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Resimlerin kaydedileceği klasörü statik klasör içindeki resimler olarak ayarla
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'resimler')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MODELLER
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(80), nullable=False)
    marka = db.Column(db.String(80), nullable=False)
    yil = db.Column(db.Integer)
    fiyat_gunluk = db.Column(db.Float)
    image_filename = db.Column(db.String(255))

    kiralamalar = db.relationship("Reservation", backref="car", lazy=True)

    @property
    def durum(self):
        today = date.today()
        for kira in self.kiralamalar:
            if (
                kira.baslangic_tarihi and
                kira.bitis_tarihi and
                kira.baslangic_tarihi.date() <= today <= kira.bitis_tarihi.date() and
                not kira.iade_edildi
            ):
                return "Kirada"
        return "Müsait"



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    profile_image_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(5), default='user')
    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Kullanıcı {self.username}>"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    baslangic_tarihi = db.Column(db.DateTime, nullable=False)
    bitis_tarihi = db.Column(db.DateTime, nullable=False)
    alis_yeri = db.Column(db.String(100), nullable=True)
    iade_yeri = db.Column(db.String(100), nullable=True)
    toplam_tutar = db.Column(db.Float, nullable=True)
    iade_edildi = db.Column(db.Boolean, default=False)
    
    

    def __repr__(self):
        return f"<Rezervasyon {self.id} - Kullanıcı: {self.user_id}, Araç: {self.car_id}>"

# Varsayılan admin kullanıcısı oluşturma (model tanımlarından sonra)
with app.app_context():
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin is None:
        admin_user = User(username='admin', email='admin@example.com', role='admin')
        admin_user.set_password('123456') # <-- BURAYI MUTLAKA DEĞİŞTİRİN!
        db.session.add(admin_user)
        db.session.commit()
        print("Varsayılan 'admin' kullanıcısı oluşturuldu.")


@app.route('/')
def anasayfa():
    return render_template('index.html')

@app.route('/index')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return render_template('karsilama.html', username=user.username)
    flash('Lütfen giriş yapın.', 'warning')
    return redirect(url_for('kullanici_girisi'))

@app.route('/cikis')
def cikis():
    session.pop('user_id', None)  # session'dan kullanıcıyı çıkar
    return redirect(url_for('index'))  # Ana sayfaya yönlendir

@app.route('/arabalarimiz')
def arabalarimiz():
    arabalar = Car.query.all()
    return render_template('arabalarimiz.html', arabalar=arabalar)

@app.route('/iade-et/<int:rezervasyon_id>', methods=['POST'])
def iade_et(rezervasyon_id):
    rezervasyon = Reservation.query.get_or_404(rezervasyon_id)
    if not rezervasyon.iade_edildi:
        rezervasyon.iade_edildi = True
        db.session.commit()
        flash("Araç başarıyla iade edildi.", "success")
    else:
        flash("Bu araç zaten iade edilmiş.", "warning")
    return redirect(url_for('rezervasyonlarim'))

@app.route('/musteriler/listele')
def musterileri_listele():
    musteriler = User.query.all()
    return render_template('musteriler_listele.html', musteriler=musteriler)



@app.route('/rezervasyonlarim')
def rezervasyonlarim():
    if 'user_id' not in session:
        flash('Lütfen giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    user = User.query.get(session['user_id'])

    if user is None:
        session.clear() # Oturumu tamamen temizle
        flash('Kullanıcı bulunamadı veya oturumunuzun süresi doldu. Lütfen tekrar giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))
    

    rezervasyonlar = user.reservations
    return render_template('rezervasyonlarim.html', rezervasyonlar=rezervasyonlar)

@app.route('/iletisim')
def iletisim_sayfasi():
    return render_template('iletisim.html')

@app.route('/giris', methods=['GET', 'POST'])
def kullanici_girisi():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Lütfen e-posta ve şifre giriniz.', 'error')
            return render_template('giris.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['username'] = user.username
            session['role'] = user.role
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Giriş başarısız. E-posta veya şifre hatalı.', 'error')

    return render_template('giris.html')

@app.route('/cikis')
def kullanici_cikisi():
    session.clear()
    flash('Çıkış yapıldı.', 'success')
    return redirect(url_for('anasayfa'))

@app.route('/admin-panel')
def admin_paneli():
    if 'user_id' in session and session.get('role') == 'admin':
        toplam_arac = Car.query.count()

        # Sadece aktif kiralamalar (iade edilmemiş)
        aktif_kiralama = Reservation.query.filter_by(iade_edildi=False).count()

        # Boştaki araç = toplam - aktif kiralanan
        bos_arac = toplam_arac - aktif_kiralama

        # Son 5 rezervasyon
        son_kiralama = Reservation.query.order_by(Reservation.baslangic_tarihi.desc()).limit(5).all()

        # --------------------
        # GELİR HESAPLAMA
        # --------------------

        # Toplam gelir (iade edilmemiş tüm rezervasyonlar)
        toplam_gelir = db.session.query(func.coalesce(func.sum(Reservation.toplam_tutar), 0)).filter(Reservation.iade_edildi == False).scalar()

        # Aylık gelir (bu yıl ve ay)
        now = datetime.now()
        aylik_gelir = db.session.query(func.coalesce(func.sum(Reservation.toplam_tutar), 0)).filter(
            extract('year', Reservation.baslangic_tarihi) == now.year,
            extract('month', Reservation.baslangic_tarihi) == now.month,
            Reservation.iade_edildi == False
        ).scalar()

        # İstersen geçmiş 6 ay için aylık gelirler (grafik için örnek veri)
        gelir_ayliklar = []
        for i in range(5, -1, -1):  # 5 ay öncesinden bugüne
            ay = (now.month - i - 1) % 12 + 1
            yil = now.year + ((now.month - i - 1) // 12)
            gelir = db.session.query(func.coalesce(func.sum(Reservation.toplam_tutar), 0)).filter(
                extract('year', Reservation.baslangic_tarihi) == yil,
                extract('month', Reservation.baslangic_tarihi) == ay,
                Reservation.iade_edildi == False
            ).scalar()
            gelir_ayliklar.append({
                'yil': yil,
                'ay': ay,
                'gelir': round(gelir, 2)
            })

        return render_template('admin_panel.html',
                               total_cars=toplam_arac,
                               rented_cars=aktif_kiralama,
                               available_cars=bos_arac,
                               son_kiralama=son_kiralama,
                               toplam_gelir=round(toplam_gelir, 2),
                               aylik_gelir=round(aylik_gelir, 2),
                               gelir_ayliklar=gelir_ayliklar
                              )
    else:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('anasayfa'))

@app.route('/admin/arac/ekle', methods=['GET', 'POST'])
def arac_ekle():
    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        yil = request.form['yil']
        fiyat = request.form['fiyat']
        image_filename = request.files.get('image')

        # Yeni araç nesnesi oluştur
        yeni_arac = Car(marka=marka, model=model, yil=int(yil), fiyat_gunluk=float(fiyat))
        
        # Veritabanına ekle
        db.session.add(yeni_arac)
        db.session.commit()

        flash('Araç başarıyla eklendi.', 'success')
        return redirect(url_for('admin_arac_listesi'))  # Araçlar sayfasına yönlendir

    # Mevcut yıl değerini dinamik olarak ayarlamak için
    current_year = 2023  # veya datetime.datetime.now().year ile dinamik olarak alabilirsiniz
    return render_template('arac_ekle.html', max_year=current_year)
    
@app.route('/admin/araclar', methods=['GET', 'POST'])
def admin_arac_listesi():
    if 'user_id' in session and session.get('role') == 'admin':
        arabalar = Car.query.all()
        return render_template('arac_liste.html', araclar=arabalar)  # buradaki değişken ismi düzeltildi
    else:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('anasayfa'))
    
@app.route('/admin/kiralamalar', methods=['GET', 'POST'])
def tum_kiralamalar():
    kiralamalar = Reservation.query.order_by(Reservation.baslangic_tarihi.desc()).all()
    return render_template('kiralamalar_listele.html', kiralamalar=kiralamalar)



@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_id' not in session:
        flash('Lütfen giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.city = request.form.get('city')
        user.district = request.form.get('district')
        user.address = request.form.get('address')

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_image_url = filename

        db.session.commit()
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('profil'))

    return render_template('profil.html', user=user)

@app.route('/kayit', methods=['GET', 'POST'])
def kayit_sayfasi():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')

        if not username or not email or not password:
            flash('Lütfen tüm zorunlu alanları doldurun.', 'error')
            return render_template('kayit.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Bu kullanıcı adı veya e-posta zaten kayıtlı.', 'error')
            return render_template('kayit.html')

        yeni_user = User(username=username, email=email, full_name=full_name)
        yeni_user.set_password(password)

        db.session.add(yeni_user)
        db.session.commit()
        flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
        return redirect(url_for('kullanici_girisi'))

    return render_template('kayit.html')

@app.route('/profil_detay', methods=['GET', 'POST'])
def profil_detay():
    user = get_current_user()
    if not user:
        flash('Lütfen giriş yapınız.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.city = request.form.get('city')
        user.district = request.form.get('district')
        user.address = request.form.get('address')

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_image_url = filename

        db.session.commit()
        flash('Profil güncellendi.', 'success')
        return redirect(url_for('profil_detay'))

    return render_template('profil_detay.html', user=user)

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# -----------------------------
# **KİRALAMA İŞLEMİ İÇİN YENİ ROUTE**
@app.route('/kirala/<int:car_id>', methods=['POST'])
def kirala(car_id):
    if 'user_id' not in session:
        flash('Lütfen giriş yapın.', 'warning')
        return redirect(url_for('kullanici_girisi'))

    araba = Car.query.get_or_404(car_id)

    # Formdan gelen veriler
    alis_yeri = request.form.get('alis_yeri')
    iade_yeri = request.form.get('iade_yeri')
    baslangic_str = request.form.get('alis_tarihi')
    bitis_str = request.form.get('iade_tarihi')

    try:
        baslangic_tarihi = datetime.strptime(baslangic_str, '%Y-%m-%d')
        bitis_tarihi = datetime.strptime(bitis_str, '%Y-%m-%d')
    except ValueError:
        flash('Tarih formatı yanlış. YYYY-AA-GG formatında giriniz.', 'error')
        # Kullanıcıyı doğru sayfaya yönlendirmek daha iyi olabilir, örneğin araba detay sayfası veya arabalarimiz sayfası
        return redirect(url_for('arabalarimiz'))

    if bitis_tarihi < baslangic_tarihi:
        flash('Bitiş tarihi başlangıç tarihinden önce olamaz.', 'error')
        # Kullanıcıyı doğru sayfaya yönlendirmek daha iyi olabilir
        return redirect(url_for('arabalarimiz'))

    # **TOPLAM TUTAR HESAPLAMA BAŞLANGIÇ**
    # Kiralama süresini gün olarak hesapla. İki tarih arasındaki farka 1 gün ekliyoruz çünkü başlangıç ve bitiş günü de sayılır.
    delta = bitis_tarihi - baslangic_tarihi
    duration_in_days = delta.days + 1

    # Aracın günlük fiyatını al
    gunluk_fiyat = araba.fiyat_gunluk

    # Toplam tutarı hesapla
    toplam_tutar = gunluk_fiyat * duration_in_days
    # **TOPLAM TUTAR HESAPLAMA BİTİŞ**


    yeni_rezervasyon = Reservation(
        user_id=session['user_id'],
        car_id=car_id,
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi,
        alis_yeri=alis_yeri,
        iade_yeri=iade_yeri,
        # **Hesaplanan toplam tutarı atama**
        toplam_tutar=toplam_tutar
    )
    db.session.add(yeni_rezervasyon)
    db.session.commit()

    flash(f"{araba.marka} {araba.model} aracı başarıyla kiralandı! Toplam Tutar: {toplam_tutar:.2f} TL", 'success') # Flash mesajına tutarı ekledim
    return redirect(url_for('rezervasyonlarim'))

import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

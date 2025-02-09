from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField
from wtforms.validators import InputRequired, NumberRange, ValidationError, DataRequired

class DenemeSonucuForm(FlaskForm):
    # Tarih Alanı Eklendi
    tarih = DateField('Sınav Tarihi', validators=[DataRequired()], format='%Y-%m-%d')
    
    # Deneme Adı Alanı Eklendi
    deneme_adi = StringField('Deneme Adı', validators=[DataRequired()])
    
    # 20 soruluk dersler
    dogru_matematik = IntegerField('Matematik Doğru', validators=[InputRequired(), NumberRange(min=0, max=20)])
    yanlis_matematik = IntegerField('Matematik Yanlış', validators=[InputRequired(), NumberRange(min=0, max=20)])
    dogru_fen = IntegerField('Fen Doğru', validators=[InputRequired(), NumberRange(min=0, max=20)])
    yanlis_fen = IntegerField('Fen Yanlış', validators=[InputRequired(), NumberRange(min=0, max=20)])
    dogru_turkce = IntegerField('Türkçe Doğru', validators=[InputRequired(), NumberRange(min=0, max=20)])
    yanlis_turkce = IntegerField('Türkçe Yanlış', validators=[InputRequired(), NumberRange(min=0, max=20)])

    # 10 soruluk dersler
    dogru_sosyal = IntegerField('Sosyal Doğru', validators=[InputRequired(), NumberRange(min=0, max=10)])
    yanlis_sosyal = IntegerField('Sosyal Yanlış', validators=[InputRequired(), NumberRange(min=0, max=10)])
    dogru_ingilizce = IntegerField('İngilizce Doğru', validators=[InputRequired(), NumberRange(min=0, max=10)])
    yanlis_ingilizce = IntegerField('İngilizce Yanlış', validators=[InputRequired(), NumberRange(min=0, max=10)])
    dogru_din = IntegerField('Din Doğru', validators=[InputRequired(), NumberRange(min=0, max=10)])
    yanlis_din = IntegerField('Din Yanlış', validators=[InputRequired(), NumberRange(min=0, max=10)])

    submit = SubmitField('Kaydet')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        # 20 soruluk dersler için toplam doğrulama
        for ders in ['matematik', 'fen', 'turkce']:
            dogru = getattr(self, f'dogru_{ders}').data or 0
            yanlis = getattr(self, f'yanlis_{ders}').data or 0
            if dogru + yanlis > 20:
                getattr(self, f'dogru_{ders}').errors.append('Toplam en fazla 20 olabilir!')
                getattr(self, f'yanlis_{ders}').errors.append('Toplam en fazla 20 olabilir!')
                return False

        # 10 soruluk dersler için toplam doğrulama
        for ders in ['sosyal', 'ingilizce', 'din']:
            dogru = getattr(self, f'dogru_{ders}').data or 0
            yanlis = getattr(self, f'yanlis_{ders}').data or 0
            if dogru + yanlis > 10:
                getattr(self, f'dogru_{ders}').errors.append('Toplam en fazla 10 olabilir!')
                getattr(self, f'yanlis_{ders}').errors.append('Toplam en fazla 10 olabilir!')
                return False
        
        return True

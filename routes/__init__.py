from flask import Blueprint

# Blueprint tanımları
ogrenci_bp = Blueprint('ogrenci', __name__, url_prefix='/ogrenci')
ogretmen_bp = Blueprint('ogretmen', __name__, url_prefix='/ogretmen')
rehber_bp = Blueprint('rehber', __name__, url_prefix='/rehber')

# Blueprint'lerin rotaları modüllerinden içe aktarılıyor
from routes import ogrenci, ogretmen, rehber

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Veritabanı nesnesi
db = SQLAlchemy()

# Migrate nesnesi
migrate = Migrate()

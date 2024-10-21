import pyotp
import qrcode
import sqlite3
from model import OTPModel
from variables import qrcodes_path, app_name


class OTPController:
    def __init__(self, db_path="otp_data.db"):
        self.db_path = db_path
        self._initialize_db()

    def is_key_valid(self, key):
        return OTPModel.isBase32(key)

    def get_otp(self, label):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM otps WHERE label = ?", (label,))
            row = cursor.fetchone()
            if row:
                return OTPModel(row[1], row[2], row[3])
            return None

    def generate_secret_key(self):
        return pyotp.random_base32()

    def generate_qr_code(self, uri):
        qr = qrcode.make(uri)
        return qr.get_image()

    def get_provisioning_uri(self, label):
        model = self.get_otp(label)
        secret_key = model.secret
        type = model.type
        counter = model.counter
        if type == "totp":
            return pyotp.TOTP(secret_key).provisioning_uri(
                name=label, issuer_name=app_name
            )
        else:
            return pyotp.HOTP(secret_key).provisioning_uri(
                name=label, issuer_name=app_name, initial_count=counter
            )

    def generate_otp(self, model):
        secret_key = model.secret
        type = model.type
        counter = model.counter
        if type == "totp":
            return pyotp.TOTP(secret_key).now()
        else:
            return pyotp.HOTP(secret_key).at(counter)

    def update_hotp_counter(self, label):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE otps 
                SET counter = counter + 1 
                WHERE label = ?
            """,
                (label,),
            )
            conn.commit()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS otps (
                    label TEXT PRIMARY KEY,
                    secret TEXT NOT NULL,
                    type TEXT NOT NULL,
                    counter INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    def add_otp(self, label, secret=None, otp_type=None, counter=None):
        if label and secret and otp_type:
            model = OTPModel(secret, otp_type, counter)
            if self.otp_valid(model):
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO otps (label, secret, type, counter)
                        VALUES (?, ?, ?, ?)
                        """,
                        (label, model.secret, model.type, model.counter),
                    )
                    conn.commit()

    def otp_valid(self, model: OTPModel):
        return isinstance(model, OTPModel) and model.is_model(True)

    def delete_otp(self, label):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM otps WHERE label = ?", (label,))
            conn.commit()

    def get_otps(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM otps")
            otps = cursor.fetchall()
            return {row[0]: OTPModel(row[1], row[2], row[3]) for row in otps}

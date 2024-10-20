import pyotp
import qrcode
from model import OTPManager, OTPModel
from variables import qrcodes_path, app_name


class OTPController:
    def __init__(self):
        self.otp_manager = OTPManager()

    def add_otp(
        self, label, secret=None, type=None, counter=None, model: OTPModel | None = None
    ):
        if not model:
            model = OTPModel(secret, type, counter)
        if label and self.otp_valid(model):
            self.otp_manager.add_otp(label, model)

    def is_key_valid(self, key):
        return OTPModel.isBase32(key)

    def otp_valid(self, model: OTPModel):
        return isinstance(model, OTPModel) and model.is_model(True)

    def delete_otp(self, label):
        self.otp_manager.delete_otp(label)

    def get_otps(self):
        return self.otp_manager.get_otps()

    def get_otp(self, label):
        return self.otp_manager.get_otps()[label]

    def generate_secret_key(self):
        return pyotp.random_base32()

    def generate_qr_code(self, uri, label):
        qr = qrcode.make(uri)
        return qr

    def get_provisioning_uri(self, model, label):
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
        if label in self.otp_manager.otps:
            self.otp_manager.otps[label].counter += 1

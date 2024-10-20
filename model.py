from base64 import b32encode, b32decode


class OTPModel:
    def __init__(self, secret=None, type=None, counter=None):
        self.secret = secret
        self.type = type
        self.counter = counter
        if not self.is_model(self):
            raise ValueError("Wrong setted values")

    def is_model(self, is_check_filling=False):
        type = self.type
        secret = self.secret
        counter = self.counter
        if is_check_filling and (not type or not secret):
            return False
        if type and type not in ["totp", "hotp"]:
            return False
        if secret and not self.isBase32(secret):
            return False
        if counter and not isinstance(counter, int):
            return False
        if type == "hotp" and counter == None:
            return False
        return True

    @staticmethod
    def isBase32(sb):
        try:
            if isinstance(sb, str):
                sb_bytes = bytes(sb, "ascii")
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return b32encode(b32decode(sb_bytes)) == sb_bytes
        except Exception:
            return False


class OTPManager:
    def __init__(self):
        self.otps = {}

    def add_otp(self, label, model: OTPModel):
        self.otps[label] = model

    def delete_otp(self, label):
        if label in self.otps:
            del self.otps[label]

    def get_otps(self):
        return self.otps

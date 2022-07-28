from Crypto.Cipher import AES
import base64
from django.conf import settings


class AESCrypt(object):
    def __init__(self, key=settings.SECRET_KEY[:16], model="ECB", iv="", encode_="gbk"):
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象
        self.encrypt_text = ""

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    def encrypt(self, text):
        text = self.add_16(text)
        encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(encrypt_text).decode().strip()

    def decrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        decrypt_text = self.aes.decrypt(text)
        return decrypt_text.decode(self.encode_).strip('\0')


if __name__ == '__main__':
    pr = AESCrypt()
    en_text = pr.encrypt('fasdfdsdfasdfsdfsdfsdfsddsf')
    print('encrypt:', en_text)
    print('decrypt:', pr.decrypt(en_text))

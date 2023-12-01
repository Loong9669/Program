from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode
import os
from configparser import ConfigParser


def generate_aes_key(password, salt, key_length=32):
    # 使用PBKDF2算法生成符合AES要求的密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt.encode('utf-8'),
        length=key_length,
        backend=default_backend()
    )
    key = kdf.derive(password.encode('utf-8'))
    return key

def encrypt_aes(key, data):
    key_bytes = key
    data_bytes = data.encode('utf-8')
    # 使用固定IV（Initialization Vector）
    iv = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
    # 创建一个AES密码器对象，使用CFB模式
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    # 创建一个加密器对象
    encryptor = cipher.encryptor()
    # 加密数据
    ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
    # 合并IV和密文，然后将结果编码为URL安全的Base64字符串
    encrypted_data = urlsafe_b64encode(iv + ciphertext).decode('utf-8')
    return encrypted_data

# 生成AES密钥
def genarate_passwd(password):
    config = read_config()
    salt = config.get('passwd', 'salt')
    key = generate_aes_key(password, salt, key_length=16)
    # 加密密码
    encrypted_password = encrypt_aes(key, password)
    return encrypted_password

# 读取配置文件
def read_config():
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建配置文件的路径
    config_file_path = os.path.join(current_dir, "../conf/config.ini")
    # 读取配置文件
    config = ConfigParser()
    config.read(config_file_path)
    return config

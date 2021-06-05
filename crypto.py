import base64
import os
import hashlib
import six
# from Crypto import Random
# from Crypto.Cipher import PKCS1_OAEP
# from Crypto.PublicKey import RSA
# import os
#
#
# class PublicKeyFileExists(Exception):
#     pass
#
#
# class RSAEncryption(object):
#     def __init__(self, private_key=None, public_key=None):
#         self.private = private_key
#         self.public = public_key
#         self.pwd = b'pa$$w0rd'
#
#     def encrypt(self, message):
#         public_key = self.get_public_key()
#         public_key_object = PKCS1_OAEP.new(RSA.importKey(public_key), label=self.pwd)
#         encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message))
#         # use base64 for save encrypted_message in database without problems with encoding
#         return base64.b64encode(encrypted_message)
#
#     def decrypt(self, encoded_encrypted_message):
#         encrypted_message = base64.b64decode(encoded_encrypted_message)
#         private_key = self.get_private_key()
#         private_key_object = PKCS1_OAEP.new(RSA.importKey(private_key), label=self.pwd)
#         decrypted_message = private_key_object.decrypt(encrypted_message)
#         return six.text_type(decrypted_message, encoding='utf8')
#
#     def generate_keys(self):
#         """Be careful rewrite your keys"""
#         random_generator = Random.new().read
#         key = RSA.generate(1024, random_generator)
#         self.private, self.public = key.exportKey(), key.publickey().exportKey()
#
#     def get_public_key(self):
#         """run generate_keys() before get keys """
#         return self.public
#
#     def get_private_key(self):
#         """run generate_keys() before get keys """
#         return self.private
#
#     @staticmethod
#     def _to_format_for_encrypt(value):
#         if isinstance(value, int):
#             return six.binary_type(value)
#         for str_type in six.string_types:
#             if isinstance(value, str_type):
#                 return value.encode('utf8')
#         if isinstance(value, six.binary_type):
#             return value


def generate_hash():
    return hashlib.sha1(os.urandom(32)).hexdigest()

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

digestSize = 11
key = RSA.generate(pow(2, digestSize))
public_key = key.public_key().exportKey('PEM')
private_key = key.exportKey('PEM')

message = 'To be signed'
private_key_rsa = RSA.import_key(private_key)
h = SHA256.new(message.encode('utf8'))
signature = pkcs1_15.new(private_key_rsa).sign(h)

public_key_rsa = RSA.import_key(public_key)
h = SHA256.new(message.encode('utf8'))
try:
    pkcs1_15.new(public_key_rsa).verify(h, signature)
    print("The signature is valid.".encode('utf8'))
except (ValueError, TypeError):
   print("The signature is not valid.".encode('utf8'))
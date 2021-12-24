from Crypto.PublicKey import ECC
from wallet import Wallet
import base64
import secrets
from Crypto.Cipher import AES
import hashlib, secrets, binascii
from tinyec import registry
# Generates the keys
#Generate 2 ECC Private keys
wallet = Wallet()

DATA = {'sender': 'Bob', 'receiver': 'Jen', 'amount': 100.0}

key1 = ECC.generate(curve='P-256')
key2 = ECC.generate(curve='P-256')

# with open('keys_der.pem', 'wb') as f:
# 	""" key generation """
# 	f.write(key1.export_key(format='DER'))
def generate_priv_key():
	""" generates private key """
	password = wallet.password()
	with open('priv-keys_pem.pem', 'w') as f:
		""" key generation """
		key = key1.export_key(format='PEM', passphrase=password, protection='PBKDF2WithHMAC-SHA1AndAES128-CBC')
		f.write(key)
		f.close()
		return {'private key': key, 'passphrase': password}

# close('priv-keys_pem.pem')
# with open('keys_SEC.pem', 'wb') as f:
# 	""" key generation """
# 	f.write(key1.export_key(format='SEC1'))
	# print(password)

# Create public key
def generate_pub_key():
	""" generates public key """
	# private_key = f'priv-keys_pem.pem'
	with open('pub-keys_pem.pem', 'w') as f:
		""" Write the public key """
		priv_key = key1
		pubkey = priv_key.public_key().export_key(format='PEM')
		f.write(pubkey)
		return pubkey
	# privkey = ECC.import_key(f)
	# privkey.export_key(f, passphrase=PASSWORD, protection='PBKDF2WithHMAC-SHA1AndAES128-CBC')
def ecc_point_to_256_bit_key(point):
    sha = hashlib.sha256(int.to_bytes(point.x, 32, 'big'))
    sha.update(int.to_bytes(point.y, 32, 'big'))
    return sha.digest()

def encrypt_message(key, message):
	""" Encrypts the message """
	curve = registry.get_curve('brainpoolP256r1')
	# f = open(key, 'rb')
	# pubkey = ECC.import_key(f)
	# pubkey = str(pubkey)
	# pubkey = key
	# pubkey = pubkey.encode()
	# print(pubkey)
	# print(type(pubkey))
	# cipher = AES.new(pubkey, AES.MODE_CBC) # Create a AES cipher object with the key using the mode CBC
	# ciphered_data = cipher.encrypt(pad(message, AES.block_size)) # Pad the input data and then encrypt
	# file = f'{message}.bin'
	# file_out = open(file, "wb") # Open file to write bytes
	# file_out.write(cipher.iv) # Write the iv to the output file (will be required for decryption)
	# file_out.write(ciphered_data) # Write the varying length ciphertext to the file (this is the encrypted data)
	# file_out.close()
	ciphertextPrivKey = secrets.randbelow(curve.field.n)
	sharedECCKey = ciphertextPrivKey * key
	secretKey = ecc_point_to_256_bit_key(sharedECCKey)
	ciphertext, nonce, authTag = (message, secretKey)
	ciphertextPubKey = ciphertextPrivKey * curve.g
	return (ciphertext, nonce, authTag, ciphertextPubKey)


def decrypt_message(filename, message):
	""" Decrypts the  """

if __name__ == '__main__':
	privkey_and_passphrase = generate_priv_key()
	privkey = privkey_and_passphrase['private key']
	passphrase = privkey_and_passphrase['passphrase']
	pubkey = generate_pub_key()
	encrypt_message(key=pubkey, message=DATA)
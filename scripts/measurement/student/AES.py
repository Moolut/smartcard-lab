from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def aes_ecb_encrypt(key, plaintext):
    # Create AES cipher in ECB mode
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plaintext)

def aes_ecb_decrypt(key, ciphertext):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

# Example usage
if __name__ == "__main__":
    # Key must be 16, 24, or 32 bytes
    key = b"0" * 16
    plaintext = b"Hello, AES in ECB Mode!"

    # Encrypt the plaintext
    ciphertext = aes_ecb_encrypt(key, plaintext)
    print(f"Ciphertext (hex): {ciphertext.hex()}")

    # Decrypt the ciphertext
    decrypted_plaintext = aes_ecb_decrypt(key, ciphertext)
    print(f"Decrypted Plaintext: {decrypted_plaintext.decode('utf-8')}")

def hexVector2number(row):
    result = 0x00
    for bytenum in range(16):
        result = result | (int(row[bytenum]) << (15 - bytenum) * 8)
        
    num_bytes = (result.bit_length() + 7) // 8 or 1
    return result.to_bytes(num_bytes, 'big')


def compare_result(ct, pt, key):
    ct = hexVector2number(ct)
    pt = hexVector2number(pt)
    encrypted = aes_ecb_encrypt(key, pt)
    
    correct_enc = False
    correct_dec = False
    
    if encrypted == ct:
        correct_enc = True
    else:
        correct_enc = False
        
    decrypted = aes_ecb_decrypt(key, ct)

    if decrypted == pt:
        correct_dec = True
    else:
        correct_dec = False
        
    return True if correct_enc and correct_dec else False
from util.encryptionUtil import xor_encode, xor_decode

str1 = "dr@gmail.com"
print("Original String:", str1)
encoded_str = xor_encode(str1)
print("Encoded String:", encoded_str)
decoded_str = xor_decode(encoded_str)
print("Decoded String:", decoded_str)
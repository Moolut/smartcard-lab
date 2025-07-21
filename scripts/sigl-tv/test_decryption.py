#!/usr/bin/env python3

# T. Music 05/2023

# This script attempts to perform a decryption with random ciphertexts and checks
# whether the card works correctly.

import os
import sys
import hjson
import binascii

from time import sleep
from smartcard.CardType import ATRCardType
from smartcard.ATR import ATR
from smartcard.CardConnection import CardConnection
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes, toASCIIString, bs2hl
import Crypto.Cipher.AES

key_ascii = "00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF"
print(f"Reference Key: {key_ascii}\n")

try:
    key = binascii.unhexlify(key_ascii.replace(" ", ""))
    if (len(key) != 16):
        print(f"    Error: Key length is {len(key)}, but expected length is 16")
        exit(1)
    # print(key)
except Exception as ex:
    print(ex)
    print("Error parsing key -> please fix")
    exit(1)

cardtype = ATRCardType( toBytes( "3B 90 11 00" ) )
atr = ATR( toBytes( "3B 90 11 00" ) )
if not atr.isT0Supported():
  print ("Error: Card does not support T0 protocol.")

cardrequest = CardRequest( timeout=5, cardType=cardtype )

## Wait for the card to be present:
## In case the card is in the reader, this command will return immediately.
print("Waiting for card....")
cardservice = cardrequest.waitforcard()

cardservice.connection.connect( CardConnection.T0_protocol )
print("Connected to card with T0 protocol")

sample_data      = os.urandom(16)
cmd_decrypt_key  = [0x88, 0x10, 0, 0, len(sample_data)] + list(sample_data)
cmd_get_response = [0x88, 0xc0, 0x00, 0x00, 0x10]

sample_data_ascii = " ".join("{:02x}".format(d) for d in sample_data)

print(f"Sample Data to decrypt: {sample_data_ascii}\n")

print ('sending ' + toHexString(cmd_decrypt_key))
response, sw1, sw2 = cardservice.connection.transmit(cmd_decrypt_key)
print ('response: ', response, ' status words: ', "%x %x" % (sw1, sw2))
## There will be no response here, but the card answers with sw1=0x61, sw2=0x10,
## indicating that there are 16 (=0x10) bytes to read now.

## Now we fetch the decrypted chunk key using the GET_RESPONSE command:
print ('sending ' + toHexString(cmd_get_response))
response, sw1, sw2 = cardservice.connection.transmit(cmd_get_response)
print ('response: ', response, ' status words: ', "%x %x" % (sw1, sw2))

print("")

# Calculate the expected result for the selected key
aes_device = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_ECB)
expected_response = aes_device.decrypt(sample_data)

expected_response_ascii = " ".join("{:02x}".format(d) for d in expected_response)
returned_response_ascii = " ".join("{:02x}".format(d) for d in response)
print(f"Returned plaintext:  {returned_response_ascii}")
print(f"Expected platintext: {expected_response_ascii}")

if returned_response_ascii == expected_response_ascii:
    print("Responses Match :)")
else:
    print("Response MISMATCH. Please check key")

print("\nClosing connection. Bye.")
cardservice.connection.disconnect()


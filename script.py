#!/usr/bin/env python

# Imports
import secrets
import json
import codecs
import ecdsa
import hashlib
import base58
import requests
import time
import logging

from smtplib import SMTP_SSL as SMTP

wif = ""
fileName = 'privatekeys_' + time.strftime("%m-%d-%Y-%H-%M") + '.csv'

logging.basicConfig(filename = fileName, level=logging.INFO, format = '%(message)s', datefmt = '%Y-%m-%d-%H-%M')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("blockcypher").setLevel(logging.WARNING)
logging.info('TIMESTEP - WifKey - PublicAddress')

def ping_address(publicAddress):
    global pk
    global wif
    global publicKey

    response = requests.get("https://blockstream.info/api/address/"+ publicAddress)

    if response.ok:
        ourJson = response.json()
        balance = dict(ourJson['chain_stats'])['funded_txo_sum']
        print(balance)
    else:
        print("[ERROR] " + response.text)
        raise ValueError("cannot reach block explorer for balance", response)
    
    logging.log(time.strftime("%m-%d-%Y-%H-%M") + " - " + wif.decode('utf-8') + " - " + publicAddress)

    if float(balance) > 0.00000000:
        logging.log(time.strftime("%m-%d-%Y-%H-%M") + " - ", wif.decode('utf-8') + " - " + publicAddress + "$: " + str(balance))
        print("++++++ SUCCESS ++++++")
        print("Congatulations, alert the world cause you just made some sort of history friend!")
        print(wif.decode('utf-8'))
        print("++++++ SUCCESS ++++++")
        with open('result.txt', 'a+') as f:
            f.write(time.strftime("%m-%d-%Y-%H-%M") + " - ", wif.decode('utf-8') + " - " + publicAddress + "$: " + str(balance))
            f.close

def wif_conversion(pk):
	global wif
	padding = '80' + pk
	# print( padding )

	hashedVal = hashlib.sha256(codecs.decode(padding, 'hex')).hexdigest()
	checksum = hashlib.sha256(codecs.decode(hashedVal, 'hex')).hexdigest()[:8]
	# print( hashedVal )
	# print( padding+checksum )

	payload = padding + checksum
	wif = base58.b58encode(codecs.decode(payload, 'hex'))
	print( wif.decode('utf-8') )
	

while True:

	pk = secrets.token_hex(32)
	wif_conversion(pk)

	sk = ecdsa.SigningKey.from_string(codecs.decode(pk, "hex"), curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()
	publicKey = "\04" + str(vk.to_string())
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(hashlib.sha256(codecs.encode(publicKey)).digest())
	networkAppend = b'\00' + ripemd160.digest()
	checksum = hashlib.sha256(hashlib.sha256(networkAppend).digest()).digest()[:4]
	binary_address = networkAppend + checksum
	publicAddress = base58.b58encode(binary_address)
	print( publicAddress.decode('utf-8') )
	while True:
		try:
			ping_address(publicAddress.decode('utf-8'))
			# probably does nothing...who knows ;)
			time.sleep(.47)	
		except ValueError:
			print( "Aaaannnnd we got Timed Out" )
			print( pk )
			print( publicAddress )
			time.sleep(3)
			continue
		except KeyError:
			print( "we may be denied or something, keep the script moving" )
			time.sleep(10)			
		break
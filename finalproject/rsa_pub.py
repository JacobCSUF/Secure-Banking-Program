from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP
import Crypto.Signature.pkcs1_15
import msgpack
from Crypto.Signature import DSS
from Crypto.PublicKey import DSA

class RSA_crypto:

    def __init__(self,digsig_type_,key):
        
        self.pub_and_priv = key
        if digsig_type_ == 'DSA':
            self.digsig = DSA.generate(1024)
        self.digsig_type = digsig_type_

    
    #handles public encryption
    def public_encrypt(self, message, public_key_):
        private_key = self.pub_and_priv
        public_key = public_key_
        text = msgpack.dumps(message)

        #digital signature
        hash = SHA256.new(text)
        if self.digsig_type == 'DSA':
            
            sig =  DSS.new(self.digsig, 'fips-186-3')
            signature = sig.sign(hash)
        else: 
            sig = Cryptodome.Signature.pkcs1_15.new(private_key)
            signature = sig.sign(hash)
           
        #public encryption
        cipher_encrypt = PKCS1_OAEP.new(public_key, hashAlgo=None, mgfunc=None, randfunc=None)
        encrypted_text = cipher_encrypt.encrypt(text)
        
        return encrypted_text, signature
        
    
    
    
    #Handles private decryption
    
    def private_decrypt(self, message, public_key_):
        text = message[0]
        digsig = message[1]

        private_key = self.pub_and_priv
        public_key = public_key_
        ready_decrypt = PKCS1_OAEP.new(private_key, hashAlgo=None, mgfunc=None, randfunc=None)
        decrypt = ready_decrypt.decrypt(text)
       
        
        #verify digsig
        hash = SHA256.new(decrypt)
        if self.digsig_type != 'DSA':
            try:
                Cryptodome.Signature.pkcs1_15.new(public_key).verify(hash, digsig)
                
            except (ValueError, TypeError):
                print("Invalid RSA signature, sender not authenticated")

        else:
            try:
                verify_ = DSS.new(public_key, 'fips-186-3')
                verify_.verify(hash, digsig)
                
               
            except (ValueError, TypeError):
                print("Invalid DSA signature, sender not authenticated")


        yayaya = msgpack.loads(decrypt)
        
        return yayaya
        


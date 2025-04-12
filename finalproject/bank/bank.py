import socket
import matplotlib
from Crypto.PublicKey import RSA
from Crypto.PublicKey import DSA

import msgpack
import threading

import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import rsa_pub
import bank_services
import time

#sets the actions of each thread(atm that connects)
def do_thread(atm_sock):
    atm_location = ''
    user = ''
    #Encrypts and sends a message to the atm
    def send_rsa(message):
        confirmation, digsig = bank_RSA.public_encrypt(message,atm_public)
        combined = (confirmation, digsig)
        
        combined_bytes = msgpack.packb(combined)
        
        atm_sock.send(combined_bytes)
    


    #Recieves and decrypts message sent from atm
    def recieve_rsa():
        atm_msg = atm_sock.recv(2048)
        both = msgpack.unpackb(atm_msg)
        if bank_RSA.digsig_type == 'DSA':
            message = bank_RSA.private_decrypt(both,atm_dsa)
        else:
            message = bank_RSA.private_decrypt(both,atm_public)
        if len(user) == 0:
            print(f'\n\nMessage from: {atm_location}')
        else:
            print(f'\n\nMessage from: {atm_location}, ID: {user}')
        return message

    #connects to atm
    atm_msg = atm_sock.recv(2048) 
    decoded = atm_msg.decode()
    atm_location = decoded
    print(f'\n{atm_location} connected to bank')

    msg = 'Connected'
    atm_sock.send(msg.encode())



    atm_msg = atm_sock.recv(2048)
    decoded = atm_msg.decode()

    bank_RSA = rsa_pub.RSA_crypto(decoded,bank_priv)
    
   #sets atm's public key depending on which atm connects
    if atm_location == 'atm1-OrangeCounty':
        with open ("atm1_public.pem", "rb") as pub_file:
            contents = pub_file.read()
            atm_public = RSA.importKey(contents)
    else:
        with open ("atm2_public.pem", "rb") as pub_file:
            contents = pub_file.read()
            atm_public = RSA.importKey(contents)


    
    
    #if DSA is being used then the bank/atm exchanges public DSA keys
    if bank_RSA.digsig_type == 'DSA':
        atm_dsa_ = atm_sock.recv(2048)
        atm_dsa = DSA.import_key(atm_dsa_)
        bank_DSA = bank_RSA.digsig.public_key()
        byte_bank_public = bank_DSA.export_key()
        atm_sock.send(byte_bank_public)
        print(f'{atm_location} DSA digital signature verified')
    else: 
        print(f'{atm_location} RSA digital signature verified')
        


    #handles user login
    while True:
        id_pass = recieve_rsa()
        id = id_pass[0]
        password = id_pass[1]
        verification = bank_control.verify_login(id,password)
        
        if verification:
            print("Login Successful from atm\n")
            send_rsa(('Success',0))
            user = id
            break
        else:
            print('Invalid login from atm\n')
            send_rsa(('Failure',0))

        
            

    
    #controls all the 1-5 inputs from atm
    while True:
        #recieving choice/value
        option = recieve_rsa()
        print(option)

        #displays money
        if option[0] == 1:
            amount = bank_control.display_money(user)
            send_rsa((amount,0))

        #adds money
        elif option[0] == 2:
            amount_to_add = option[1]
            bank_control.add_money(amount_to_add,user)
            amount = bank_control.display_money(user)
            send_rsa((amount,0))


        #subtracts money
        elif option[0] == 3:
            amount_to_sub = option[1]
            bank_control.withdraw_money(amount_to_sub,user)
            amount = bank_control.display_money(user)
            send_rsa((amount,0))


        #displays all transactions
        elif option[0] == 4:
            transactions = bank_control.get_user_transactions(user)
            
            for i in transactions:
               
                
                send_rsa((i,len(transactions)))

                time.sleep(.1)

        #ends connection
        elif option[0] == 5:
            print(f'{atm_location}, ID: {user} Disconnected from services\n\n')
            break
        




#START

BANK_PORT = 1213
BANK_IP = "127.0.0.1"
bank_sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bank_sock.bind((BANK_IP,BANK_PORT))
bank_sock.listen(8)

bank_control = bank_services.Bank_services()


with open ("bank_private.pem", "rb") as priv_file:
	contents = priv_file.read()
	bank_priv = RSA.importKey(contents)




try:
    print("Bank connected")
    while True:

    #recieving public key from atm RSA
        atm_socket_, atm_info = bank_sock.accept()
        
        thread= threading.Thread(target= do_thread, args =(atm_socket_,))
        thread.start() 

except KeyboardInterrupt:
    print('Bank server closing')

finally:
    bank_sock.close()
    print("Bank server closed")
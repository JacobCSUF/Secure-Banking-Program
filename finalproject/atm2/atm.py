import socket
import pwinput
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import rsa_pub
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey import DSA
import msgpack
 
#sending encrypted messages RSA
def send_rsa(message):
    id_pass, digsig = atm_RSA.public_encrypt((message),bank_public)
    combined = (id_pass, digsig)
    combined_bytes = msgpack.dumps(combined)
    atm_sock.send(combined_bytes)

#recieving and decrypting message RSA
def recieve_rsa():
    confirmation = atm_sock.recv(2048)
   
    both = msgpack.loads(confirmation)
    if atm_RSA.digsig_type == 'DSA':
        decrypt_confirmation = atm_RSA.private_decrypt(both,bank_DSA)
    else:
        decrypt_confirmation = atm_RSA.private_decrypt(both,bank_public)
    return decrypt_confirmation

#makes sure input is a valid integer and small
def get_int_input(message):
    while True:
        try:
            
            x = input(message)
            if len(x) > 10:
                raise ValueError()
            return int(x)
        except ValueError:
            print("Please make sure you enter a number and that its not more than several million")
   


#makes sure user specifies a digsig when running program
if len(sys.argv) != 2:
    print('Please specify which digital signature type you want: (RSA or DSA)')
    sys.exit()
else: 
    digsig_type = sys.argv[1]
    if digsig_type == 'RSA' or digsig_type == 'DSA':
        pass
    else:
        print('Please specify which digital signature type you want: (RSA or DSA)')
        sys.exit()

#connects to bank
BANK_IP = "127.0.0.1"
BANK_PORT = 1213
atm_sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
atm_sock.connect((BANK_IP,BANK_PORT))

msg = 'atm2-San Diego County'.encode()
atm_sock.send(msg)

confirm_ = atm_sock.recv(2048)

msg = digsig_type.encode()
atm_sock.send(msg)

#sets atm's private key
with open ("atm2_private.pem", "rb") as priv_file:
	contents = priv_file.read()
	atm_priv = RSA.importKey(contents)
    
#sets banks public key
with open ("bank_public.pem", "rb") as pub_file:
	contents = pub_file.read()
	bank_public = RSA.importKey(contents)
   

atm_RSA = rsa_pub.RSA_crypto(digsig_type,atm_priv)



#if DSA digsig is used then sends/recieves DSA public key
if atm_RSA.digsig_type == 'DSA':
    atm_public = atm_RSA.digsig.public_key()
    byte_atm_public = atm_public.export_key()
    atm_sock.send(byte_atm_public)
    bank_pub_byte = atm_sock.recv(2048)
    bank_DSA = DSA.import_key(bank_pub_byte)
    print('Bank DSA digital signature verified')
else: 
    print('Bank RSA digital signature verified')




print("**********************************************************************")
print("                      Welcome to BIGCOOL BANKS                        ")
print("**********************************************************************")
print("\nLogin:")
while True:
    id = input("Please enter your 6 digit ID: ")
    if len(id) != 6:
        print('\nID is only 6 digits')
        continue
    password = pwinput.pwinput("Please enter your password: ")
    if len(password) > 30:
        print('\nInvalid Login, Try again')
        continue

    #Sending password RSA
    id_pass = (id,password)
    send_rsa(id_pass)

    #Recivining confirmation for id/pass
    confirm = recieve_rsa()
    if confirm[0] == 'Success':
        print("\nLogin Successful")
        break
    if confirm[0] == 'Failure':
        print("\nInvalid Login, Try again")


while True:
    print('\n')
    print('**********************************************************************')
    print('                          Account Services                            ')
    print('**********************************************************************')
    print('Display money:  1')
    print('Deposit money:  2')
    print('Withdraw money: 3')
    print('View history:   4')
    print('Exit:           5')
    print('**********************************************************************')
    x = get_int_input('Choose an option (1-5): ')
    print('\n\n')
    value = 0

    #displays money
    if x == 1:
        send_rsa((x,value))
        money_in_account = recieve_rsa()
        print(f"\nYou currently have ${money_in_account[0]} in your bank account")

    #adds money
    if x == 2:
        value = get_int_input('How much money would you like to deposit? ')
        send_rsa((x,value))
        money_in_account = recieve_rsa()
        print(f"\n${value} deposited in your account" )
        print(f"\nYou now have ${money_in_account[0]} in your bank account")

    #subtracts money
    elif x == 3:
        value = get_int_input("How much money would you like to withdraw? ")
        send_rsa((x,value))
        money_in_account = recieve_rsa()
        print(f"\n${value} withdrawed from your account" )
        print(f"\nYou now have ${money_in_account[0]} in your bank account")

    #shows all transactions
    elif x == 4:

        print('')
        send_rsa((x,value))
        transaction_list = []
        transactions = recieve_rsa()
     
        counter = transactions[1]
        transaction_list.append(transactions[0])
        i = 1
        while i < counter:
            partial = recieve_rsa()
            
            transaction_list.append(partial[0])
            i = i+1
        
        
        for j in transaction_list:
            print(j)
       
    #exit
    elif x == 5:
        send_rsa((x,value))

        break

        

        

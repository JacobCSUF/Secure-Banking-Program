import bcrypt
import json
import datetime 

with open('user_info.json') as json_file:
    user_data = json.load(json_file)

 
class Bank_services:

    def __init__(self):
        pass

    #verifies that the login info is correct
    def verify_login(self,id,password):
        
        with open('db.txt','r') as file:
            for text in file:
                parts = text.split()
                if id == parts[0]:
                    stored_pass = parts[1]
                    stored_pass = stored_pass.encode(encoding='utf-8')
                    password = password.encode(encoding='utf-8')
                    if bcrypt.checkpw(password, stored_pass):
                        
                        return True
                    else: 
                        return False
    
    #returns amount of money user has
    def display_money(self,id):
        return user_data[id]['money']
    
    #adds money to users account
    def add_money(self, ammount,id):
        user_data[id]['money'] = (user_data[id]['money'] + ammount)
        
        str_to_add = f"Deposited ${ammount}"
        self.add_transaction_to_json(str_to_add,id)

        with open('user_info.json', 'w') as file:
            json.dump(user_data, file,indent= 3)

    #withdraws money from users account
    def withdraw_money(self,ammount,id):
        user_data[id]['money'] = (user_data[id]['money'] - ammount)
        
        str_to_add = f"Withdrawed ${ammount}"
        self.add_transaction_to_json(str_to_add,id)

        with open('user_info.json', 'w') as file:
            json.dump(user_data, file,indent= 3)



    #helper function to add transaction string to json
    def add_transaction_to_json(self,transaction_str,id):
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        all =  transaction_str + ' at ' +formatted_date_time
        user_data[id]['transactions'].append(all)

    #returns a list of all of a users transactions
    def get_user_transactions(self,id):
        return user_data[id]['transactions']


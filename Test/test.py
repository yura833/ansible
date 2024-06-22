import json
import os

print("                WELCOME TO MY WEBSITE                               ")
print("                Click login or Register                             ")


def load_data(database_name):
    if not os.path.exists(database_name) or os.path.getsize(database_name) == 0:
        return {}
    with open(database_name, 'r') as data_f:
        database_content = json.load(data_f)
        return database_content


filename = 'database.json'

while True:
    user_input = input("Try: ")
    if user_input == 'login':
        dictionary = load_data(filename)
        user_auth = input("What's your username: ")
        pass_auth = input("WHat's your password: ")
        if pass_auth == dictionary[user_auth]:
            print('Successfuly Logged in')
        else:
            print('Could not Register,Incorrect Password or Username')

    elif user_input == 'register':
        loading_data = load_data(filename)
        username = input("Enter your name: ")
        password = input("Enter your password: ")

        loading_data[username] = password

        with open(filename, 'w') as f:
            json.dump(loading_data, f)


    else:
        print("                Thanks for visiting my site")
        break

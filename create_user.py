import getpass

import streamlit as st
import streamlit_authenticator as stauth

from config import Config
from src.adapters import Controller

print('***CREATE USER***')
name     = input('name (add your name): ')
username = input('username: ')
email    = input('email: ')
password = getpass.getpass()

hashed_passwords = stauth.Hasher([password]).generate()

#############################################################
### REGISTRY USER ###
#############################################################

controller = Controller()
request    = {'resource': '/user/registry',
                'user_username' : username,
                'user_email'    : email,
                'user_name'     : name,
                'user_password' : hashed_passwords[-1],
            }

resp       = controller(request=request)

messages = resp['messages']
entities = resp['entities']

if messages:
    raise Exception('\n\n'.join(messages))

print(f'User {username} created successfully.')
#############################################################


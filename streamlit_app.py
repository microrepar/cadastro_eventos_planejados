"""Application's entry point
Project name: Calendário Secretaria e Eventos Temáticos
Author: McSilva
Description: Cadastro de eventos temáticos da prefeitura.
"""
import streamlit as st

from src.adapters import Controller


from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from dotenv import load_dotenv
from yaml.loader import SafeLoader

from src.adapters.controller import Controller

# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5678))
# ptvsd.wait_for_attach() # Only include this line if you always want to attach the debugger

load_dotenv()

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Dashboard Folha", page_icon=":spiral_calendar:", layout="wide")

placeholder_msg = st.empty()

config_file = Path(__file__).parent / 'config.yaml'
with config_file.open('rb') as file:
    config = yaml.load(file, Loader=SafeLoader)

#############################################################
### GET ALL USERS ###
#############################################################
controller = Controller()
request    = {'resource': '/user'}
resp       = controller(request=request)
#############################################################
messages = resp['messages']
entities = resp['entities']
#############################################################

credentials = {'usernames': {}}
if not messages:
    for user in entities:
        credentials['usernames'].setdefault(user.username, {})
        credentials['usernames'][user.username]['name'] = user.name
        credentials['usernames'][user.username]['email'] = user.email
        credentials['usernames'][user.username]['password'] = user.password
else:
    placeholder_msg.warning('\n\n'.join(messages))

config['credentials'] = credentials
st.session_state.credentials = credentials

authenticator = stauth.Authenticate(
    config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
    config['cookie']['name'],           # cookie:           str
    config['cookie']['key'],            # cookie:           str
    config['cookie']['expiry_days'],    # cookie:           str
    config['preauthorized'],            # preauthorized:    List[str]
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    st.session_state.username = username


    #############################################################
    ### ALL USERS PLACEHOLDER###
    #############################################################
    st.markdown(f'## ALL REGISTRED USERS')
    placeholder_get_all_users = st.empty()
    #############################################################


    #############################################################
    ### REGISTRY USER ###
    #############################################################
    st.markdown('## REGISTRY USER')

    controller = Controller()
    request    = {'resource': '/user/registry',
                'user_name': 'test',
                'user_age': 36,
                'user_username': 'username_test',
                'user_password': 'password_test',
                }

    st.write(request)

    if st.button('Add', type='primary'):
        resp       = controller(request=request)

        st.write(resp)
    #############################################################


    #############################################################
    ### UPDATE USER ###
    #############################################################
    st.markdown('## UPDATE USER')

    controller = Controller()
    request    = {'resource': '/user/update',
                'user_id_': 1,
                'user_name': 'codigo100cera',
                'user_age': 36,
                'user_username': 'username_test',
                'user_password': 'password_test',
                }

    st.write(request)

    if st.button('Update', type='primary'):
        resp       = controller(request=request)

        st.write(resp)
    #############################################################


    #############################################################
    ### REMOVE USER ###
    #############################################################
    st.markdown('## REMOVE USER')

    controller = Controller()
    request    = {'resource': '/user/remove',
                'user_id_': 1
                }

    st.write(request)

    if st.button('Remove', type='primary'):
        resp       = controller(request=request)

        st.write(resp)
    #############################################################


    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user'}
    resp       = controller(request=request)
    #############################################################

    placeholder_get_all_users.write(resp)
    #############################################################

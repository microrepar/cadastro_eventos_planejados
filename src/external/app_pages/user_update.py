import pickle
from pathlib import Path

import pandas as pd
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

from src.adapters import Controller

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

add_page_title()

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


st.session_state['username'] = st.session_state['username']
if st.session_state.username:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    try:
        col1, col2 = st.columns(2)
        selected_username = col1.selectbox('Username', list(credentials['usernames']))
        field = col2.selectbox('Field', ['name', 'email'])

        new_value = None
        actual_value = None

        with st.form("my_form"):   
            st.write("### Update user detail")
            actual_value = st.text_input('Actual value', 
                          value=credentials['usernames'][selected_username][field], 
                          disabled=True)
            new_value = st.text_input('New value')
            # Every form must have a submit button.
            submitted = st.form_submit_button("UPDATE USER", type="primary")

        if submitted:
            #############################################################
            ### UPDATE USER ###
            #############################################################
            request = {'resource': '/user/update_detail',
                       'user_username': selected_username 
                       }
            request.setdefault(f'user_{field}', new_value)

            controller = Controller()
            resp = controller(request=request)
            msg = resp.get('messages')
            
            messages = resp['messages']
            entities = resp['entities']

            if messages:
                raise Exception('\n\n'.join(messages))
            #############################################################

            st.success(f'User change {field} from "{actual_value}" to "{new_value}" registred successfully')       

    except Exception as e:
        placeholder_msg.error(e)
        st.error(e)

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user'}
    resp       = controller(request=request)
    #############################################################
    messages = resp['messages']
    entities = resp['entities']

    if messages:
        placeholder_msg.erro('\n\n'.join(messages), icon='🚨')
    #############################################################

    st.divider()

    if entities:
        st.markdown('### Users')
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")

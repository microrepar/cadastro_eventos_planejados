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
    user_dict = {}
    for user in entities:
        credentials['usernames'].setdefault(user.username, {})
        credentials['usernames'][user.username]['name'] = user.name
        credentials['usernames'][user.username]['email'] = user.email
        credentials['usernames'][user.username]['password'] = user.password
        user_dict[user.username] = user
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
username = st.session_state['username']

if st.session_state.username:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    st.divider()
    st.markdown('### Eventos planejados cadastrados')
    #############################################################
    ### GET ALL PLANNEDEVENT ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/planned_event',
                #   'plannedevent_user_id': user_dict[username].id,
                  }
    resp       = controller(request=request)
    #############################################################
    messages = resp.get('messages', [])
    entities = resp.get('entities', [])
    # st.write(resp)
    #############################################################

    if entities:
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        placeholder_data_editor = st.empty()

        editor_config = {
            'nome': st.column_config.TextColumn('Nome do evento', required=True),
            'tematica': st.column_config.TextColumn('Temática do evento'),
            'data_inicio': st.column_config.DateColumn('Data início', format='DD/MM/YYYY'),
            'data_fim': st.column_config.DateColumn('Data fim', format='DD/MM/YYYY'),
            'descricao': st.column_config.TextColumn('Breve descrição'),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False


        if st.button('Reset', type='primary', key='reset_update'):
            st.session_state.flag_reset = not st.session_state.flag_reset
        
        placeholder_alert_empty = st.empty()
        placeholder_error_empty = st.empty()
        placeholder_success_empty = st.empty()
        
        disable_fields = ['id']
        if st.session_state.flag_reset:
            editor_key = 'update_data1'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        key=editor_key)                
        else:
            editor_key = 'update_data'
            edited_df = placeholder_data_editor.data_editor(df, 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        key=editor_key)
        
        # st.write(st.session_state[editor_key])
        
        if st.session_state[editor_key].get('deleted_rows'):  
            
            flag_contem_admin = False
            
            error_messages = []
            alert_messages = []            
            nome_evento_list = list()
            for index in st.session_state[editor_key]['deleted_rows']:
                
                nome_evento = df.iloc[index]['nome']                                
                
            
                plannedevent_id = df.iloc[index]['id']                    
                #############################################################
                ### DELETE PLANNEDEVENT BY ID ###
                #############################################################
                controller = Controller()
                request    = {'resource': '/planned_event/delete',
                            'plannedevent_id_': plannedevent_id}
                resp       = controller(request=request)
                #############################################################
                messages = resp['messages']
                entities = resp['entities']

                if messages:
                    error_messages += messages
                else:
                    nome_evento_list.append(nome_evento)
                #############################################################
            
            if error_messages:
                placeholder_error_empty.error('\n\n'.join(error_messages), icon='🚨')
            
            if alert_messages:
                placeholder_alert_empty.warning('\n\n'.join(alert_messages), icon='⚠️')

            if nome_evento_list:
                placeholder_success_empty.success(f'Foram removidos os seguintes eventos: {", ".join(nome_evento_list)}')


            st.session_state[editor_key]['deleted_rows'] = []
        
        
        if st.session_state[editor_key].get('edited_rows'):                
            placeholder_alert_empty.error('Changing records via the board is not allowed, please use the form to add new users.', icon='🚨')

        if st.session_state[editor_key].get('added_rows'):
            placeholder_alert_empty.error('Adding new records via the board is not allowed, please use the form to add new users.', icon='🚨')
    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")
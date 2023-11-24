"""Application's entry point
Project name: Calendário Secretaria e Eventos Temáticos
Author: McSilva
Description: Cadastro de eventos temáticos da prefeitura.
"""
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import Page, Section, add_page_title, show_pages
from yaml.loader import SafeLoader

from src.adapters import Controller

# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5678))
# ptvsd.wait_for_attach() # Only include this line if you always want to attach the debugger



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Planned Event Calendar", page_icon=":spiral_calendar:", layout="wide")

placeholder_msg = st.empty()

config_file = Path(__file__).parent / 'src/external/app_pages' / 'config.yaml'
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

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password to access application")

if authentication_status:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    st.session_state.username = username

    if username == 'admin':
        show_pages(
            [   Page("streamlit_app.py", "PLANEJAMENTO DE EVENTOS", "📅"),
                Page("src/external/app_pages/eventos_cadastrados.py", "EVENTOS CADASTRADOS", "📄"),
                # Page("src/external/app_pages/calendar.py", "Calendar", "🗓️"),
                # Section(name="Notebooks", icon=":books:"),
                # # Can use :<icon-name>: or the actual icon 
                Page("src/external/app_pages/user_update.py", "User update", "🔄️"),
                Page("src/external/app_pages/signup.py", "Sign up", "🔑"),
            ]
        )
    else:
        show_pages(
            [Page("streamlit_app.py", "PLANEJAMENTO DE EVENTOS", "📅"),]
        )

    add_page_title()

    # with st.form("my_form"):   
    #     st.write("Formulário de Cadastro dos Eventos Planejados")
    #     nome_evento = st.text_input('Nome do evento:red[*]')
    #     organizador = st.text_input('Organizador', value=name, disabled=True)
        
    #     cb_nova_tematica = st.checkbox('Adicionar nova temática')
    #     if cb_nova_tematica:
    #         tematica_evento = st.text_input('Temática do Evento:red[*]', placeholder='Nome do tema como: Dia das Crianças ou Dia da Consciência Negra, etc...')
    #     else:
    #         tematica_evento = st.selectbox('Temática do Evento:red[*]',[], placeholder='Não encontrou a temática, marque a caixa acima do form e adicione uma nova')

    #     col1, col2 = st.columns(2)
    #     data_inicio = col1.date_input('**Data início**:red[*]', None, format='DD/MM/YYYY')
    #     data_fim = col2.date_input('**Data fim**:red[*]', None, format='DD/MM/YYYY')
    #     descricao = st.text_area('Descrição', placeholder='Breve descrição sobre o que está planejado para o evento')
        

    #     # Every form must have a submit button.
    #     submitted = st.form_submit_button("REGISTRAR NOVO EVENTO", type="primary", use_container_width=True)
    
    st.divider()
    with st.container():
        st.markdown("### Formulário de Cadastro dos Eventos Planejados")
        nome_evento = st.text_input('**Nome do evento**:red[*]')
        organizador = st.text_input('**Organizador**', value=name, disabled=True)
        
        col1, *col = st.columns(3)
        if col1.checkbox('Nova temática'):
            tematica_evento = st.text_input('**Adicione a Temática do Evento**:red[*]', 
                                            placeholder='Adicione aqui a temática, exemplo: "Dia das Crianças" ou "Dia da Consciência Negra", etc...')
        else:
            #############################################################
            ### GET ALL TEMATICA ###
            #############################################################
            controller = Controller()
            request    = {'resource': '/planned_event/get_all_tematicas'}
            resp       = controller(request=request)
            #############################################################
            messages = resp.get('messages', [])
            tematica_list = resp.get('objects', [])
            # st.write(resp)
            #############################################################
            if tematica_list:
                msg_placeholder = 'Selecione uma temática ou adicione uma nova marcando a caixa acima'
            else:
                msg_placeholder = 'Atenção! Não há temáticas cadastradas, adicione uma marcando a caixa acima'

            tematica_evento = st.selectbox('**Selecione a Temática do Evento**:red[*]', 
                                           tematica_list, 
                                           index=None, 
                                           placeholder=msg_placeholder)

        col1, col2 = st.columns(2)
        data_inicio = col1.date_input('**Data início**:red[*]', None, format='DD/MM/YYYY')
        data_fim = col2.date_input('**Data fim**:red[*]', None, format='DD/MM/YYYY')
        descricao = st.text_area('**Descrição**', placeholder='Breve descrição sobre o que está planejado para o evento')
        

        # Every form must have a submit button.
        submitted = st.button("REGISTRAR NOVO EVENTO", type="primary", use_container_width=True)

        # Finalizando o contorno personalizado
        st.write("</div>", unsafe_allow_html=True)


    if submitted:
        #############################################################
        ### REGISTRY PLANNEDEVENT ###
        #############################################################
        controller = Controller()
        request    = {'resource': '/planned_event/registry',
                      'plannedevent_nome'        : nome_evento,
                      'plannedevent_tematica'    : tematica_evento,
                      'plannedevent_data_inicio' : data_inicio,
                      'plannedevent_data_fim'    : data_fim,
                      'plannedevent_descricao'   : descricao,
                      'plannedevent_user_id'     : user_dict[username].id,
                    }

        #############################################################
        resp = controller(request=request)
        messages = resp['messages']
        
        if messages:
            st.error('\n\n'.join(messages), icon='🚨')
        else:
            st.success(f'O Evento **{nome_evento}** foi cadastrado com sucesso.')
        #############################################################


    st.divider()
    st.markdown('### Eventos planejados cadastrados')
    #############################################################
    ### GET ALL PLANNEDEVENT ###
    #############################################################
    controller = Controller()
    request = {'resource': '/planned_event',
               'plannedevent_user_id': user_dict[username].id,}
    resp = controller(request=request)
    #############################################################
    messages = resp.get('messages', [])
    entities = resp.get('entities', [])
    # st.write(resp)
    #############################################################

    if entities:
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        placeholder_data_editor = st.empty()

        editor_config = {
            'nome'        : st.column_config.TextColumn('Nome do evento', required=True),
            'tematica'    : st.column_config.TextColumn('Temática do evento'),
            'data_inicio' : st.column_config.DateColumn('Data início', format='DD/MM/YYYY'),
            'data_fim'    : st.column_config.DateColumn('Data fim', format='DD/MM/YYYY'),
            'descricao'   : st.column_config.TextColumn('Breve descrição'),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False


        if st.button('Reset', type='primary', key='reset_update'):
            st.session_state.flag_reset = not st.session_state.flag_reset
        
        placeholder_alert_empty = st.empty()
        placeholder_error_empty = st.empty()
        placeholder_success_empty = st.empty()
        
        disable_fields = ['id']
        visible_fields = ['nome' ,'tematica' ,'data_inicio' ,'data_fim' ,'descricao' ,]
            
        if st.session_state.flag_reset:
            editor_key = 'update_data1'
            edited_df = placeholder_data_editor.data_editor(df[visible_fields], 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        key=editor_key)                
        else:
            editor_key = 'update_data'
            edited_df = placeholder_data_editor.data_editor(df[visible_fields], 
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
                request = {'resource': '/planned_event/delete',
                              'plannedevent_id_': plannedevent_id}
                resp = controller(request=request)
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
        st.markdown(':red[Atteption! There are no registred planned events.]')

else:
    show_pages(
        [Page("streamlit_app.py", "PLANEJAMENTO DE EVENTOS", "📅"),]
    )
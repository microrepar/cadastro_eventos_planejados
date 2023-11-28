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

if 'user_dict' not in st.session_state:
    st.session_state.user_dict = {}

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
user_dict = {}
if not messages:
    for user in entities:
        credentials['usernames'].setdefault(user.username, {})
        credentials['usernames'][user.username]['name'] = user.name
        credentials['usernames'][user.username]['email'] = user.email
        credentials['usernames'][user.username]['password'] = user.password
        user_dict[user.username] = user
    st.session_state.user_dict = user_dict
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
            [   Page("streamlit_app.py", "CAD-EVENTOS PMMC", "📅"),
                Page("src/external/app_pages/eventos_cadastrados.py", "Eventos Cadastrados", "📄"),
                # Page("src/external/app_pages/calendar.py", "Calendar", "🗓️"),
                # Section(name="Notebooks", icon=":books:"),
                # # Can use :<icon-name>: or the actual icon 
                Page("src/external/app_pages/user_update.py", "User update", "🔄️"),
                Page("src/external/app_pages/signup.py", "Sign up", "🔑"),
            ]
        )
    else:
        show_pages(
            [Page("streamlit_app.py", "CAD-EVENTOS PMMC", "📅"),]
        )

    add_page_title()

    st.divider()
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
        msg_placeholder = ('Selecione uma temática ou adicione '
                           'uma nova marcando a caixa abaixo')
    else:
        msg_placeholder = ('Atenção! Não há temáticas cadastradas, '
                           'adicione uma marcando a caixa abaixo')
    #############################################################

    with st.container():
        st.markdown("### Formulário de Cadastro dos Eventos Planejados")
        nome_evento = st.text_input('**Nome do evento**:red[*]')
        organizador = st.text_input('**Organizador**', value=name, disabled=True)
        
        placeholder_tematica_field = st.empty()
        col1, *col = st.columns(3)
        if col1.checkbox('  Nova temática'):
            tematica_evento = placeholder_tematica_field.text_input('**Adicione a Temática do Evento**:red[*]', 
                                            placeholder='Adicione aqui a temática, exemplo: "Dia das Crianças" ou "Dia da Consciência Negra", etc...')
        else:            
            tematica_evento = placeholder_tematica_field.selectbox('**Selecione a Temática do Evento**:red[*]', 
                                           tematica_list, 
                                           index=None, 
                                           placeholder=msg_placeholder)

        st.divider()
        col1, col2 = st.columns(2)
        data_inicio = col1.date_input('**Data início**:red[*]', None, format='DD/MM/YYYY')
        data_fim = col2.date_input('**Data fim**:red[*]', None, format='DD/MM/YYYY')
        descricao = st.text_area('**Descrição**', placeholder='Breve descrição sobre o que está planejado para o evento')
        

        # Every form must have a submit button.
        submitted = st.button("💾 SALVAR", type="primary", use_container_width=True)

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
            st.error('\n  -'.join(messages), icon='🚨')
        else:
            st.success(f'O Evento **{nome_evento}** foi cadastrado com sucesso.')
        #############################################################

    st.divider()
    st.markdown('### Eventos Cadastrados')
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
            'tematica'    : st.column_config.SelectboxColumn('Temática do evento', options=tematica_list, required=True),
            'data_inicio' : st.column_config.DateColumn('Data início', format='DD/MM/YYYY', required=True),
            'data_fim'    : st.column_config.DateColumn('Data fim', format='DD/MM/YYYY', required=True),
            'descricao'   : st.column_config.TextColumn('Breve descrição'),
        }

        if 'flag_reset' not in st.session_state:
            st.session_state.flag_reset = False
        
        if 'flag_btn_update' not in st.session_state:
            st.session_state.flag_btn_update = False
        
        if 'flag_btn_delete' not in st.session_state:
            st.session_state.flag_btn_delete = False
        
        def on_click_reset_data_editor(*args, **kwargs):
            st.session_state.flag_reset = not st.session_state.flag_reset
            if kwargs.get('key') == 'edited_rows':
                st.session_state[editor_key][kwargs['key']] = {}
            elif kwargs.get('key') == 'deleted_rows':
                st.session_state[editor_key][kwargs['key']] = []
        
        def on_click_btn_update(*args, **kwargs):
            st.session_state.flag_btn_update = kwargs.get('flag', True)
        
        def on_click_btn_delete(*args, **kwargs):
            st.session_state.flag_btn_delete = True

        placeholder_text_area = st.empty()
        cols = st.columns(3)
        with cols[0]:
            placeholder_btn_reset_update = st.empty()
        with cols[1]:
            placeholder_btn_cancelar = st.empty()

        # placeholder_btn_reset_update.button('Reset', 
        #                                        type='primary',
        #                                        on_click=on_click_reset_data_editor,
        #                                        use_container_width=True,
        #                                        key='reset_update')
        
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
                                                        on_change=on_click_btn_update,
                                                        kwargs={'flag': False},
                                                        key=editor_key)                
        else:
            editor_key = 'update_data'
            edited_df = placeholder_data_editor.data_editor(df[visible_fields], 
                                                        num_rows="dynamic", 
                                                        use_container_width=True,
                                                        column_config=editor_config,
                                                        disabled=disable_fields,
                                                        on_change=on_click_btn_update,
                                                        kwargs={'flag': False},
                                                        key=editor_key)
        
        if st.session_state[editor_key].get('deleted_rows'):
            
            if not st.session_state.flag_btn_delete:
                nome_evento_list = list()
                for index in st.session_state[editor_key]['deleted_rows']:
                    nome_evento = df.iloc[index]['nome']
                    nome_evento_list.append(nome_evento)
            
                placeholder_text_area.text_area('**:red[CONFIRME A EXCLUSÃO DO(S) EVENTO(S) A SEGUIR:]**', 
                                                value='- ' + '\n- '.join(nome_evento_list),
                                                disabled=True)
            
                placeholder_btn_reset_update.button(f'Confirmar Exclusão', 
                                                    type='primary',
                                                    on_click=on_click_btn_delete,
                                                    use_container_width=True,
                                                    key='btn_delete')
                
                placeholder_btn_cancelar.button('Cancelar',
                                                type='primary',
                                                on_click=on_click_reset_data_editor,
                                                kwargs={'key':'deleted_rows'},
                                                use_container_width=True,
                                                key='reset_update_concluir')
                                                        
            if st.session_state.flag_btn_delete:
                st.session_state.flag_btn_delete = False
                
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
                    placeholder_error_empty.error('\n  -'.join(error_messages), icon='🚨')
                
                if alert_messages:
                    placeholder_alert_empty.warning('\n  -'.join(alert_messages), icon='⚠️')

                if nome_evento_list:
                    placeholder_success_empty.success(f'**Foram removidos os seguintes eventos:** {", ".join(nome_evento_list)}')


                st.session_state[editor_key]['deleted_rows'] = []
                
        
        if st.session_state[editor_key].get('edited_rows'):
            # st.write(st.session_state[editor_key])

            if not st.session_state.flag_btn_update: 
                placeholder_btn_reset_update.button('Salvar Alterações', 
                                                    type='primary',
                                                    on_click=on_click_btn_update,
                                                    use_container_width=True,
                                                    key='btn_update')

                placeholder_btn_cancelar.button('Cancelar',
                                                type='primary',
                                                on_click=on_click_reset_data_editor,
                                                kwargs={'key':'edited_rows'},
                                                use_container_width=True,
                                                key='reset_update_concluir')
                                                            
            if st.session_state.flag_btn_update:
                st.session_state.flag_btn_update = False
                
                evento_list = []
                error_messages = []
                
                edited_rows = st.session_state[editor_key].get('edited_rows')
                
                for index, value in st.session_state[editor_key]['edited_rows'].items():                    
                    id_evento          = df.iloc[index]['id']
                    nome_evento        = value.get('nome') or df.iloc[index]['nome']
                    tematica_evento    = value.get('tematica') or df.iloc[index]['tematica']
                    data_inicio_evento = value.get('data_inicio') or df.iloc[index]['data_inicio']
                    data_fim_evento    = value.get('data_fim') or df.iloc[index]['data_fim']
                    descricao_evento   = value.get('descricao') or df.iloc[index]['descricao']

                    #############################################################
                    ### DELETE USER BY ID ###
                    #############################################################
                    controller = Controller()
                    request    = {
                        'resource'         : '/plannedevent/update_detail',
                        'plannedevent_id_'         : id_evento,                        
                        'plannedevent_nome'        : nome_evento,
                        'plannedevent_tematica'    : tematica_evento,
                        'plannedevent_data_inicio' : data_inicio_evento,
                        'plannedevent_data_fim'    : data_fim_evento,
                        'plannedevent_descricao'   : descricao_evento,
                    }
                    resp = controller(request=request)
                    #############################################################
                    messages = resp['messages']
                    entities = resp['entities']

                    if messages:
                        error_messages += messages
                    else:
                        evento_list.append(nome_evento)

                    #############################################################
                    # st.write(request)

                btn_update_ok = False
                if error_messages:
                    placeholder_error_empty.error('\n  -'.join(error_messages), icon='🚨')                    
                    st.session_state.flag_btn_update = True
                    btn_update_ok = True                        
                
                if evento_list:
                    st.session_state.flag_btn_update = False
                    on_click_reset_data_editor({'key':'edited_rows'})
                    
                    placeholder_btn_cancelar.empty()
                    placeholder_btn_reset_update.button('Concluir', use_container_width=True)
                    placeholder_data_editor.success(f'**Foram atualizados os seguintes eventos:** {", ".join(evento_list)}')
                    
                
                if btn_update_ok: 
                    placeholder_btn_cancelar.button('Cancelar',
                                                    type='primary',
                                                    on_click=on_click_reset_data_editor,
                                                    kwargs={'key':'edited_rows'},
                                                    use_container_width=True,
                                                    key='reset_update_concluir')
                                                                
                    placeholder_btn_reset_update.button('Salvar Alterações', 
                                                        type='primary',
                                                        on_click=on_click_btn_update,
                                                        use_container_width=True,
                                                        key='btn_update')
                

                            
                     
                    


        if st.session_state[editor_key].get('added_rows'):
            placeholder_alert_empty.error('Não é permitido adicionar novos eventos por meio do quadro! Por favor, clique em cancelar e use o formulário de cadastro.', icon='🚨')
            placeholder_btn_reset_update.button('Cancelar',
                                                    type='primary',
                                                    on_click=on_click_reset_data_editor,
                                                    kwargs={'key':'added_rows'},
                                                    use_container_width=True,
                                                    key='reset_update_concluir')
        

    else:
        st.markdown(f':red[Atenção! Não há eventos cadastrados pelo usuário **{name}**.]')

else:
    show_pages(
        [Page("streamlit_app.py", "CAD-EVENTOS PMMC", "📅"),]
    )
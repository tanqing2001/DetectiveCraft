import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

AUTH_CONFIG_LOC = None
AUTH_CONFIG = None

def set_config(config_path):
    global AUTH_CONFIG
    global AUTH_CONFIG_LOC
    with open(config_path) as file:
        AUTH_CONFIG_LOC = config_path
        AUTH_CONFIG = yaml.load(file, Loader=SafeLoader)


def authenticate_user():
    authenticator = stauth.Authenticate(
        AUTH_CONFIG['credentials'],
        AUTH_CONFIG['cookie']['name'],
        AUTH_CONFIG['cookie']['key'],
        AUTH_CONFIG['cookie']['expiry_days'],
        AUTH_CONFIG['preauthorized']
    )
    name, authentication_status, username = authenticator.login('main')
    return name, username, authentication_status, authenticator

def custom_logout(authenticator):
    authenticator.authentication_handler.execute_logout()
    authenticator.cookie_handler.delete_cookie()

def all_users():
    return AUTH_CONFIG['credentials']['username']

#################### User Auth #######################
def _register_credentials(username: str, name:str, password:str, email: str,
                          security_q: str, security_q_answer:str, preauthorization:bool):
    global AUTH_CONFIG

    AUTH_CONFIG['credentials']['usernames'][username] = {'name': name,
                                                         'password': Hasher([password]).generate()[0],
                                                         'email': email,
                                                         'security_question': security_q,
                                                         'security_answer': Hasher([security_q_answer]).generate()[0]}
    if preauthorization:
        AUTH_CONFIG['preauthorized']['emails'].remove(email)
    with open(AUTH_CONFIG_LOC, 'w') as file:
        yaml.dump(AUTH_CONFIG, file)


def register_user(preauthorization = False):
    register_user_form = st.form("Register User")
    register_user_form.subheader("Register Account")
    new_email = register_user_form.text_input("Email")
    new_username = register_user_form.text_input("Username").lower()
    new_name = register_user_form.text_input('Your Name')
    new_password = register_user_form.text_input("Password", type = 'password')
    new_password_repeat = register_user_form.text_input("Repeat Password", type = 'password')

    security_q_list = ['What city were you born in?',
                       "What is your oldest sibling's middle name?",
                       'What was the first concert you attended?',
                       'What was the make and model of your first car?',
                       'In what city or town did your parents meet?',
                       'What city was your grandparent born in?',
                       'What was the name of your first pet?']
    security_q = register_user_form.selectbox("Security Question", security_q_list)
    security_q_answer = register_user_form.text_input("Answer")

    if register_user_form.form_submit_button("Register"):
        if len(new_email) and len(new_username) and len(new_name) and len(new_password) and len(security_q) and len(security_q_answer) > 0:
            if new_username not in AUTH_CONFIG['credentials']['usernames']:
                if new_password == new_password_repeat:
                    if preauthorization:
                        if new_email in AUTH_CONFIG['preauthorized']['emails']:
                            _register_credentials(new_username, new_name, new_password, new_email,
                                                  security_q, security_q_answer, preauthorization)
                            st.success('Successfully registered account. Please proceed to log in!')
                        else:
                            raise Exception("User not preauthorized to register")
                    else:
                        _register_credentials(new_username, new_name, new_password, new_email,
                                                  security_q, security_q_answer, preauthorization)
                        st.success('Successfully registered account. Please proceed to log in!')
                else:
                    raise Exception("Passwords do not match")
            else:
                raise Exception("Username already taken")
        else:
            raise Exception("Please fill in all fields!")

def _verify_cred(username, email, q_answer = None):
    if username in AUTH_CONFIG['credentials']['usernames']:
        if AUTH_CONFIG['credentials']['usernames'][username]['email'] == email:
            st.session_state['v_cred_form_completed'] = (1, 0)
            if q_answer is not None:
                if bcrypt.checkpw(q_answer.encode(),
                                  AUTH_CONFIG['credentials']['usernames'][username]['security_answer'].encode()):
                    st.session_state['v_cred_form_completed'] = (1, 1)

def _set_new_password(username, pw):
    global AUTH_CONFIG
    AUTH_CONFIG['credentials']['usernames'][username]['password'] = pw
    with open(AUTH_CONFIG_LOC, 'w') as file:
        yaml.dump(AUTH_CONFIG, file)

def reset_password():
    if 'v_cred_form_completed' not in st.session_state:
        st.session_state['v_cred_form_completed'] = (0, 0)

    reset_password_form = st.form('Reset password')
    username = reset_password_form.text_input("Username")
    email = reset_password_form.text_input("Email")
    if reset_password_form.form_submit_button("Verify Credentials"):
        _verify_cred(username, email)
        if st.session_state['v_cred_form_completed'][0] == 0:
            st.error("Credentials not found or does not match our records!")

    if st.session_state['v_cred_form_completed'][0] == 1:
        security_form = st.form('s_q_form')
        s_question = security_form.markdown('Security Question: ' + AUTH_CONFIG['credentials']['usernames'][username]['security_question'])
        q_answer = security_form.text_input("Answer")
        if security_form.form_submit_button("Answer"):
            _verify_cred(username, email, q_answer)
            if st.session_state['v_cred_form_completed'][1] == 0:
                st.error("Credentials not found or does not match our records!")

    if st.session_state['v_cred_form_completed'][1] == 1:
        new_password_form = st.form('new pw', clear_on_submit = True)
        new_password = new_password_form.text_input("New Password", type='password')
        new_password_repeat = new_password_form.text_input('Repeat Password', type='password')
        if new_password_form.form_submit_button('Reset Password'):
            if new_password == new_password_repeat:
                hash_pw = Hasher([new_password]).generate()[0]
                _set_new_password(username, hash_pw)
                st.success('Successfully reset password!')
            else:
                st.error('Passwords do not match. Please try again!')
                       
                                                      










                                                         



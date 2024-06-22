import streamlit as st
import authentication as auth

def main():
    if 'authentication_status' not in st.session_state:
        st.switch_page('ui_navigator.py')
    
    def logout_user():
        st.session_state['authentication_status'] = False
    logout_butt = st.button('Logout', key = 'logout_001', on_click=logout_user)
    if logout_butt:
        st.switch_page('navigator.py')
        
    st.write("Welcome, :orange[" + st.session_state['name'] + ']! :tulip:')
    st.divider()
    st.markdown(':rainbow[==== This is a placeholder for future **FANCY** User Dashboard ====]')
    st.divider()
    st.write('Games:')
    if st.button('Game 1'):
        st.switch_page('pages/game_ui.py')
    # print('dashboard', st.session_state)
    
if __name__ == '__main__':
    main()
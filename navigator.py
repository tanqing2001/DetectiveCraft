import streamlit as st
from time import sleep
import authentication as auth
import pages.user_dashboard as user_dashboard

def main():
    st.set_page_config(initial_sidebar_state = 'collapsed')
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
        </style>
        """,
            unsafe_allow_html=True,
        )
    
    if ('authentication_status' in st.session_state) and (st.session_state['authentication_status'] == False):
        name, username, authentication_status, authenticator = auth.authenticate_user()
        auth.custom_logout(authenticator)
    else:
        name, username, authentication_status, authenticator = auth.authenticate_user()
    
    if st.session_state['authentication_status']:
        sleep(0.5)
        # TODO: reset all session_state variables of game
        # authenticator.logout('Logout', 'main')
        # user_dashboard.user_dashboard(name)
        # if st.button('Game 1'):
        st.switch_page("pages/user_dashboard.py")
    
    else:
        if st.session_state['authentication_status'] == False:
            st.error('Username/password is incorrect')
        st.divider()
        st.markdown("#### Need Help?")
        with st.expander('New User', expanded = False):
            try:
                auth.register_user()
            except Exception as e:
                st.error(e)
        with st.expander("Forgot Password", expanded = False):
            auth.reset_password()


    # if st.button("Log in", type="primary"):
    #     if username == "test" and password == "test":
    #         st.session_state.logged_in = True
    #         st.success("Logged in successfully!")
    #         sleep(0.5)
    #         st.switch_page("pages/game_ui.py")
    #     else:
    #         st.error("Incorrect username or password")


if __name__ == '__main__':
    auth.set_config('user_data/streamlit_config.yaml')
    main()


    
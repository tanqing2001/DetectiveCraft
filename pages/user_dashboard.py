import base64
import random
import streamlit as st
import authentication as auth
from streamlit_extras.stylable_container import stylable_container

IMAGE_PATH = 'dashboard_images/'

@st.cache_data
def get_base64_of_bin_file(bin_file):
     with open(bin_file, 'rb') as f:
         data = f.read()
     return base64.b64encode(data).decode()
    
def set_background(png_file):
    css_code = """
    <style>
    .stApp > header {
        height: min(10vh, 5.625vw) !important;
    }
    </style>
    """    
    st.markdown(css_code, unsafe_allow_html=True)
    
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: contain;
    background-repeat: no-repeat;
    margin-top: min(9.090909090909vh, 5.625vw);
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def settings_page():
    # Menu Image
    if st.session_state['profile_portal']:
        settings_html = """
        <div style="position: fixed; top: min(10vh, 6.25vw); left: min(1vw, 1.6vh);">
            <div style="position: relative; display: inline-block;">
                <img style="height: min(20vh, 12.5vw);" src="data:image/png;base64,{}" 
                     alt="Button Image" class="settings-portal" id=settings-portal-button">
            </div>
        </div>
        """
        image_base64 = get_base64_of_bin_file(IMAGE_PATH + 'profile_menu.png')
        st.markdown(settings_html.format(image_base64), unsafe_allow_html=True)

        # Log out Button
        with stylable_container(
        'logout_button_cont',
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: min(23vh, 14.375vw); 
        left: min(1.25vw, 2vh);
        width: min(14.5vw, 23.2vh); 
        height: min(3.8vw, 6.08vh);
        min-height: 0px;
        min-width: 0px;
        border-radius: 5%;
        }
        button:hover {
        box-shadow: 0 0 12px 5px #ffffff;
        border: none;
        border-radius: 20%;
        }
        button:focus {
        border: none;
        box-shadow: rgba(255, 255, 255, 0.5) 0px 0px 5px 0.1rem;
        border-radius: 20%;
        }""",
        ):
            def logout_user():
                st.session_state['authentication_status'] = False
                st.session_state['profile_portal'] = False
            logout_butt = st.button(" ", key = 'logout_001', on_click=logout_user)
            if logout_butt:
                st.switch_page('ui_navigator.py')
    
    # Create Clickable Button
    def set_setting_image():
        st.session_state['profile_portal'] = not st.session_state['profile_portal']
    with stylable_container(
        'settings_button_cont',
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: min(11.8vh, 7.375vw); 
        left: min(2vw, 3.2vh);
        width: min(4.4vw, 7.04vh); 
        height: min(3.8vw, 6.08vh);
        min-height: 0px;
        min-width: 0px;
        border-radius: 10%;
        }
        button:hover {
        box-shadow: 0 0 12px 5px #ffffff;
        border: none;
        border-radius: 20%;
        }
        button:focus {
        border: none;
        box-shadow: rgba(255, 255, 255, 0.5) 0px 0px 5px 0.1rem;
        border-radius: 20%;
        }""",
    ):
        b = st.button(" ", key='settings_button', on_click=set_setting_image)
 

def _get_game_thumbnail_image(game_ids: list):
    image_files = {i: f'game_data/{i}/images/thumbnail.jpg' for i in game_ids}
    return image_files

def _create_game_cover(top_margin, left_margin, image_file, game_id, category):
    button_key = str(random.randint(100000,999999))
    button_html = """
    <div style="position: fixed; top: """+ top_margin + """; left: """ + left_margin + """;">
        <div style="position: relative; display: inline-block;">
            <img style="width: min(12vw, 19.2vh); height: min(9vw, 14.4vh); border-radius: 20%;" src="data:image/png;base64,{}" alt="Button Image" class="g""" + game_id + button_key +"""-thumb" id="g""" + game_id + button_key +"""-thumb-button">
        </div>
    </div>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)

    # Generate the clickable st button
    def set_game_id():
        st.session_state['cur_game'] = game_id
    
    with stylable_container(
        f'game_{game_id}_{button_key}_butt_cont',
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: """+ top_margin + """; 
        left: """ + left_margin + """;
        width: min(12vw, 19.2vh); 
        height: min(9vw, 14.4vh);
        min-height: 0px;
        min-width: 0px;
        border-radius: 20%;
        }
        button:hover {
        box-shadow: 0 0 12px 5px #ffffff;
        border: none;
        border-radius: 20%;
        }
        button:focus {
        border: none;
        box-shadow: rgba(255, 255, 255, 0.5) 0px 0px 5px 0.1rem;
        border-radius: 20%;
        }""",
    ):
        set_key = f'game_{game_id}_{category}_butt'
        b = st.button(" ", key=set_key, on_click=set_game_id)
        if b:
            st.switch_page('pages/game_ui.py')

def display_games():
    # TODO: at some point, grab these ids from user information
    user_games = ['game1']
    recent_games = ['game1']
    rec_games = ['game2', 'game3', 'game4', 'game5']

    # left margin
    left_margin = 'min(33vw, 52.8vh)'
    gap_margin = 'min(2vw, 3.2vh)'
    butt_len = 'min(12vw, 19.2vh)'
    
    # My Games
    top_margin = 'min(22vh, 13.75vw)'
    images = _get_game_thumbnail_image(user_games)
    for g_i in range(len(user_games)):
        cur_left_margin = f'calc({left_margin} + ' + ' + '.join([f'{butt_len} + {gap_margin}' for gap in range(g_i + 1)]) + ')'
        _create_game_cover(top_margin, cur_left_margin, images[user_games[g_i]], user_games[g_i], 'mygame')
    
    # # Community Games
    top_margin = 'min(49vh, 30.625vw)'
    images = _get_game_thumbnail_image(rec_games)
    cur_left_margin = f'calc({left_margin})'
    for g_i in range(len(rec_games)):
        if g_i > 0:
            cur_gap = ' + '.join([f'{butt_len} + {gap_margin}' for gap in range(g_i)]) 
            cur_left_margin = f'calc({left_margin} + ' + cur_gap + ')'
        _create_game_cover(top_margin, cur_left_margin, images[rec_games[g_i]], rec_games[g_i], 'recgame')

    # Recently Played
    top_margin = 'min(76vh, 47.5vw)'
    images = _get_game_thumbnail_image(recent_games)
    cur_left_margin = f'calc({left_margin})'
    for g_i in range(len(recent_games)):
        if g_i > 0:
            cur_gap = ' + '.join([f'{butt_len} + {gap_margin}' for gap in range(g_i)]) 
            cur_left_margin = f'calc({left_margin} + ' + cur_gap + ')'
        _create_game_cover(top_margin, cur_left_margin, images[recent_games[g_i]], recent_games[g_i], 'recent')
    
    

def create_game_button(image_file):
    left_margin = 'min(33vw, 52.8vh)'
    top_margin = 'min(22vh, 13.75vw)'
    
    button_html = """
    <div style="position: fixed; top: """+ top_margin + """; left: """ + left_margin + """;">
        <div style="position: relative; display: inline-block;">
            <img style="width: min(12vw, 19.2vh); height: min(9vw, 14.4vh);" src="data:image/png;base64,{}" alt="Button Image" class="create-game-button-image" id="create-game-custom-button">
        </div>
    </div>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)

    # Generate the clickable st button
    # def set_screen_state(direction):
    #     if direction == 'left':
    #         st.session_state['screen_state'] = st.session_state['screen_state'] - 1
    #     elif direction == 'right':
    #         st.session_state['screen_state'] = st.session_state['screen_state'] + 1
    #     chosen_ones = random_select_char()
    #     st.session_state['chosen_char'] = chosen_ones[0]
    #     st.session_state['chosen_pos'] = chosen_ones[1]
    
    with stylable_container(
        'create_game_butt_cont',
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: """+ top_margin + """; 
        left: """ + left_margin + """;
        width: min(12vw, 19.2vh); 
        height: min(9vw, 14.4vh);
        min-height: 0px;
        min-width: 0px;
        border-radius: 20%;
        }
        button:hover {
        box-shadow: 0 0 12px 5px #ffffff;
        border: none;
        border-radius: 20%;
        }
        button:focus {
        border: none;
        box-shadow: rgba(255, 255, 255, 0.5) 0px 0px 5px 0.1rem;
        border-radius: 20%;
        }""",
    ):
        # b = st.button(" ", key=button_key, on_click=set_screen_state, args=[direction])
        b = st.button(" ", key='create_game_butt')


def main():
    if 'authentication_status' not in st.session_state:
        st.switch_page('ui_navigator.py')

    # Initialize state vars
    if 'cur_game' not in st.session_state:
        st.session_state['cur_game'] = None
    if 'profile_portal' not in st.session_state:
        st.session_state['profile_portal'] = False
    
    set_background(IMAGE_PATH + 'main_dashboard.png')
    create_game_button(IMAGE_PATH + 'create_game_button.png')
    display_games()
    settings_page()
    # st.write("Welcome, :orange[" + st.session_state['name'] + ']! :tulip:')
    # st.divider()
    # st.markdown(':rainbow[==== This is a placeholder for future **FANCY** User Dashboard ====]')
    # st.divider()
    # st.write('Games:')
    # if st.button('Game 1'):
    #     st.switch_page('pages/game_ui.py')
    # print('dashboard', st.session_state)
    
if __name__ == '__main__':
    main()
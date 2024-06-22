import json, time
import base64
import random
import asyncio
import numpy as np
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from functions import character_resize, background_resize

from model_adaptor import npc_chat, compare_task_answers

# Set Game ID
GAME_ID = 'game1' # This should eventually be a variable passed in when user clicks on a particular game
if 'game_id' not in st.session_state:
    st.session_state['game_id'] = GAME_ID

# Load Game Images
IMAGE_CONFIG = json.load(open('game_data/' + st.session_state['game_id'] + '/image_config.json'))
CHAR_NAMES = list(IMAGE_CONFIG['characters'].keys())
CHAR_IMAGES = ['game_data/' + st.session_state['game_id'] + '/images/' + i for i in IMAGE_CONFIG['characters'].values()]
BACK_IMAGES = ['game_data/' + st.session_state['game_id'] + '/images/' + i for i in IMAGE_CONFIG['backgrounds']]


def load_game_data():
    f = open('game_data/' + st.session_state['game_id'] + '/admin.json')
    return json.load(f)  


def load_npc_bot():
    chat_hist = st.session_state['chat_history_log']
    npc_bots = {}
    for npc in CHAR_NAMES:
        info_db_path = 'game_data/' + st.session_state['game_id'] + '/' + npc
        info_prompt_path = 'game_data/' + st.session_state['game_id'] + '/' + npc + '_prompt.txt'
        npc_bots[npc] = npc_chat(npc, info_db_path, info_prompt_path, chat_hist[npc])
    return npc_bots

def append_unlocked_events(story: str, characters: list):
    for ch in characters:
        st.session_state['npc_bots'][ch].info_db.add_texts([story])

@st.cache_data
def get_base64_of_bin_file(bin_file):
     with open(bin_file, 'rb') as f:
         data = f.read()
     return base64.b64encode(data).decode()

#
def set_background(png_file):
     bin_str = get_base64_of_bin_file(png_file)
     page_bg_img = '''
     <style>
     .stApp {
     background-image: url("data:image/png;base64,%s");
     background-size: contain;
     background-repeat: no-repeat;
     }
     </style>
     ''' % bin_str

     st.markdown(page_bg_img, unsafe_allow_html=True)
     return


def all_image_resize():
    # global CHAR_IMAGES
    global BACK_IMAGES
    # for i in range(len(CHAR_IMAGES)):
    #     new_file_name = character_resize(CHAR_IMAGES[i])
    #     CHAR_IMAGES[i] = new_file_name
    for i in range(len(BACK_IMAGES)):
        new_file_name = background_resize(BACK_IMAGES[i])
        BACK_IMAGES[i] = new_file_name


def name_tag(char_name, top_margin, left_margin):
    st.markdown(
        """
        <style>
        .name_tag {
            margin: 0px;
            font-size: min(2.25vh, 1.2656vw) !important;
            font-weight: 600 !important;
            font-family: cursive;
            color: #8F5218 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="position: fixed; top: """ + top_margin + """; left: """ + left_margin + """; \
                border-radius: 0.5rem; border: min(0.65vh, 0.3656vw) double #894600; transform: translateX(-50%);
                background: radial-gradient(farthest-corner at 0% 100%, #FFE6B7, #B87B38); 
                padding-left: min(1vh, 0.5625vw); padding-right: min(1vh, 0.5625vw); padding-top: min(0.5vh, 0.28125vw); padding-bottom: min(0.5vh, 0.28125vw);">
            <div style="position: relative; display: inline-block;">
            <p class="name_tag">
                """ + char_name + """
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def place_character(char_name, position):
    file_name = CHAR_IMAGES[CHAR_NAMES.index(char_name)]
    
    if position == 'left':
        margin = 'min(30vw, 53.333vh)'
    elif position == 'middle':
        margin = 'min(50vw, 88.889vh)'
    elif position == 'right':
        margin = 'min(70vw, 124.444vh)'

    # Place char image
    char_html = """
    <div style="position: fixed; top: min(30vh, 16.875vw); left: """ + margin + """; transform: translateX(-50%);">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="charImage" class="char-image">
        </div>
    </div>
    """

    css_code = """
    <style>
    .char-image {
        height: min(70vh, 39.37vw);
        transition: box-shadow 0.3s ease-in-out;
    }
    </style>
    """    
    img_base64 = get_base64_of_bin_file(file_name)
    st.markdown(char_html.format(img_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)



    # Place Name Tag
    name_tag(char_name, 'min(25vh, 14.0625vw)', margin)
    
    # Generate the clickable st button
    ## Button Image
    button_key = random.randint(100000,999999)
    image_button = "game_images/chat_button_3.gif"
    direction = 'left'
    # Define the HTML code to create a button with transparent background using a local image and glow effect on hover
    button_html = """
    <div style="position: fixed; top: min(70vh, 39.375vw); left: """ + margin + """; transform: translateX(-50%);">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Button Image" class=\"""" + direction + """chat-button-image" id=\"""" + direction + """chat-custom-button">
        </div>
    </div>
    """
    css_code = """
    <style>
    .""" + direction + """chat-button-image {
        width: min(10vh, 5.625vw);
        height: min(10vh, 5.625vw);
        transition: box-shadow 0.3s ease-in-out;
    }
    </style>
    """
    image_base64 = get_base64_of_bin_file(image_button)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    ## Button click
    def open_chat_portal(file_name):
        st.session_state['chat_char'] = CHAR_IMAGES.index(file_name)
        st.session_state['chat_portal'] = True
        
    with stylable_container(
        'butt' + str(button_key),
        css_styles="""
        button[kind="primary"]{
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: min(70vh, 39.375vw);
        left: """ + margin + """;
        transform: translateX(-50%);
        height: min(10vh, 5.625vw);
        width: min(10vh, 5.625vw);
        min-height: 0px;
        min-width: 0px;
        border: none;
        }
        button[kind="primary"]:hover {
        animation: none;
        box-shadow: 0 0 12px 6px #ffffff;
        border-radius: 50%;
        border: none;
        }
        button[kind="primary"]:focus {
        outline: none;
        border-radius: 50%;
        border: none;
        box-shadow: rgba(255, 255, 255, 0.75) 0px 0px 5px 0.05rem,
                    inset rgba(255, 255, 255, 0.75) 0px 0px 10px 0.05rem;
        }
        button[kind="primary"]:not(hover) {
        box-shadow: inset 0 0 12px 2px #ffffff,
                    0 0 12px 5px #ffffff;
        border-radius: 50%;
        border: none;
        animation: glow 3s linear infinite;
        }
        @keyframes glow {
          0% {
            box-shadow: rgba(255, 255, 255, 0.2) 0px 0px 5px 0.1rem,
                        inset 0 0 15px 1px rgba(255, 255, 255, 0.7);
          }
          30% {
            box-shadow: rgba(255, 255, 255, 0.7) 0px 0px 10px 0.2rem,
                        inset 0 0 10px 0.5px rgba(255, 255, 255, 0.5);
          }
          75% {
            box-shadow: rgba(255, 255, 255, 1) 0px 0px 20px 0.3rem;
          }
          100% {
            box-shadow: rgba(255, 255, 255, 0) 0px 0px 10px 0.2rem;
          }""",
    ):
        b = st.button(" ", key=button_key, type='primary', on_click=open_chat_portal, args=[file_name])

def random_select_char():
    # choose_n = np.random.choice([1, 2, 3], size=1, p=[0.85, 0.14, 0.01])[0]
    choose_n = 1
    choose_char = random.sample(CHAR_NAMES, choose_n)
    choose_pos = random.sample(['left', 'middle', 'right'], choose_n)
    return choose_char, choose_pos

def navigation_buttons(direction):
    if direction == 'left':
        image_file = "game_images/left_button.png"
        margin = 'min(1vw, 1.778vh)'
    elif direction == 'right':
        image_file = "game_images/right_button.png"
        margin = 'calc(min(99vw, 176vh) - min(10vh, 5.625vw))'
    
    # Define the HTML code to create a button with transparent background using a local image and glow effect on hover
    button_html = """
    <div style="position: fixed; top: min(50vh, 28.125vw); left: """ + margin + """;">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Button Image" class=\"""" + direction + """-button-image" id=\"""" + direction + """-custom-button">
        </div>
    </div>
    """

    # Define the CSS code for the hover effect
    css_code = """
    <style>
    .""" + direction + """-button-image {
        width: min(10vh, 5.625vw);
        height: min(10vh, 5.625vw);
        transition: box-shadow 0.3s ease-in-out;
    }
    </style>
    """
    # Read the image file and convert it to base64
    image_base64 = get_base64_of_bin_file(image_file)

    # Display the HTML code with the button and CSS code
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    # Generate the clickable st button
    def set_screen_state(direction):
        if direction == 'left':
            st.session_state['screen_state'] = st.session_state['screen_state'] - 1
        elif direction == 'right':
            st.session_state['screen_state'] = st.session_state['screen_state'] + 1
        chosen_ones = random_select_char()
        st.session_state['chosen_char'] = chosen_ones[0]
        st.session_state['chosen_pos'] = chosen_ones[1]
    
    button_key = random.randint(1000,9999)
    with stylable_container(
        'butt' + str(button_key),
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: min(50vh, 28.125vw);
        left: """ + margin + """;
        height: min(10vh, 5.625vw);
        width: min(10vh, 5.625vw);
        min-height: 0px;
        min-width: 0px;
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
        b = st.button(" ", key=button_key, on_click=set_screen_state, args=[direction])



def function_buttons(button_name):
    if button_name == 'settings':
        image_file = "game_images/setting_button.png"
        left_margin = 'min(92vw, 163.5556vh)'
    elif button_name == 'chat_history':
        image_file = "game_images/chat_history_button.png"
        left_margin = 'calc(min(84vw, 149.3333vh))'
    elif button_name == 'task':
        image_file = "game_images/task_button.png"
        left_margin = 'calc(min(76vw, 135.1111vh))'
    

    top_margin = 'min(8vh, 5.0625vw)'
    button_html = """
    <div style="position: fixed; top: """ + top_margin + """; left: """ + left_margin + """;">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Button Image" class="setting-button-image" id="setting-custom-button">
        </div>
    </div>
    """
    css_code = """
    <style>
    .setting-button-image {
        width: min(10vh, 5.625vw);
        height: min(10vh, 5.625vw);
    }
    </style>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    # Generate the clickable st button
    def open_portal(button_name):
        if button_name == 'settings':
            st.session_state['settings_portal'] = True
        elif button_name == 'chat_history':
            st.session_state['chat_history_portal'] = True
        elif button_name == 'task':
            st.session_state['task_portal'] = True

    button_key = random.randint(10000,99999)
    with stylable_container(
        'butt' + str(button_key),
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: """ + top_margin + """;
        left: """ + left_margin + """;
        height: min(10vh, 5.625vw);
        width: min(10vh, 5.625vw);
        min-height: 0px;
        min-width: 0px;
        }
        """,
    ):
        b = st.button(" ", key=button_key, on_click=open_portal, args=[button_name])



def timer(test, hours = 0, minutes = 30):
    # Clock icon
    image_file = "game_images/timer_icon.png"
    # left_margin = 'min(1vw, 1111111111.7778vh)'
    left_margin = 'min(2vw, 3.555555556vh)'
    top_margin = 'min(10vh, 5.625vw)'
    button_html = """
    <div style="position: fixed; top: """ + top_margin + """; left: """ + left_margin + """;">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Timer Icon" class="timer-icon" id="timer-icon">
        </div>
    </div>
    """
    css_code = """
    <style>
    .timer-icon {
        width: min(7vh, 3.9375vw);
        height: min(7vh, 3.9375vw);
        filter: drop-shadow(0 0 3px #ffffff) drop-shadow(0 0 3px #ffffff) 
                drop-shadow(0 0 3px #ffffff) drop-shadow(0 0 3px #ffffff); 
    }
    </style>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)
    
    # Timer
    top_margin = 'min(11vh, 6.1875vw)'
    # left_margin = 'min(5.5vw, 9999999.7778vh)'
    left_margin = 'min(7vw, 12.44444444vh)'
    if st.session_state.time_left == 0:
        st.session_state.time_left = hours * 60 * 60 + minutes * 60
    st.markdown(
        """
        <style>
        .time {
            font-size: min(3vh, 1.6875vw) !important;
            font-weight: 800 !important;
            color: #F1B107 !important;
            text-shadow: 0 0 15px #ffffff, 0 0 15px #ffffff, 
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 15px #ffffff, 0 0 15px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    async def watch():  
        test.empty()
        while st.session_state.time_left >= 0:
            test.empty()
            hours = int(st.session_state.time_left / 60 / 60)
            minutes = int((st.session_state.time_left - (hours * 60 * 60)) / 60)
            seconds = st.session_state.time_left % 60
            timer_str = str(hours) + ' Hours ' + str(minutes) + ' Minutes ' + str(seconds) + ' Seconds Left'
            test.markdown(
                """
                <div style="position: fixed; top: """ + top_margin + """; left: """ + left_margin + """;">
                    <div style="position: relative; display: inline-block;">
                    <p class="time">
                        """ + timer_str + """
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.session_state.time_left -= 1
            r = await asyncio.sleep(1)
            test.empty()
    asyncio.run(watch())
    if st.session_state['game_stages'] == 1:
        st.session_state['task_portal'] = True
        darken_background()
        st.session_state['game_stages'] = 2
        st.rerun()
    timer_str = '0 Hours 0 Minutes 0 Seconds Left'
    st.markdown(
                """
                <div style="position: fixed; top: """ + top_margin + """; left: """ + left_margin + """;">
                    <div style="position: relative; display: inline-block;">
                    <p class="time">
                        """ + timer_str + """
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def darken_background():
    image_file = 'game_images/dark_mask.png'
    button_html = """
    <div style="position: fixed; top: 0px; left: 0px;">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Darken" class="darken" id="darken">
        </div>
    </div>
    """
    css_code = """
    <style>
    .darken {
        width: min(100vw, 177.78vh);
        height: min(100vh, 56.25vw);
    }
    </style>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)


def close_button(top_margin, left_margin):
    top_margin = 'min(' + str(top_margin) + 'vh, ' + str(round(top_margin*9/16, 4)) + 'vw)'
    left_margin = 'min(' + str(left_margin) + 'vw, ' + str(round(left_margin*16/9, 4)) + 'vh)'
    
    image_file = 'game_images/close_button.png'
    button_html = """
    <div style="position: fixed; top: """ + top_margin +"""; left: """ + left_margin + """;">
        <div style="position: relative; display: inline-block;">
            <img src="data:image/png;base64,{}" alt="Close Button" class="close-butt" id="close-butt">
        </div>
    </div>
    """
    css_code = """
    <style>
    .close-butt {
        height: min(5vw, 8.8889vh);
        width: min(5vw, 8.8889vh);
    }
    </style>
    """
    image_base64 = get_base64_of_bin_file(image_file)
    st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    # Generate the clickable st button
    def close_portal_state():
        if st.session_state['game_stages'] == 0:
            st.session_state['game_stages'] = 1 # show clues tab first in task portal
        portal_states = ['task_portal', 'settings_portal', 'chat_history_portal', 'chat_portal']
        for ps in portal_states:
            st.session_state[ps] = False
        st.session_state['cur_task'] = -1
        
    button_key = random.randint(100000,999999)
    with stylable_container(
        'butt' + str(button_key),
        css_styles="""
        button {
        background-color: rgb(204, 49, 49, 0);
        position: fixed;
        top: """ + top_margin + """;
        left: """ + left_margin + """;
        height: min(5vw, 8.8889vh);
        width: min(5vw, 8.8889vh);
        min-height: 0px;
        min-width: 0px;
        }
        """,
    ):
        b = st.button(" ", key=button_key, on_click = close_portal_state)


def settings_page():
    darken_background()
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: min(0.65vh, 0.3656vw) solid #E8A33B;
                border-radius: 0.5rem;
                background: #E8E8E8;
                position: fixed;
                top: min(32vh, 18vw);
                left: min(22.5vw, 40vh);
                height: min(50vh, 28.125vw);
                width: min(55vw, 97.7778vh);
            }
            """,
    ):
        ### Header ###
        image_file = 'game_images/setting_header.png'
        button_html = """
        <div style="position: fixed; top: min(36vh, 20.25vw); left: min(31vw, 55.1111vh);">
            <div style="position: relative; display: inline-block;">
                <img src="data:image/png;base64,{}" alt="Setting Header" class="setting-header" id="setting-header">
            </div>
        </div>
        """
        css_code = """
        <style>
        .setting-header {
            width: min(38vw, 67.5556vh);
        }
        </style>
        """
        image_base64 = get_base64_of_bin_file(image_file)
        st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
        st.markdown(css_code, unsafe_allow_html=True)

        
        ### button 1: Exit & Save ###
        image_file = 'game_images/setting_exit_save.png'
        button_html = """
        <div style="position: fixed; top: min(50vh, 28.125vw); left: min(32vw, 56.88889vh);">
            <div style="position: relative; display: inline-block;">
                <img src="data:image/png;base64,{}" alt="Exit Save" class="exit-save" id="exit-save">
            </div>
        </div>
        """
        css_code = """
        <style>
        .exit-save {
            width: min(36vw, 64vh);
            height: min(4vw, 7.1111vh);
        }
        </style>
        """
        image_base64 = get_base64_of_bin_file(image_file)
        st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
        st.markdown(css_code, unsafe_allow_html=True)

        ### button 2: Exit without save ###
        image_file = 'game_images/setting_exit_no_save.png'
        button_html = """
        <div style="position: fixed; top: min(60vh, 33.75vw); left: min(32vw, 56.88889vh);">
            <div style="position: relative; display: inline-block;">
                <img src="data:image/png;base64,{}" alt="Exit No Save" class="exit-no-save" id="exit-no-save">
            </div>
        </div>
        """
        css_code = """
        <style>
        .exit-no-save {
            width: min(36vw, 64vh);
            height: min(4vw, 7.1111vh);
        }
        </style>
        """
        image_base64 = get_base64_of_bin_file(image_file)
        st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
        st.markdown(css_code, unsafe_allow_html=True)

        # Generate the clickable st button              
        button_key = random.randint(100000,999999)
        with stylable_container(
            'butt' + str(button_key),
            css_styles="""
            button {
            background-color: rgb(204, 49, 49, 0);
            position: fixed;
            top: min(60vh, 33.75vw); 
            left: min(32vw, 56.88889vh);
            height: min(4vw, 7.1111vh);
            width: min(36vw, 64vh);
            min-height: 0px;
            min-width: 0px;
            color: rgba(0, 0, 0, 0);
            border-radius: 0.5rem;
            border: none;
            }
            """,
        ):
            if st.button("exit_no_save_butt"):
                st.switch_page('pages/user_dashboard.py')    
        
        if st.session_state['settings_portal']:
            close_button(28, 74.5)


def task_page():
    darken_background()
    with stylable_container(
        key="task_container",
        css_styles="""
            {
                border: min(0.65vh, 0.3656vw) solid #B87A36;
                border-radius: 0.5rem;
                background: #E8E8E8;
                position: fixed;
                top: min(32vh, 18vw);
                left: min(22.5vw, 40vh);
                height: min(59vh, 33.1875vw);
                width: min(55vw, 97.7778vh);
            }
            """,
    ):
        
        # Create tab buttons        
        with stylable_container(
        key="task_tabs",
        css_styles="""
            {
                display: inline;
                border: 0px;
                border-radius: 0.5rem;
                background: rbga(0, 0, 0, 0);
                position: fixed;
                top: calc(min(32vh, 18vw) - min(6vh, 3.375vw));
                left: calc(min(22.5vw, 40vh) + min(0.3vw, 0.5333vh));
                height: min(10vh, 5.625vw);
                width: min(55vw, 97.7778vh);
            }
            """):
            st.markdown("""
            <style>
            
                .stTabs [data-baseweb="tab-list"] {
                	gap: 0px;
                    border-radius: 0.5rem 0.5rem 0px 0px;
                    # padding-top: 2px;
                }
            
                .stTabs [data-baseweb="tab"] {
                    width: min(13vw, 23.1111vh);
                	height: min(6vh, 3.375vw);
                	background-color: #B87A36;
                    color: #E9C38B;
                	border-radius: 0.5rem 0.5rem 0px 0px;
                }
                .stTabs [data-testid="stMarkdownContainer"]{
                    font-family: cursive;
                }
                .stTabs [data-testid="stMarkdownContainer"] > p {
                    font-size: min(2.2vh, 1.2375vw);
                }
                .stTabs [aria-selected="true"] {
                    background-color: #E9C38B;
                    color: #B87A36;
                }
                .stTabs [data-baseweb="tab-highlight"] {
                    background-color: #B87A36;
                }
                .stTabs [data-baseweb="tab-border"] {
                    background-color: rgba(0, 0, 0, 0)
                }
                
            
            </style>""", unsafe_allow_html=True)

            cur_prog_stat = (st.session_state['task_progress'] / len(sum(st.session_state['task_status'].values(), [])))
            if st.session_state['game_stages'] == 0:
                tab_names = ['Overview', 'Clues', 'Final Answer']
            elif st.session_state['game_stages'] == 1:
                if cur_prog_stat <= 0.3:
                    tab_names = ['Clues', 'Overview', 'Final Answer']
                else:
                    tab_names = ['Clues', 'Final Answer', 'Overview']
            else:
                tab_names = ['Final Answer', 'Clues', 'Overview']

            tabs = st.tabs(tab_names)
        
        # Introduction Letter
        with tabs[tab_names.index('Overview')]:
            with stylable_container(key="overview_tab_container", # set background color darker to show chat
                css_styles="""
                    {
                        border: min(0.65vh, 0.3656vw) solid #B87A36;
                        border-radius: 0.5rem;
                        background: #DDD9D5;
                        position: fixed;
                        top: min(32vh, 18vw);
                        left: min(22.5vw, 40vh);
                        height: min(59vh, 33.1875vw);
                        width: min(55vw, 97.7778vh);
                    }
                    """,
            ):
                # chat area container: styling
                with stylable_container(key = 'overview_tab', css_styles="""
                    {
                        position: fixed;
                        top: min(35.5vh, 19.96875vw);
                        left: min(24.5vw, 43.5556vh);
                        height: min(52vh, 29.25vw);
                        width: min(51vw, 90.6667vh);
                        display: flex;
                    }
                    """):
                    # chat area double container: scrolling
                    with st.container(height=1000, border=False):
                        police_msgs = ['Hi Detective :blue[[Player Name]]',
                                      'Thanks for taking on the investigation of this **potential murder case**.  \nYour help is very much needed in identifying the suspected **victim** and **murderer**.',
                                      f'Below is the location of your search:  \n📍**{st.session_state['game_data']['story_setting']['event_name']}**  \n{st.session_state['game_data']['story_setting']['event_description']}',
                                      'The individuals you will need to investigate are:  \n-' + '  \n-'.join(CHAR_NAMES),
                                      'Remember, you only have **:red[12 hours]** before it is too late.',
                                      'Best of Luck!']
                        if st.session_state['game_stages'] == 0:
                            time.sleep(2)
                            for message in police_msgs:
                                with st.chat_message('user', avatar='👮'):
                                    # st.markdown(message)
                                    message_placeholder = st.empty()
                                    full_response = ""
                                    for chunk in message.split(' '):
                                        full_response += chunk + " "
                                        time.sleep(0.1)
                                        # Add a blinking cursor to simulate typing
                                        message_placeholder.markdown(full_response + "�?")
                                    message_placeholder.markdown(full_response)
                                time.sleep(1)
                        else:
                            for message in police_msgs:
                                with st.chat_message('user', avatar='👮'):
                                    st.markdown(message)
#             with stylable_container(key = 'overview_tab', css_styles="""
#                     {
#                         position: fixed;
#                         top: min(35.5vh, 19.96875vw);
#                         left: min(24.5vw, 43.5556vh);
#                         height: min(52vh, 29.25vw);
#                         width: min(51vw, 90.6667vh);
#                         overflow-y: auto;
#                         overflow-x: hidden;
#                         display: flex;
#                     }
#                     """):
#                 cols = st.columns((0.001, 15, 0.1))
#                 with cols[1]:
#                     # original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">Original imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal imageOriginal image</p>'
#                     # st.markdown(original_title, unsafe_allow_html=True)
#                     overview = """**Dear Detective :blue[[Player Name]]:**\n\n
# &nbsp; &nbsp; &nbsp; We have been informed by an anonymous tipster of :orange[an imminent threat of murder] within close proximity to your location. Your assistance in this matter is **urgently** required! Please read the below :orange[case details] **CAREFULLY**:\n\n
#                 """
#                     st.markdown(overview)
#                     st.markdown("""**--Case Overview--**  
#                     """ + '*' + st.session_state['game_data']['overview'] + """*  
#                     **--END--**""")
    
#                     instructions = """  
#     Now, with that information, your :orange[one and only goal] is to prevent the impending tragedy from happening by **identifying** both the intended **victim** and the **perpetrator** among three individuals. A few pieces of advice before you go:  
#     - Some :orange[mysterious clues] were discreetly left by an anonymous informant  
#     - :orange[Engage in dialogue] with the identified subjects with tact and discernment. They should have the information to help you :orange[solve the clues]  
#     - Once solved, clues should :orange[reveal critical information] about the case. Use it to gain trust with the subjects and :orange[gather their identities & motives.]\n\n
#     **Remember**, you only have :warning:**:red[12 hours]**:exclamation: before it is too late. The timer has already started! Best of luck in your endeavor.\n\n
#     **Yours truly,**  
#     **Officer X**"""
#                     st.markdown(instructions)
        
        # Tasks
        with tabs[tab_names.index('Clues')]:            
            with stylable_container(key = 'clues_tab', css_styles="""
                    {
                        position: fixed;
                        top: min(35.5vh, 19.96875vw);
                        left: min(24.5vw, 43.5556vh);
                        height: min(52vh, 29.25vw);
                        width: min(51vw, 90.6667vh);
                        overflow-y: auto;
                        overflow-x: hidden;
                        display: flex;
                    }
                    """):
                for series, clues in st.session_state['game_data']['clues'].items():
                    cur_status = st.session_state['task_status'][series]
                    completion_stat = """&nbsp; &nbsp; ( """ + str(int(len([i for i in cur_status if i]) /len(cur_status) * 100)) + '% )'
                    with st.expander("Clues Set *:orange[" + series.upper() + ']*' + completion_stat, expanded=(series == st.session_state['cur_task'])):
                        active_task = cur_status.index(False) + 1 if False in cur_status else -1      
                        for c_num, c_val in clues.items():
                            task_key = series+c_num
                            task_stat = cur_status[int(c_num) - 1]
                            # If task completed
                            if task_stat:
                                expander_title = "Task *:blue[" + c_num + ']* &nbsp; :white_check_mark:'
                                checked = st.checkbox(expander_title, key='check_' + task_key)
                                placeholder = st.empty()
                                if checked:
                                    with placeholder.form('tform_' + task_key):
                                        st.write(c_val['question'])
                                        st.text_input('Answer:', value=c_val['answer'], disabled=True)
                                        submitted = st.form_submit_button("Submit", disabled=True)
                                placeholder = st.empty()
                                placeholder.write("**Decoded Clue:** :orange[" + c_val['info'] + "]")
                            # If active task
                            elif int(c_num) == active_task:
                                expander_title = "Task *:blue[" + c_num + ']*'
                                checked = st.checkbox(expander_title, key='check_' + task_key, value = True)
                                placeholder = st.empty()
                                if checked:
                                    with placeholder.form('tform_' + task_key):
                                        st.write(c_val['question'])
                                        answer = st.text_input('Answer:')
                                        submitted = st.form_submit_button("Submit")
                                        if submitted:
                                            st.session_state['cur_task'] = series
                                            if compare_task_answers(c_val['answer'], answer) == 'yes':
                                                st.session_state['task_status'][series][int(c_num) -1] = True
                                                append_unlocked_events(c_val['story'], c_val['char'])
                                                st.session_state['task_progress'] += 1
                                                st.rerun()
                                            else:
                                                st.error('Answer is incorrect. Try Again!')
                            # If task locked
                            else:
                                expander_title = "Task *:blue[" + c_num + ']* &nbsp; :lock:'
                                checked = st.checkbox(expander_title, key='check_' + task_key, disabled=True)
                                placeholder = st.empty()
        # Final Answer Tab
        with tabs[tab_names.index('Final Answer')]:
            ### Header ###
            image_file = 'game_images/task_final_answer.png'
            button_html = """
            <div style="position: fixed; top: min(36vh, 20.25vw); left: min(29vw, 51.5556vh);">
                <div style="position: relative; display: inline-block;">
                    <img src="data:image/png;base64,{}" alt="Setting Header" class="setting-header" id="setting-header">
                </div>
            </div>
            """
            css_code = """
            <style>
            .setting-header {
                width: min(42vw, 74.6667vh);
            }
            </style>
            """
            image_base64 = get_base64_of_bin_file(image_file)
            st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
            st.markdown(css_code, unsafe_allow_html=True)

            with stylable_container(
                key="final_answer_form_cont",
                css_styles="""
                    {
                        border: min(0.65vh, 0.3656vw) solid rgba(0, 0, 0, 0);
                        border-radius: 0.5rem;
                        background: rbga(0, 0, 0, 0);
                        position: fixed;
                        top: min(39vh, 21.9375vw);
                        left: min(22.5vw, 40vh);
                        height: min(52vh, 29.25vw);
                        width: min(55vw, 97.7778vh);
                        overflow-y: auto;
                        overflow-x: hidden;
                        display: flex;
                    }
                    """):
                cur_prog_stat = (st.session_state['task_progress'] / len(sum(st.session_state['task_status'].values(), [])))
                if (cur_prog_stat > 0.3) or (st.session_state['game_stages'] == 2):
                    disable = False
                    place_holder = 'Choose a Name'
                    title_add = ''
                else:
                    disable = True
                    place_holder = 'Solve >30% of all clues OR wait until time is up to UNLOCK!'
                    title_add = ':lock: &nbsp; '
                cols = st.columns((0.6, 15, 0.6))
                with cols[1]:
                    st.markdown(" &nbsp; \n\n &nbsp; ")
                    st.write(" ")
                    with st.form('final_answer_form'):
                        victim = st.selectbox(title_add + 'Victim:', options = CHAR_NAMES, index = None, placeholder = place_holder, disabled = disable)
                        murderer = st.selectbox(title_add + 'Suspected Murderer:', options = CHAR_NAMES, index = None, placeholder = place_holder, disabled = disable)
                        submitted = st.form_submit_button("Submit", disabled=disable)
                        if submitted:
                            if (victim == st.session_state['game_data']['final_answer']['victim']) and (murderer == st.session_state['game_data']['final_answer']['killer']):
                                st.session_state['game_success'] = 1
                            else:
                                st.session_state['game_success'] = 0
        if st.session_state['task_portal']:
            close_button(28, 74.5)


def task_progress_bar():
    cur_prog_stat = str(int(round((st.session_state['task_progress'] / len(sum(st.session_state['task_status'].values(), []))) * 100, 0))) + '%'

    with stylable_container(key = 'prog_bar_background', css_styles="""
        {
            position: fixed;
            top: min(11.5vh, 6.46875vw);
            left: min(37.5vw, 66.66666667vh);
            height: min(4vh, 2.25vw);
            width: min(35vw, 62.22222222vh);
            display: flex;
            background: linear-gradient(to right, #2394b9, lightblue """ + cur_prog_stat + """, #F2F2F2 """ + cur_prog_stat + """);
            border-radius: 5rem;
            color: rgba(0, 0, 0, 0);
            box-shadow: inset 0px -10px 10px -5px #2f2f2f,
                        0 0 10px 1px #bfbfbf;
        }
        """):
        placeholder = st.empty()
        st.markdown(
        """
        <style>
        .prog_text {
            font-size: min(2vh, 1.125vw) !important;
            font-weight: 600 !important;
            color: #B87A36 !important;
            text-shadow: 0 0 15px #ffffff, 0 0 15px #ffffff, 
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True)
        placeholder.markdown(
            """
            <div style="position: fixed; padding-top: min(2vh, 1.125vw); left: min(54vw, 96vh);">
                <div style="position: relative; display: inline-block;">
                <p class="prog_text">
                    """ + cur_prog_stat + """
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)


def char_trust_bar(trust_level):
    trust_level_str = str(trust_level) + '%'

    top_margin = 'min(91vh, 51.1875vw)'
    left_margin = 'min(19vw, 33.7778vh)'

    with stylable_container(key = 'trust_bar_background', css_styles="""
        {
            position: fixed;
            top: """ + top_margin + """;
            left: """ + left_margin + """;
            transform: translateX(-50%);
            height: min(4vh, 2.25vw);
            width: min(20vw, 35.5556vh);
            display: flex;
            background: linear-gradient(to right, #2394b9, #e71847 """ + trust_level_str + """, #F2F2F2 """ + trust_level_str + """);
            border-radius: 5rem;
            color: rgba(0, 0, 0, 0);
            box-shadow: inset 0px -10px 10px -5px #2f2f2f,
                        0 0 10px 1px #bfbfbf;
        }
        """):
        st.empty()
    
    with stylable_container(key = 'trust_bar_foreground', css_styles="""
        {
            position: fixed;
            top: """ + top_margin + """;
            left: """ + left_margin + """;
            transform: translateX(-50%);
            height: min(4vh, 2.25vw);
            width: min(20vw, 35.5556vh);
            display: flex;
            background: linear-gradient(to right, transparent, transparent """ + trust_level_str + """, #F2F2F2 """ + trust_level_str + """);
            border-radius: 5rem;
            color: rgba(0, 0, 0, 0);
            box-shadow: inset 0px -10px 10px -5px #2f2f2f;
        }
        """):
        placeholder = st.empty() # ff2474
        st.markdown(
        """
        <style>
        .trust_text {
            font-size: min(2vh, 1.125vw) !important;
            font-weight: 600 !important;
            color: #B87A36 !important;
            text-shadow: 0 0 15px #ffffff, 0 0 15px #ffffff, 
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff,
                         0 0 5px #ffffff, 0 0 5px #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True)
        placeholder.markdown(
            """
            <div style="position: fixed; left: """ + left_margin + """; width: min(20vw, 35.5556vh); transform: translateX(-65%); padding-top: min(2vh, 1.125vw);">
                <div style="position: relative; display: inline-block;">
                <p class="trust_text">
                    Trust Level: """ + trust_level_str + """
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def chat_history_page():
    darken_background()
    with stylable_container(
        key="chat_history_cont",
        css_styles="""
            {
                border: min(0.65vh, 0.3656vw) solid #B87A36;
                border-radius: 0.5rem;
                background: #DDD9D5;
                position: fixed;
                top: min(32vh, 18vw);
                left: min(22.5vw, 40vh);
                height: min(59vh, 33.1875vw);
                width: min(55vw, 97.7778vh);
                box-shadow: inset 0px 10px 5px -5px #a8a8a8;
            }
            """,
    ):
        with stylable_container(
        key="chat_history_tab",
        css_styles="""
            {
                display: inline;
                border: 0px;
                border-radius: 0.5rem;
                background: rbga(0, 0, 0, 0);
                position: fixed;
                top: calc(min(32vh, 18vw) - min(6vh, 3.375vw));
                left: calc(min(22.5vw, 40vh) + min(0.3vw, 0.5333vh));
                height: min(10vh, 5.625vw);
                width: min(55vw, 97.7778vh);
            }
            """):
            st.markdown("""
            <style>
            
                .stTabs [data-baseweb="tab-list"] {
                	gap: 0px;
                    border-radius: 0.5rem 0.5rem 0px 0px;
                    # padding-top: 2px;
                }
            
                .stTabs [data-baseweb="tab"] {
                    width: min(13vw, 23.1111vh);
                	height: min(6vh, 3.375vw);
                	background-color: #B87A36;
                    color: #E9C38B;
                	border-radius: 0.5rem 0.5rem 0px 0px;
                }
                .stTabs [data-testid="stMarkdownContainer"]{
                    font-family: cursive;
                }
                .stTabs [data-testid="stMarkdownContainer"] > p {
                    font-size: min(2.2vh, 1.2375vw);
                }
                .stTabs [aria-selected="true"] {
                    background-color: #E9C38B;
                    color: #B87A36;
                }
                .stTabs [data-baseweb="tab-highlight"] {
                    background-color: #B87A36;
                }
                .stTabs [data-baseweb="tab-border"] {
                    background-color: rgba(0, 0, 0, 0)
                }
                
            
            </style>""", unsafe_allow_html=True)
            tabs = st.tabs(CHAR_NAMES)
        for t in range(len(tabs)):
            with tabs[t]:
                with stylable_container(key = 'chat_hist_display_' + str(t), css_styles="""
                    {
                        position: fixed;
                        top: min(35.5vh, 19.96875vw);
                        left: min(24.5vw, 43.5556vh);
                        height: min(52vh, 29.25vw);
                        width: min(51vw, 90.6667vh);
                        overflow-y: auto;
                        overflow-x: hidden;
                        display: flex;
                    }
                    """):
                    for message in reversed(st.session_state['chat_history_log'][CHAR_NAMES[t]]):
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
        
        if st.session_state['chat_history_portal']:
            close_button(28, 74.5)


def display_chat(char_chat_name):
    with stylable_container(
            key="chat_hist_cont",
            css_styles="""
                {
                    # border: min(0.65vh, 0.3656vw) solid #E8A33B;
                    # border-radius: 0.5rem;
                    background: #DDD9D5;
                    position: fixed;
                    top: calc(min(15vh, 8.4375vw) + min(0.65vh, 0.3656vw));
                    left: calc(min(38vw, 67.5556vh) + min(0.65vh, 0.3656vw));
                    height: min(59vh, 33.1875vw);
                    width: calc(min(55vw, 97.7778vh) - min(0.65vh, 0.3656vw) - min(0.65vh, 0.3656vw));
                    box-shadow: inset 0px -10px 5px -5px #a8a8a8;
                }
                """):
        
        with stylable_container(
            key = 'chat_display',
            css_styles="""
            {
                position: fixed;
                top: min(18.5vh, 10.40625vw);
                left: min(40vw, 71.1111vh);
                height: min(52vh, 29.25vw);
                width: min(51vw, 90.6667vh);
                overflow-y: auto;
                overflow-x: hidden;
                display: flex;
                overflow-anchor: none !important; 
                flex-direction: column-reverse;
            }
            """):
            for message in st.session_state['chat_history_log'][char_chat_name]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def chat_input(char_chat_name):
    with stylable_container(
        key="chat_input",
        css_styles="""
        {
            position: fixed;
            top: min(75vh, 42.1875vw);
            left: min(40vw, 71.1111vh);
        }
        """):
            m = st.markdown("""
                <style> 
                .stChatInput {
                width: min(51vw, 90.6667vh);
                }
                .stChatInput > div > div{
                max-width: min(51vw, 90.6667vh);
                }
                .stChatInput > div > div > div > textarea{
                height: min(10vh, 5.625vw);
                }
                </style>
                """, unsafe_allow_html=True)
            prompt = st.chat_input("What's on your mind...")
            if prompt:
                st.session_state['chat_history_log'][char_chat_name].insert(0, {'role': 'user', 'content': prompt})
    return prompt

def chat_response(char_chat_name, prompt):
    response, _ = st.session_state['npc_bots'][char_chat_name].to_chat(prompt)
    st.session_state['chat_history_log'][char_chat_name].insert(0, {'role': char_chat_name, 'content': response})

def chat_page():
    with stylable_container(key = 'container_chat', css_styles="",):
        darken_background()
        darken_background()
        
        # Char Image
        margin = 'min(18vw, 32vh)'
        char_html = """
        <div style="position: fixed; top: min(30vh, 16.875vw); left: """ + margin + """; transform: translateX(-50%);">
            <div style="position: relative; display: inline-block;">
                <img src="data:image/png;base64,{}" alt="charImageChat" class="char-image-chat">
            </div>
        </div>
        """
    
        css_code = """
        <style>
        .char-image-chat {
            height: min(70vh, 39.37vw);
            transition: box-shadow 0.3s ease-in-out;
            filter: drop-shadow(0 0 15px #ffffff) drop-shadow(0 0 50px #ffffff);
        }
        </style>
        """    
        img_base64 = get_base64_of_bin_file(CHAR_IMAGES[st.session_state['chat_char']])
        st.markdown(char_html.format(img_base64), unsafe_allow_html=True)
        st.markdown(css_code, unsafe_allow_html=True)

        # Name Tag
        tag_left_margin = 'min(19vw, 33.77778vh)'
        tag_top_margin = 'min(22vh, 12.375vw)'
        name_tag(CHAR_NAMES[st.session_state['chat_char']], tag_top_margin, tag_left_margin)

        # Trust Level Bar
        char_trust_bar(80)
        
        # Chatting section
        with stylable_container(
            key="container_with_border_chat",
            css_styles="""
                {
                    border: min(0.65vh, 0.3656vw) solid #E8A33B;
                    border-radius: 0.5rem;
                    background: #E8E8E8;
                    position: fixed;
                    top: min(15vh, 8.4375vw);
                    left: min(38vw, 67.5556vh);
                    height: min(75vh, 42.1875vw);
                    width: min(55vw, 97.7778vh);
                }
                """,
        ):

            char_chat_name = CHAR_NAMES[st.session_state['chat_char']]
            display_chat(char_chat_name)
            prompt = chat_input(char_chat_name)
            if prompt:
                display_chat(char_chat_name)
                chat_response(char_chat_name, prompt)
                st.rerun()
            if st.session_state['chat_portal']:
                close_button(11, 90)


def ending_page():
    if st.session_state['game_success'] != -1:
        # Close open windows & darken background
        portal_states = ['task_portal', 'settings_portal', 'chat_history_portal', 'chat_portal']
        portal_open = False
        for ps in portal_states:
            if st.session_state[ps]:
                portal_open = True
                st.session_state[ps] = False
        if portal_open:
            st.rerun()
        darken_background()

    with stylable_container(
        key="ending_page_container",
        css_styles="""
            {
                border: min(0.65vh, 0.3656vw) solid #B87A36;
                border-radius: 0.5rem;
                background: #E8E8E8;
                position: fixed;
                top: min(20vh, 11.25vw);
                left: min(22.5vw, 40vh);
                height: min(71vh, 39.9375vw);
                width: min(55vw, 97.7778vh);
            }
            """,
    ):
        if st.session_state['game_success'] == 1:
            image_file = 'game_images/success_star.png'
            st.balloons()
        elif st.session_state['game_success'] == 0:
            image_file = 'game_images/fail_cloud.png'
            st.snow()

        ### Header ###
        button_html = """
        <div style="position: fixed; top: min(22vh, 12.375vw); left: min(31vw, 55.1111vh);">
            <div style="position: relative; display: inline-block;">
                <img src="data:image/png;base64,{}" alt="Setting Header" class="ending-header" id="ending-header">
            </div>
        </div>
        """
        css_code = """
        <style>
        .ending-header {
            width: min(38vw, 67.5556vh);
        }
        </style>
        """
        image_base64 = get_base64_of_bin_file(image_file)
        st.markdown(button_html.format(image_base64), unsafe_allow_html=True)
        st.markdown(css_code, unsafe_allow_html=True)

        # Text container
        with stylable_container(
        key="ending_text_container",
        css_styles="""
            {
                position: fixed;
                top: min(38vh, 21.375vw);
                left: min(25vw, 44.44444vh);
                height: min(10.5vh, 33.1875vw);
                width: min(50vw, 88.88889vh);
                text-align: center;
                overflow-y: auto;
                overflow-x: hidden;
            }
            """,
        ):
            cols = st.columns((1, 100, 1))
            cols[1].markdown(f'In the end, **:red[{st.session_state["game_data"]["final_answer"]["killer"]}]** had an intention to kill **:blue[{st.session_state["game_data"]["final_answer"]["victim"]}]** because [Generate some summary for reason of murder xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.....].', unsafe_allow_html=True)

        # Feedback Survey Container
        with stylable_container(
        key="feedback_form_container",
        css_styles="""
            {
                position: fixed;
                top: min(52vh, 29.25vw);
                left: min(22.5vw, 40vh);
                height: min(59vh, 33.1875vw);
                width: min(55vw, 97.7778vh);
                text-align: center;
            }
            """,
        ):
            cols = st.columns((1, 10, 1))
            with cols[1].form('feed-back-form'):
                st.write("**Feedback Survey**")
                col_s = st.columns((2, 8))
                with col_s[0]:
                    st.write(' \n')
                    st.write('**Engagement**')
                    st.markdown("<p style='padding-top:8px'></p>", unsafe_allow_html=True)
                    st.write('**Innovativeness**')
                    st.markdown("<p style='padding-top:10px'></p>", unsafe_allow_html=True)
                    st.write('**Cohesiveness**')
                with col_s[1]:
                    st.slider("Engagement", 0, 5, 0, 1, label_visibility='collapsed')
                    st.slider("Innovativeness", 0, 5, 0, 1, label_visibility='collapsed')
                    st.slider("Cohesiveness", 0, 5, 0, 1, label_visibility='collapsed')
                received = st.form_submit_button('Submit & Exit Game')
            if received:
                st.switch_page('pages/user_dashboard.py')

def main():
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
    
    all_image_resize()

    if 'game_data' not in st.session_state:
        st.session_state['game_data'] = load_game_data()

    # Initialize session states
    if 'time_left' not in st.session_state:
        st.session_state['time_left'] = 0
    if 'screen_state' not in st.session_state:
        st.session_state['screen_state'] = 1
    if 'chosen_char' not in st.session_state:
        chosen_ones = random_select_char()
        st.session_state['chosen_char'] = chosen_ones[0]
        st.session_state['chosen_pos'] = chosen_ones[1]
    portal_states = ['task_portal', 'settings_portal', 'chat_history_portal', 'chat_portal']
    for p in portal_states:
        if p not in st.session_state:
            st.session_state[p] = False

    # Initialize chat states
    if 'chat_char' not in st.session_state:
        st.session_state['chat_char'] = 0
    if 'char_trust' not in st.session_state:
        st.session_state['char_trust'] = {i: 100 for i in CHAR_NAMES}
    if 'chat_history_log' not in st.session_state:
        st.session_state['chat_history_log'] = {i: [] for i in CHAR_NAMES}
    if 'npc_bots' not in st.session_state:
        st.session_state['npc_bots'] = load_npc_bot()
    
    # Initialize task status
    if 'task_status' not in st.session_state:
        st.session_state['task_status'] = {l: [False, False, False] for l in ['a', 'b', 'c']}
    if 'task_progress' not in st.session_state:
        st.session_state['task_progress'] = 0
    if 'cur_task' not in st.session_state:
        st.session_state['cur_task'] = -1
    if 'game_stages' not in st.session_state:
        st.session_state['game_stages'] = 0
        st.session_state['task_portal'] = True
    if 'game_success' not in st.session_state:
        st.session_state['game_success'] = -1
    
    # Set scenes
    if st.session_state['screen_state'] == 1:
        set_background(BACK_IMAGES[0])  # Provide the path to your image file
        navigation_buttons('left')
        navigation_buttons('right')
    elif st.session_state['screen_state'] == 0:
        set_background(BACK_IMAGES[1])  # Provide the path to your image file
        navigation_buttons('right')
    elif st.session_state['screen_state'] == 2:
        set_background(BACK_IMAGES[2])  # Provide the path to your image file
        navigation_buttons('left')
    
    for c, p in zip(st.session_state['chosen_char'], st.session_state['chosen_pos']):
        place_character(c, p)

    task_progress_bar()
    
    if st.session_state['game_stages'] == 2:
        darken_background()
    
    # Set functional buttons
    function_buttons('settings')
    function_buttons('task')
    function_buttons('chat_history')
    
    # potals
    if st.session_state['settings_portal']:
        settings_page()
    if st.session_state['task_portal']:
        task_page()
    if st.session_state['chat_history_portal']:
        chat_history_page()
    if st.session_state['chat_portal']:
        chat_page()

    if st.session_state['game_success'] != -1:
        ending_page()
    else:
        # Set timer
        test = st.empty()
        timer(test)


if __name__ == '__main__':
    main()



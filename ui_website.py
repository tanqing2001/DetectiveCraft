import streamlit as st
import authentication as auth
import base64
from st_clickable_images import clickable_images


def main():
    if 'authentication_status' not in st.session_state:
        st.switch_page('navigator.py')
    
    def logout_user():
        st.session_state['authentication_status'] = False
    logout_butt = st.button('Logout', key='logout_001', on_click=logout_user)
    if logout_butt:
        st.switch_page('navigator.py')
        
    st.write("Welcome to MindRev!")
    st.divider()
    st.write("MindRev is a revolutionary educational gaming platform that transforms learning into an exciting adventure. Leveraging Generative AI, users can create custom educational games or choose from a vast library of community-contributed games. MindRev offers a variety of engaging games, such as murder mysteries, spy missions, and fantasy quests, among many others, designed to enhance critical thinking, technical skills, and creative exploration. With tools for game creation and sharing, MindRev fosters a vibrant community of learners, educators, and game designers, emphasizing interactive and immersive learning experiences that promise an unforgettable educational journey.")
    st.divider()
    # st.write("Choose your adventure!")

    games = ["The Kill Venture", "Sin Kitty", "Mars Revolta", "Savior Simone", "Banditos", "AnnaDroid", "Deadworld Reborn", "Elephant in Space", "Killer Nick"]
    images = []
    for e in [
        "game1_thumbnail.jpg", 
        "game2_thumbnail.jpg", 
        "game3_thumbnail.jpg", 
        "game4_thumbnail.jpg",
        "game5_thumbnail.jpg",
        "game6_thumbnail.jpg",
        "game7_thumbnail.jpg",
        "game8_thumbnail.jpg",
        "game9_thumbnail.jpg",
    ]:
        with open(f"website_images/{e}", "rb") as image:
            # Encode the image to base64
            encoded = base64.b64encode(image.read()).decode()
            image_data = f"data:image/png;base64,{encoded}"
            images.append(image_data)

    clicked = clickable_images(
        images,
        titles=[e for e in games],
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={
            "margin": "10px", 
            "height": "100px", 
            "border": "2px solid #e0e0e0", 
            "border-radius": "10px", 
            "box-shadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2)",
            "cursor": "pointer"  # Added cursor style
        },
    )

    if clicked == 0:
        st.switch_page('pages/game_ui.py')

if __name__ == '__main__':
    main()

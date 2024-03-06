import streamlit as st


def add_css():
    # Inject custom CSS to remove form borders using data-testid attribute
    st.markdown(
        f"""
            <style>
                .filter-errors {{
                    color: red !important;
                }}
                .element-container:has(.btn-selected) + div button{{
                    border: 1.5px black solid !important;
                }}
                .element-container:has(.selected) + div button {{
                    border: 1.5px black solid !important;
                }}
                .element-container:has(.black-background) + div{{
                    border-color: black !important; /* New border color on hover */
                }}
                .st-g1:focus {{
                    color: black !important; /* New border color on hover */
                }}
                [data-baseweb="tab-list"] p {{
                    color: white !important; /* New border color on hover */
                }}
                [data-baseweb="tab-highlight"] {{
                    background-color: white !important; /* New border color on hover */
                }}
                button:focus {{
                    border-color: black !important; /* New border color on hover */
                }}
                button:hover {{
                    border-color: black !important; /* New border color on hover */
                }}
                [data-testid="stSidebar"] {{
                    background-color: rgba(128, 0, 128, 0.66) !important; /* #800080a8 with 50% transparency */
                }}
                .element-container:has(.selected) + div p{{
                    font-weight: 600;
                }}
                .element-container:has(.button-after-red) + div button{{
                    background-color: #f15454 !important;
                }}
                .element-container:has(.button-after-green) + div button{{
                    background-color: #90ee90 !important;
                }}            
                .element-container:has(.button-after-orange) + div button{{
                    background-color: #ffcc99 !important;
                }}
                .element-container:has(.button-after-gray) + div button{{
                    background-color: #d3d3d3 !important;
                }}
                .element-container:has(.800080a8) + div button{{
                    background-color: #800080a8 !important;
                }}
                .stApp {{
                    background-image: url("https://ramimusic.io/shop/wp-content/uploads/2024/01/background.png");
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }}
                header {{
                    display: none !important;
                }}
                [data-testid="stBottom"]>div{{
                    background-color: transparent !important;
                }}
                .stChatFloatingInputContainer {{
                    background-color: transparent !important;
                }}
                .stChatMessage {{
                    background-color: transparent !important;
                }}
                .stChatMessage * {{
                    color: white !important;
                }}
                ol *{{
                    color: white !important;
                }}
                button *{{
                    color: black !important;
                }}
                [data-testid="stSidebar"] p {{
                    color: white;
                }}
                [data-testid="stSidebar"] h1 {{
                    color: white;
                }}
                [data-testid="stSidebar"] span {{
                    color: white;
                }}
                .main p {{
                    color: white;
                }}
                # .row-widget {{
                #     color: white !important;
                # }}
                .main h1{{
                    color: white !important;
                }}
                .main span{{
                    color: white !important;
                }}
            </style>
            """,
        unsafe_allow_html=True,
    )


import streamlit as st

st.set_page_config(
    page_title="Family Store",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #111318;
    color: white;
}
section[data-testid="stSidebar"] {
    background: #1b1e25;
}
h1, h2, h3, p, label {
    color: white !important;
}
div.stButton > button {
    background: #d4a84f;
    color: #111318;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    width: 100%;
}
div.stButton > button:hover {
    background: #f0c66b;
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 Family Store")
st.caption("Your Home, Your Comfort")

st.divider()

st.subheader("Welcome to our store")

search = st.text_input(
    "Search products",
    placeholder="Search for household products..."
)

categories = [
    "All Products",
    "Cleaning",
    "Kitchen",
    "Home Essentials",
    "Personal Care"
]

selected = st.selectbox(
    "Categories",
    categories
)

st.info("Our products will appear here.")

st.success("Family Store is running!")

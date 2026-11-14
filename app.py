
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
.product {
    background: #1b1e25;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #333;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 Family Store")
st.caption("كل احتياجات البيت والعائلة في مكان واحد")
st.divider()

st.subheader("مرحباً بك في متجر العائلة ❤️")

search = st.text_input(
    "🔎 ابحث عن منتج",
    placeholder="اكتب اسم المنتج..."
)

categories = [
    "كل المنتجات",
    "مواد التنظيف",
    "أدوات المطبخ",
    "احتياجات المنزل",
    "العناية الشخصية"
]

category = st.selectbox("اختر القسم", categories)

products = [
    {"name": "مسحوق غسيل", "category": "مواد التنظيف", "price": 5000},
    {"name": "سائل جلي", "category": "مواد التنظيف", "price": 2500},
    {"name": "منظف أرضيات", "category": "مواد التنظيف", "price": 3000},
    {"name": "حافظة طعام", "category": "أدوات المطبخ", "price": 4000},
    {"name": "سلة منزلية", "category": "احتياجات المنزل", "price": 6000},
    {"name": "صابون يدين", "category": "العناية الشخصية", "price": 2000}
]

if "cart" not in st.session_state:
    st.session_state.cart = []

filtered = [
    p for p in products
    if (category == "كل المنتجات" or p["category"] == category)
    and search.lower() in p["name"].lower()
]

st.subheader("🛍️ منتجاتنا")

if not filtered:
    st.info("لا توجد منتجات مطابقة للبحث.")
else:
    cols = st.columns(2)
    for i, product in enumerate(filtered):
        with cols[i % 2]:
            st.markdown('<div class="product">', unsafe_allow_html=True)
            st.subheader(product["name"])
            st.write(product["category"])
            st.write(f'السعر: {product["price"]:,} دينار')
            if st.button("أضف إلى السلة", key=f"add_{i}"):
                st.session_state.cart.append(product)
                st.success("تمت الإضافة إلى السلة")
            st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🛒 سلة المشتريات")

if st.session_state.cart:
    total = sum(p["price"] for p in st.session_state.cart)
    for p in st.session_state.cart:
        st.write(f'{p["name"]} — {p["price"]:,} دينار')
    st.write(f"الإجمالي: {total:,} دينار")
    if st.button("إفراغ السلة"):
        st.session_state.cart = []
        st.rerun()
else:
    st.info("سلتك فارغة حالياً.")

st.divider()
st.caption("Family Store © 2026")

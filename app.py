import streamlit as st
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(
    page_title="Family Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp { background: #f4f7fb; color: #172033; }
header[data-testid="stHeader"] { background: rgba(244,247,251,.92); }
section[data-testid="stSidebar"] { background: #eaf0f8; }
h1,h2,h3,p,label,div[data-testid="stMarkdownContainer"] { color: #172033; }
div.stButton > button, div.stFormSubmitButton > button {
    background: #1769aa; color: white; border: 0;
    border-radius: 10px; font-weight: 700; min-height: 42px;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background: #0f4f85; color: white; border: 0;
}
.product-card {
    background: white; border: 1px solid #e1e8f0;
    border-radius: 15px; padding: 14px; margin-bottom: 12px;
}
.small-muted { color: #64748b; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

st.title("🛒 Family Store")
st.caption("كل احتياجات البيت والعائلة في مكان واحد")

# ---------- CONNECTION ----------
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=30, show_spinner=False)
def load_products():
    db = get_supabase()
    response = (
        db.table("products")
        .select("*")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []

try:
    db = get_supabase()
except Exception:
    st.error("تعذر الاتصال بقاعدة البيانات. تحقق من SUPABASE_URL وSUPABASE_KEY داخل Streamlit → Settings → Secrets.")
    st.stop()

if "cart" not in st.session_state:
    st.session_state.cart = {}
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

# ---------- NAVIGATION ----------
page = st.sidebar.radio("القائمة", ["المتجر", "سلة المشتريات", "الإدارة"])
st.sidebar.caption("Family Store © 2026")

# ---------- CUSTOMER STORE ----------
if page == "المتجر":
    st.subheader("مرحباً بك في متجر العائلة")
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔎 ابحث عن منتج", placeholder="اكتب اسم المنتج...")
    with col2:
        category_filter = st.text_input("القسم (اختياري)", placeholder="مثال: مواد التنظيف")

    try:
        products = load_products()
    except Exception as e:
        st.error("تعذر تحميل المنتجات من قاعدة البيانات.")
        st.caption(str(e))
        products = []

    filtered = [
        p for p in products
        if search.strip().casefold() in str(p.get("name", "")).casefold()
        and (
            not category_filter.strip()
            or category_filter.strip().casefold() in str(p.get("category", "")).casefold()
        )
    ]

    st.subheader(f"🛍️ المنتجات ({len(filtered)})")
    if not filtered:
        st.info("لا توجد منتجات حالياً. ستظهر المنتجات هنا عندما تضيفها من لوحة الإدارة.")
    else:
        cols = st.columns(2)
        for i, product in enumerate(filtered):
            with cols[i % 2]:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                image_url = product.get("image_url") or ""
                if image_url.startswith("https://") or image_url.startswith("http://"):
                    st.image(image_url, use_container_width=True)
                st.markdown(f"**{product.get('name', 'منتج')}**")
                st.caption(product.get("category", ""))
                if product.get("description"):
                    st.write(product["description"])
                price = int(product.get("price_iqd") or product.get("price") or 0)
                stock = int(product.get("stock") or 0)
                st.write(f"**السعر: {price:,} دينار**")
                st.caption(f"المتوفر: {stock}")
                
if stock > 0:
    qty = st.number_input(
        "اختر الكمية",
        min_value=1,
        max_value=stock,
        value=1,
        step=1,
        key=f"qty_{product['id']}"
    )

    if st.button("أضف إلى السلة", key=f"add_{product['id']}", use_container_width=True):
        pid = str(product["id"])
        current = st.session_state.cart.get(
            pid, {"product": product, "quantity": 0}
        )

        if current["quantity"] + qty <= stock:
            current["quantity"] += qty
            st.session_state.cart[pid] = current
            st.success("تمت الإضافة إلى السلة")
        else:
            st.warning("الكمية المطلوبة تتجاوز المخزون")
else:
    st.warning("غير متوفر حالياً")

                st.markdown("</div>", unsafe_allow_html=True)

# ---------- CART AND CHECKOUT ----------
elif page == "سلة المشتريات":
    st.subheader("🛒 سلة المشتريات")
    cart = st.session_state.cart
    if not cart:
        st.info("سلتك فارغة حالياً.")
    else:
        total = 0
        for pid, item in list(cart.items()):
            product = item["product"]
            price = int(product.get("price_iqd") or product.get("price") or 0)
            qty_col, info_col, remove_col = st.columns([1, 3, 1])
            with qty_col:
                new_qty = st.number_input(
                    "الكمية", min_value=1,
                    max_value=max(1, int(product.get("stock") or 1)),
                    value=int(item["quantity"]), key=f"qty_{pid}"
                )
            with info_col:
                st.write(f"**{product.get('name', 'منتج')}**")
                st.caption(f"{price:,} × {new_qty:,} = {price * new_qty:,} دينار")
            with remove_col:
                if st.button("حذف", key=f"remove_{pid}"):
                    del st.session_state.cart[pid]
                    st.rerun()
            st.session_state.cart[pid]["quantity"] = int(new_qty)
            total += price * int(new_qty)

        st.divider()
        st.subheader(f"الإجمالي: {total:,} دينار")

        with st.form("checkout_form"):
            st.markdown("### بيانات التوصيل")
            customer_name = st.text_input("الاسم")
            phone = st.text_input("رقم الهاتف")
            address = st.text_area("العنوان بالتفصيل")
            notes = st.text_area("ملاحظات (اختياري)")
            submitted = st.form_submit_button("تأكيد الطلب", use_container_width=True)

        if submitted:
            if not customer_name.strip() or not phone.strip() or not address.strip():
                st.error("يرجى إدخال الاسم ورقم الهاتف والعنوان.")
            else:
                try:
                    # Recheck prices and stock from database before saving.
                    fresh_items = []
                    fresh_total = 0
                    for pid, item in st.session_state.cart.items():
                        row = (
                            db.table("products").select("*")
                            .eq("id", int(pid)).eq("is_active", True)
                            .single().execute().data
                        )
                        qty = int(item["quantity"])
                        stock = int(row.get("stock") or 0)
                        if qty > stock:
                            raise ValueError(f"الكمية المطلوبة من {row.get('name')} غير متوفرة.")
                        price = int(row.get("price_iqd") or row.get("price") or 0)
                        fresh_total += price * qty
                        fresh_items.append({
                            "product_id": int(pid),
                            "product_name": row.get("name", "منتج"),
                            "quantity": qty,
                            "price": price,
                        })

                    order_data = {
                        "customer_name": customer_name.strip(),
                        "phone": phone.strip(),
                        "address": address.strip(),
                        "notes": notes.strip(),
                        "total_iqd": fresh_total,
                        "total": fresh_total,
                        "status": "new"
                    }
                    saved_order = db.table("orders").insert(order_data).execute().data[0]
                    order_id = saved_order["id"]
                    try:
                        items_to_save = [
                            {"order_id": order_id, **item} for item in fresh_items
                        ]
                        db.table("order_items").insert(items_to_save).execute()
                    except Exception:
                        db.table("orders").delete().eq("id", order_id).execute()
                        raise

                    for item in fresh_items:
                        product_id = item["product_id"]
                        old = db.table("products").select("stock").eq("id", product_id).single().execute().data
                        new_stock = max(0, int(old.get("stock") or 0) - item["quantity"])
                        db.table("products").update({"stock": new_stock}).eq("id", product_id).execute()

                    st.session_state.cart = {}
                    load_products.clear()
                    st.success(f"تم استلام طلبك بنجاح. رقم الطلب: {order_id}")
                    st.info("سيتم التواصل معك لتأكيد الطلب.")
                except Exception as e:
                    st.error("لم نتمكن من تسجيل الطلب. تحقق من إعدادات قاعدة البيانات أو كمية المنتجات.")
                    st.caption(str(e))

# ---------- ADMIN ----------
elif page == "الإدارة":
    if not st.session_state.admin_ok:
        st.subheader("🔐 دخول الإدارة")
        with st.form("admin_login"):
            password = st.text_input("كلمة مرور الإدارة", type="password")
            login = st.form_submit_button("دخول", use_container_width=True)
        if login:
            expected = st.secrets.get("ADMIN_PASSWORD", "")
            if expected and password == expected:
                st.session_state.admin_ok = True
                st.rerun()
            elif not expected:
                st.error("أضف ADMIN_PASSWORD إلى Streamlit → Settings → Secrets أولاً.")
            else:
                st.error("كلمة المرور غير صحيحة.")
    else:
        st.subheader("⚙️ لوحة إدارة Family Store")
        if st.button("تسجيل الخروج من الإدارة"):
            st.session_state.admin_ok = False
            st.rerun()

        admin_tab = st.tabs(["إضافة منتج", "إدارة المنتجات", "الطلبات"])

        with admin_tab[0]:
            st.markdown("### إضافة منتج جديد")
            with st.form("add_product", clear_on_submit=True):
                name = st.text_input("اسم المنتج")
                category = st.text_input("القسم")
                description = st.text_area("الوصف")
                price = st.number_input("السعر بالدينار", min_value=0, step=250)
                stock = st.number_input("الكمية المتوفرة", min_value=0, step=1)
                image_url = st.text_input("رابط صورة المنتج (اختياري)")
                add = st.form_submit_button("حفظ المنتج", use_container_width=True)
            if add:
                if not name.strip() or not category.strip():
                    st.error("اسم المنتج والقسم مطلوبان.")
                else:
                    try:
                        db.table("products").insert({
                            "name": name.strip(),
                            "category": category.strip(),
                            "description": description.strip(),
                            "price_iqd": int(price),
                            "price": int(price),
                            "stock": int(stock),
                            "image_url": image_url.strip(),
                            "is_active": True
                        }).execute()
                        load_products.clear()
                        st.success("تمت إضافة المنتج إلى المتجر.")
                    except Exception as e:
                        st.error("تعذرت إضافة المنتج. تحقق من صلاحيات قاعدة البيانات.")
                        st.caption(str(e))

        with admin_tab[1]:
            st.markdown("### تعديل أو إخفاء منتج")
            try:
                all_products = db.table("products").select("*").order("id", desc=True).execute().data or []
            except Exception as e:
                all_products = []
                st.error("تعذر تحميل المنتجات.")
                st.caption(str(e))
            if all_products:
                options = {f"{p.get('name', 'منتج')} — #{p['id']}": p for p in all_products}
                selected_label = st.selectbox("اختر المنتج", list(options.keys()))
                selected = options[selected_label]
                with st.form("edit_product"):
                    edit_name = st.text_input("اسم المنتج", value=selected.get("name") or "")
                    edit_category = st.text_input("القسم", value=selected.get("category") or "")
                    edit_description = st.text_area("الوصف", value=selected.get("description") or "")
                    edit_price = st.number_input("السعر", min_value=0, value=int(selected.get("price_iqd") or selected.get("price") or 0), step=250)
                    edit_stock = st.number_input("المخزون", min_value=0, value=int(selected.get("stock") or 0), step=1)
                    edit_image = st.text_input("رابط الصورة", value=selected.get("image_url") or "")
                    edit_active = st.checkbox("إظهار المنتج في المتجر", value=bool(selected.get("is_active", True)))
                    save_edit = st.form_submit_button("حفظ التعديلات", use_container_width=True)
                if save_edit:
                    try:
                        db.table("products").update({
                            "name": edit_name.strip(),
                            "category": edit_category.strip(),
                            "description": edit_description.strip(),
                            "price_iqd": int(edit_price),
                            "price": int(edit_price),
                            "stock": int(edit_stock),
                            "image_url": edit_image.strip(),
                            "is_active": edit_active
                        }).eq("id", selected["id"]).execute()
                        load_products.clear()
                        st.success("تم تحديث المنتج.")
                        st.rerun()
                    except Exception as e:
                        st.error("تعذر تحديث المنتج.")
                        st.caption(str(e))
            else:
                st.info("لا توجد منتجات بعد. أضف أول منتج من تبويب إضافة منتج.")

        with admin_tab[2]:
            st.markdown("### طلبات الزبائن")
            try:
                orders = db.table("orders").select("*").order("created_at", desc=True).limit(100).execute().data or []
            except Exception as e:
                orders = []
                st.error("تعذر تحميل الطلبات.")
                st.caption(str(e))
            if not orders:
                st.info("لا توجد طلبات حتى الآن.")
            for order in orders:
                with st.expander(f"طلب #{order['id']} — {order.get('customer_name', '')} — {int(order.get('total_iqd') or 0):,} د.ع"):
                    st.write(f"الهاتف: {order.get('phone', '')}")
                    st.write(f"العنوان: {order.get('address', '')}")
                    st.write(f"ملاحظات: {order.get('notes', '')}")
                    st.write(f"التاريخ: {order.get('created_at', '')}")
                    st.write("تفاصيل الطلب:")
                    try:
                        items = db.table("order_items").select("*").eq("order_id", order["id"]).execute().data or []
                        for item in items:
                            st.write(f"- {item.get('product_name', 'منتج')} × {item.get('quantity', 0)} — {int(item.get('price_iqd') or 0):,} د.ع")
                    except Exception:
                        st.caption("تعذر تحميل تفاصيل هذا الطلب.")
                    statuses = ["new", "confirmed", "preparing", "shipped", "delivered", "cancelled"]
                    current = order.get("status") or "new"
                    status = st.selectbox(
                        "حالة الطلب", statuses,
                        index=statuses.index(current) if current in statuses else 0,
                        key=f"status_{order['id']}"
                    )
                    if st.button("تحديث الحالة", key=f"update_order_{order['id']}"):
                        db.table("orders").update({"status": status}).eq("id", order["id"]).execute()
                        st.success("تم تحديث حالة الطلب.")
                        st.rerun()

st.divider()
st.caption("Family Store © 2026")

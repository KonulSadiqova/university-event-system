import streamlit as st
import pandas as pd
from database import init_db
from services import DatabaseManager, EventManager, RegistrationManager

# Verilənlər bazasını işə salaq
init_db()

db_manager = DatabaseManager()
event_manager = EventManager(db_manager)
reg_manager = RegistrationManager(db_manager)

# Səhifə konfiqurasiyası
st.set_page_config(page_title="Universitet Tədbir Sistemi", page_icon="🎓", layout="wide")

st.title("🎓 Universitet Tədbirlərinin İdarə Edilməsi və Qeydiyyat Sistemi")

# Yan menyu (Sidebar)
menu = st.sidebar.selectbox("Menyu", [
    "Tədbirlər Siyahısı", 
    "Yeni Tədbir Yarat", 
    "Tədbirə Qeydiyyat", 
    "İdarəetmə Paneli & Statistika"
])

if menu == "Tədbirlər Siyahısı":
    st.header("📅 Mövcud Tədbirlər Siyahısı")
    events = event_manager.get_all_events()
    
    if events:
        df = pd.DataFrame(events, columns=["ID", "Başlıq", "Təsvir", "Kateqoriya", "Tarix", "Saat", "Məkan", "Limit"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Hələ ki, sistemdə heç bir tədbir yoxdur.")

elif menu == "Yeni Tədbir Yarat":
    st.header("➕ Yeni Tədbir Əlavə Et")
    
    # Kateqoriyaların bazada olub-olmadığını yoxlayaq və əlavə edək
    categories = db_manager.fetch_query("SELECT id, name FROM categories")
    if not categories:
        db_manager.execute_query("INSERT INTO categories (name) VALUES ('Elmi')")
        db_manager.execute_query("INSERT INTO categories (name) VALUES ('Təlim')")
        db_manager.execute_query("INSERT INTO categories (name) VALUES ('Müsabiqə')")
        categories = db_manager.fetch_query("SELECT id, name FROM categories")
    
    cat_dict = {name: cat_id for cat_id, name in categories}

    with st.form("event_form"):
        title = st.text_input("Tədbirin Adı")
        description = st.text_area("Təsviri")
        selected_category = st.selectbox("Kateqoriya", list(cat_dict.keys()))
        date = st.date_input("Tarix")
        time = st.time_input("Saat")
        location = st.text_input("Keçirilmə Yeri")
        capacity = st.number_input("Maksimum İştirakçı Sayı", min_value=1, value=50)
        
        submit = st.form_submit_button("Tədbiri Yarat")
        if submit:
            if title and location:
                cat_id = cat_dict[selected_category]
                event_manager.add_event(title, description, cat_id, str(date), str(time), location, capacity)
                st.success("Tədbir uğurla yaradıldı!")
            else:
                st.error("Zəhmət olmasa tədbirin adını və yerini qeyd edin.")

elif menu == "Tədbirə Qeydiyyat":
    st.header("📝 Tədbir İştirakçı Qeydiyyatı")
    events = event_manager.get_all_events()
    
    if events:
        event_options = {f"{e[1]} ({e[4]})": e[0] for e in events}
        selected_event_name = st.selectbox("Tədbir seçin", list(event_options.keys()))
        selected_event_id = event_options[selected_event_name]
        
        with st.form("reg_form"):
            full_name = st.text_input("Ad və Soyad")
            email = st.text_input("E-poçt ünvanı")
            reg_submit = st.form_submit_button("Qeydiyyatdan Keç")
            
            if reg_submit:
                if full_name and email:
                    success, message = reg_manager.register_participant(selected_event_id, full_name, email)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Zəhmət olmasa bütün sahələri doldurun.")
    else:
        st.warning("Qeydiyyatdan keçmək üçün əvvəlcə mövcud tədbir olmalıdır.")

elif menu == "İdarəetmə Paneli & Statistika":
    st.header("📊 İdarəetmə Paneli və Statistika")
    events = event_manager.get_all_events()
    total_events = len(events)
    
    registrations = db_manager.fetch_query("SELECT COUNT(*) FROM registrations")
    total_regs = registrations[0][0] if registrations else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Ümumi Tədbir Sayı", total_events)
    col2.metric("Ümumi Qeydiyyat Sayı", total_regs)
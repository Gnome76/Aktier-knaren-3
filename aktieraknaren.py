import streamlit as st
import json
import os

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_target_price(pe_list, ps_list, earnings_y, earnings_ny, growth_y, growth_ny):
    try:
        avg_pe = sum(pe_list) / len(pe_list)
        avg_ps = sum(ps_list) / len(ps_list)

        target_price_pe = avg_pe * earnings_ny
        revenue_growth_factor = 1 + (growth_y + growth_ny) / 200
        target_price_ps = avg_ps * earnings_ny * revenue_growth_factor

        final_target_price = (target_price_pe + target_price_ps) / 2
        return round(final_target_price, 2)
    except:
        return 0.0

def undervaluation_status(current_price, target_price):
    try:
        diff_pct = (target_price - current_price) / target_price * 100
        if diff_pct >= 40:
            return "Undervärderad >40%", diff_pct
        elif 30 <= diff_pct < 40:
            return "Undervärderad 30–39.99%", diff_pct
        elif 0 < diff_pct < 30:
            return "Undervärderad <30%", diff_pct
        else:
            return "Övervärderad", diff_pct
    except:
        return "Okänt", 0

# App-start
st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("📈 Aktieräknaren")

data = load_data()
company_names = sorted(data.keys())

# === Filtrering ===
st.subheader("🔍 Filtrera bolag")
filter_option = st.selectbox("Visa:", [
    "Alla bolag",
    "Undervärderad 30–39.99%",
    "Undervärderad >40%"
])

filtered_companies = []
for name in company_names:
    c = data[name]
    target = calculate_target_price(c["pe"], c["ps"], c["vinst_iår"], c["vinst_next"], c["oms_y"], c["oms_next"])
    status, diff = undervaluation_status(c["kurs"], target)

    if filter_option == "Alla bolag":
        filtered_companies.append(name)
    elif filter_option == "Undervärderad 30–39.99%" and status == "Undervärderad 30–39.99%":
        filtered_companies.append(name)
    elif filter_option == "Undervärderad >40%" and status == "Undervärderad >40%":
        filtered_companies.append(name)

selected_company = st.selectbox("Välj bolag", [""] + filtered_companies)

if "clear_fields" not in st.session_state:
    st.session_state.clear_fields = True

# === Nytt bolag ===
if st.button("➕ Lägg till nytt bolag"):
    st.session_state.clear_fields = True
    selected_company = ""

# === Formulär ===
st.subheader("📊 Nyckeltal och analys")

name = st.text_input("Bolagsnamn", value=selected_company)

def num_input(label, default):
    return st.number_input(label, value=default, step=0.01, format="%.2f", placeholder="Ange värde")

# Tomma eller befintliga värden
company_data = data.get(name, {}) if name else {}

kurs = num_input("Nuvarande kurs", None if st.session_state.clear_fields else company_data.get("kurs", 0))

col1, col2, col3, col4, col5 = st.columns(5)
pe_values = [col.number_input(f"P/E {i+1}", value=None if st.session_state.clear_fields else company_data.get("pe", [0]*5)[i], step=0.01, format="%.2f", placeholder="") for i, col in enumerate([col1, col2, col3, col4, col5])]

col6, col7, col8, col9, col10 = st.columns(5)
ps_values = [col.number_input(f"P/S {i+1}", value=None if st.session_state.clear_fields else company_data.get("ps", [0]*5)[i], step=0.01, format="%.2f", placeholder="") for i, col in enumerate([col6, col7, col8, col9, col10])]

col11, col12 = st.columns(2)
vinst_iår = col11.number_input("Vinst i år", value=None if st.session_state.clear_fields else company_data.get("vinst_iår", 0), step=0.01, format="%.2f", placeholder="")
vinst_next = col12.number_input("Vinst nästa år", value=None if st.session_state.clear_fields else company_data.get("vinst_next", 0), step=0.01, format="%.2f", placeholder="")

col13, col14 = st.columns(2)
oms_y = col13.number_input("Omsättningstillväxt i år (%)", value=None if st.session_state.clear_fields else company_data.get("oms_y", 0), step=0.1, format="%.1f", placeholder="")
oms_next = col14.number_input("Omsättningstillväxt nästa år (%)", value=None if st.session_state.clear_fields else company_data.get("oms_next", 0), step=0.1, format="%.1f", placeholder="")

# === Spara bolag ===
if st.button("💾 Spara bolag") and name:
    data[name] = {
        "kurs": kurs,
        "pe": pe_values,
        "ps": ps_values,
        "vinst_iår": vinst_iår,
        "vinst_next": vinst_next,
        "oms_y": oms_y,
        "oms_next": oms_next
    }
    save_data(data)
    st.success(f"{name} sparat!")
    st.session_state.clear_fields = False

# === Ta bort bolag ===
if selected_company and st.button("🗑️ Ta bort bolag"):
    del data[selected_company]
    save_data(data)
    st.success(f"{selected_company} borttaget!")
    st.session_state.clear_fields = True

# === Beräkning av targetkurs ===
if name and all([kurs, vinst_next, pe_values[0], ps_values[0]]):
    target = calculate_target_price(pe_values, ps_values, vinst_iår, vinst_next, oms_y, oms_next)
    status, diff = undervaluation_status(kurs, target)
    buy_30 = round(target * 0.7, 2)
    buy_40 = round(target * 0.6, 2)

    st.subheader("🎯 Analys")
    st.markdown(f"""
    - **Targetkurs:** {target} kr  
    - **Status:** {status} ({diff:.2f}% skillnad)  
    - 📉 **Köp vid 30% marginal:** {buy_30} kr  
    - 📉 **Köp vid 40% marginal:** {buy_40} kr
    """)

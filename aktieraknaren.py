import streamlit as st
import json
import os

# Filnamn för databasen
DATA_FILE = "data.json"

# === FUNKTIONER ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_target_price(pe_list, ps_list, earnings_y, earnings_ny, growth_y, growth_ny):
    avg_pe = sum(pe_list) / len(pe_list)
    avg_ps = sum(ps_list) / len(ps_list)

    target_price_pe = avg_pe * earnings_ny
    revenue_growth_factor = 1 + (growth_y + growth_ny) / 200
    target_price_ps = avg_ps * earnings_ny * revenue_growth_factor

    final_target_price = (target_price_pe + target_price_ps) / 2
    return round(final_target_price, 2)

def undervaluation_status(current_price, target_price):
    diff_pct = (target_price - current_price) / target_price * 100
    if diff_pct >= 40:
        return "Undervärderad >40%", diff_pct
    elif 30 <= diff_pct < 40:
        return "Undervärderad 30–39.99%", diff_pct
    elif 0 < diff_pct < 30:
        return "Undervärderad <30%", diff_pct
    else:
        return "Övervärderad", diff_pct

# === APP START ===
st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("📈 Aktieräknaren")

companies = load_data()
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

# === SIDOPANEL ===
st.sidebar.header("🔍 Filtrera bolag")
filter_option = st.sidebar.selectbox(
    "Visa bolag som är...",
    ["Alla", "Undervärderad 30–39.99%", "Undervärderad >40%"]
)

filtered_companies = {}
for name, info in companies.items():
    status, diff = undervaluation_status(info["current_price"], info["target_price"])
    if filter_option == "Alla" or status == filter_option:
        filtered_companies[name] = info

selected = st.sidebar.selectbox("📂 Välj bolag", [""] + list(filtered_companies.keys()))

if selected:
    st.session_state.selected_company = selected
    company_data = companies[selected]
    name = selected
    current_price = company_data["current_price"]
    pe_values = company_data["pe_values"]
    ps_values = company_data["ps_values"]
    earnings_y = company_data["earnings_y"]
    earnings_ny = company_data["earnings_ny"]
    growth_y = company_data["growth_y"]
    growth_ny = company_data["growth_ny"]
else:
    name = ""
    current_price = 0.0
    pe_values = [0.0] * 5
    ps_values = [0.0] * 5
    earnings_y = 0.0
    earnings_ny = 0.0
    growth_y = 0.0
    growth_ny = 0.0

# === FORMULÄR ===
st.header("➕ Lägg till / Redigera bolag")
with st.form("company_form"):
    name = st.text_input("Bolagsnamn", value=name)
    current_price = st.number_input("Nuvarande kurs", value=current_price, step=0.1)

    st.markdown("#### P/E-värden (senaste 5 åren)")
    pe_values = [st.number_input(f"P/E {i+1}", value=pe_values[i], step=0.1, key=f"pe_{i}") for i in range(5)]

    st.markdown("#### P/S-värden (senaste 5 åren)")
    ps_values = [st.number_input(f"P/S {i+1}", value=ps_values[i], step=0.1, key=f"ps_{i}") for i in range(5)]

    col1, col2 = st.columns(2)
    with col1:
        earnings_y = st.number_input("Vinst i år", value=earnings_y, step=0.1)
        growth_y = st.number_input("Omsättningstillväxt i år (%)", value=growth_y, step=0.1)
    with col2:
        earnings_ny = st.number_input("Vinst nästa år", value=earnings_ny, step=0.1)
        growth_ny = st.number_input("Omsättningstillväxt nästa år (%)", value=growth_ny, step=0.1)

    submitted = st.form_submit_button("💾 Spara bolag")
    if submitted:
        if name.strip() == "":
            st.error("❌ Ange ett bolagsnamn.")
        else:
            target_price = calculate_target_price(pe_values, ps_values, earnings_y, earnings_ny, growth_y, growth_ny)
            companies[name] = {
                "current_price": current_price,
                "pe_values": pe_values,
                "ps_values": ps_values,
                "earnings_y": earnings_y,
                "earnings_ny": earnings_ny,
                "growth_y": growth_y,
                "growth_ny": growth_ny,
                "target_price": target_price
            }
            companies = dict(sorted(companies.items()))  # sortera i bokstavsordning
            save_data(companies)
            st.success(f"{name} sparades!")
            st.session_state.selected_company = name
            st.experimental_rerun()

# === ANALYSDEL ===
if st.session_state.selected_company:
    st.subheader("📊 Analys")
    company = companies[st.session_state.selected_company]
    target = company["target_price"]
    status, diff = undervaluation_status(company["current_price"], target)
    margin_30 = round(target * 0.7, 2)
    margin_40 = round(target * 0.6, 2)

    st.write(f"🎯 **Targetkurs:** {target} kr")
    st.write(f"📉 **Nuvarande kurs:** {company['current_price']} kr")
    st.write(f"📌 **Status:** {status} ({round(diff, 2)}%)")
    st.write(f"💰 **Köp vid 30% marginal:** {margin_30} kr")
    st.write(f"💰 **Köp vid 40% marginal:** {margin_40} kr")

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        if st.button("🗑️ Ta bort bolag"):
            del companies[st.session_state.selected_company]
            save_data(companies)
            st.success("Bolaget togs bort.")
            st.session_state.selected_company = None
            st.experimental_rerun()
    with colB:
        if st.button("➕ Lägg till nytt bolag"):
            st.session_state.selected_company = None
            st.experimental_rerun()

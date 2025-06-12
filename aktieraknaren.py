import streamlit as st
import json
import os

st.set_page_config(page_title="Aktieräknaren", layout="wide")

st.title("📊 Aktieräknaren")
st.markdown("Analysera aktier med hjälp av historiska nyckeltal och tillväxt.")

# Filnamn för lokal databas
DATA_FILE = "data.json"

# Ladda eller initiera databas
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        st.session_state.companies = json.load(f)
else:
    st.session_state.companies = {}

# Funktion för att spara till JSON
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.companies, f, indent=2)

# Funktion för att rensa formulär
def reset_form():
    st.session_state.selected_company = None
    for i in range(1, 6):
        st.session_state[f"pe_{i}"] = 0.0
        st.session_state[f"ps_{i}"] = 0.0
    st.session_state["Förväntad vinst i år"] = 0.0
    st.session_state["Förväntad vinst nästa år"] = 0.0
    st.session_state["Omsättningstillväxt i år (%)"] = 0.0
    st.session_state["Omsättningstillväxt nästa år (%)"] = 0.0
    st.session_state["Nuvarande kurs"] = 0.0
    st.session_state["Bolagsnamn"] = ""

# Knapp för att lägga till nytt bolag
if st.button("➕ Lägg till nytt bolag"):
    reset_form()

# Lista på alla bolag sorterade
company_names = sorted(st.session_state.companies.keys())

# Välj ett bolag att visa/redigera
selected = st.selectbox("📂 Välj ett bolag", [""] + company_names)
if selected:
    st.session_state.selected_company = selected
    data = st.session_state.companies[selected]
    for i in range(5):
        st.session_state[f"pe_{i+1}"] = data["pe"][i]
        st.session_state[f"ps_{i+1}"] = data["ps"][i]
    st.session_state["Förväntad vinst i år"] = data["earnings_this_year"]
    st.session_state["Förväntad vinst nästa år"] = data["earnings_next_year"]
    st.session_state["Omsättningstillväxt i år (%)"] = data["growth_this_year"]
    st.session_state["Omsättningstillväxt nästa år (%)"] = data["growth_next_year"]
    st.session_state["Nuvarande kurs"] = data["current_price"]
    st.session_state["Bolagsnamn"] = selected

# Formulär
with st.form("company_form"):
    name = st.text_input("Bolagsnamn", value=st.session_state.get("Bolagsnamn", ""))
    cols = st.columns(5)
    pe_values = [cols[i].number_input(f"P/E {i+1}", min_value=0.0, step=0.1,
                                      value=st.session_state.get(f"pe_{i+1}", 0.0),
                                      key=f"pe_{i+1}") for i in range(5)]
    cols = st.columns(5)
    ps_values = [cols[i].number_input(f"P/S {i+1}", min_value=0.0, step=0.1,
                                      value=st.session_state.get(f"ps_{i+1}", 0.0),
                                      key=f"ps_{i+1}") for i in range(5)]

    earnings_this_year = st.number_input("Förväntad vinst i år", value=st.session_state.get("Förväntad vinst i år", 0.0))
    earnings_next_year = st.number_input("Förväntad vinst nästa år", value=st.session_state.get("Förväntad vinst nästa år", 0.0))
    growth_this_year = st.number_input("Omsättningstillväxt i år (%)", value=st.session_state.get("Omsättningstillväxt i år (%)", 0.0))
    growth_next_year = st.number_input("Omsättningstillväxt nästa år (%)", value=st.session_state.get("Omsättningstillväxt nästa år (%)", 0.0))
    current_price = st.number_input("Nuvarande kurs", value=st.session_state.get("Nuvarande kurs", 0.0))

    submitted = st.form_submit_button("💾 Spara bolag")

    if submitted and name:
        st.session_state.companies[name] = {
            "pe": pe_values,
            "ps": ps_values,
            "earnings_this_year": earnings_this_year,
            "earnings_next_year": earnings_next_year,
            "growth_this_year": growth_this_year,
            "growth_next_year": growth_next_year,
            "current_price": current_price
        }
        save_data()
        st.success(f"{name} sparades!")
        reset_form()

# Radera bolag
if st.session_state.get("selected_company"):
    if st.button("🗑️ Radera bolag"):
        del st.session_state.companies[st.session_state.selected_company]
        save_data()
        st.success("Bolag raderat.")
        reset_form()

# 🔍 Filtrera undervärderade
with st.expander("📉 Filtrera undervärderade bolag"):
    undervalued_filter = st.selectbox("Visa bolag som är undervärderade med:", 
                                      ["Visa alla", "30–39,99%", "40% eller mer"])
    filtered = []
    for name, data in st.session_state.companies.items():
        avg_pe = sum(data["pe"]) / len(data["pe"])
        avg_ps = sum(data["ps"]) / len(data["ps"])
        est_earnings = data["earnings_next_year"]
        est_growth = 1 + data["growth_next_year"] / 100
        est_sales = est_growth
        target_price_pe = est_earnings * avg_pe
        target_price_ps = est_sales * avg_ps  # förenklad
        fair_price = (target_price_pe + target_price_ps) / 2
        undervaluation = (fair_price - data["current_price"]) / data["current_price"]

        if undervalued_filter == "30–39,99%" and 0.3 <= undervaluation < 0.4:
            filtered.append(name)
        elif undervalued_filter == "40% eller mer" and undervaluation >= 0.4:
            filtered.append(name)
        elif undervalued_filter == "Visa alla" and undervaluation > 0:
            filtered.append(name)

    if filtered:
        st.selectbox("📜 Bolag i urvalet", sorted(filtered))
    else:
        st.write("Inga bolag matchar filtret.")

# 📈 Visa analys
st.subheader("📊 Analys av valt bolag")
if st.session_state.get("selected_company"):
    data = st.session_state.companies[st.session_state.selected_company]
    avg_pe = sum(data["pe"]) / len(data["pe"])
    avg_ps = sum(data["ps"]) / len(data["ps"])
    est_earnings = data["earnings_next_year"]
    est_growth = 1 + data["growth_next_year"] / 100
    est_sales = est_growth
    target_price_pe = est_earnings * avg_pe
    target_price_ps = est_sales * avg_ps
    target_price = (target_price_pe + target_price_ps) / 2

    current_price = data["current_price"]
    undervaluation = (target_price - current_price) / current_price
    margin_30 = target_price * 0.7
    margin_40 = target_price * 0.6

    st.markdown(f"""
    **Targetkurs:** `{target_price:.2f} SEK`  
    **Nuvarande kurs:** `{current_price:.2f} SEK`  
    **Undervärdering:** `{undervaluation * 100:.1f}%`  
    **Köp om du vill ha 30% marginal:** `{margin_30:.2f} SEK`  
    **Köp om du vill ha 40% marginal:** `{margin_40:.2f} SEK`
    """)

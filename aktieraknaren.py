import streamlit as st
import pandas as pd
import os

# Filnamn för databas
DATA_FILE = "bolag_data.csv"

# Ladda eller initiera databas
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
            "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
            "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
            "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Apptitel
st.title("📊 Aktieräknaren")

# Ladda data
df = load_data()

# Filter högst upp
st.sidebar.header("🔍 Filtrera undervärderade bolag")
filter_option = st.sidebar.selectbox("Välj filter", ["Alla", "Undervärderade 30–39,99%", "Undervärderade ≥40%"])

# Välj bolag i rullista
selected_company = st.selectbox("Välj bolag att visa eller redigera", [""] + sorted(df["Bolagsnamn"].unique()))

# Lägg till nytt bolag-knapp
if st.button("➕ Lägg till nytt bolag"):
    selected_company = ""

# Formulär
st.subheader("📥 Fyll i eller redigera nyckeltal")
with st.form("company_form"):
    namn = st.text_input("Bolagsnamn", "" if selected_company == "" else selected_company)
    kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company]["Nuvarande kurs"].values[0]))
    vinst_i_ar = st.number_input("Vinst i år", min_value=0.0, format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company]["Vinst i år"].values[0]))
    vinst_next = st.number_input("Vinst nästa år", min_value=0.0, format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company]["Vinst nästa år"].values[0]))
    oms_i_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company]["Omsättningstillväxt i år"].values[0]))
    oms_next = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company]["Omsättningstillväxt nästa år"].values[0]))

    pe_values = []
    for i in range(1, 6):
        key = f"P/E {i}"
        val = st.number_input(key, min_value=0.0, format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company][key].values[0]))
        pe_values.append(val)

    ps_values = []
    for i in range(1, 6):
        key = f"P/S {i}"
        val = st.number_input(key, min_value=0.0, format="%.2f", value=0.0 if selected_company == "" else float(df[df["Bolagsnamn"] == selected_company][key].values[0]))
        ps_values.append(val)

    submitted = st.form_submit_button("💾 Spara bolaget")

# Spara bolaget
if submitted:
    if namn.strip() == "" or kurs <= 0 or vinst_next <= 0:
        st.error("Fyll i alla obligatoriska fält med giltiga värden.")
    else:
        new_data = {
            "Bolagsnamn": namn,
            "Nuvarande kurs": kurs,
            "Vinst i år": vinst_i_ar,
            "Vinst nästa år": vinst_next,
            "Omsättningstillväxt i år": oms_i_ar,
            "Omsättningstillväxt nästa år": oms_next,
        }
        for i in range(5):
            new_data[f"P/E {i+1}"] = pe_values[i]
            new_data[f"P/S {i+1}"] = ps_values[i]

        df = df[df["Bolagsnamn"] != namn]
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        save_data(df)
        st.success("Bolaget har sparats.")

# Visa analys för valt bolag
if selected_company and selected_company in df["Bolagsnamn"].values:
    selected = df[df["Bolagsnamn"] == selected_company].iloc[0]
    avg_pe = sum([selected[f"P/E {i+1}"] for i in range(5)]) / 5
    avg_ps = sum([selected[f"P/S {i+1}"] for i in range(5)]) / 5
    future_profit = selected["Vinst nästa år"]
    growth_factor = 1 + selected["Omsättningstillväxt nästa år"] / 100
    target_price_pe = avg_pe * future_profit
    target_price_ps = avg_ps * future_profit * growth_factor
    target_price = (target_price_pe + target_price_ps) / 2
    undervaluation = ((target_price - selected["Nuvarande kurs"]) / selected["Nuvarande kurs"]) * 100
    buy_at_30 = target_price * 0.70
    buy_at_40 = target_price * 0.60

    st.subheader("📈 Analys")
    st.markdown(f"**Targetkurs:** {target_price:.2f} kr")
    st.markdown(f"**Undervärdering:** :{'green' if undervaluation > 0 else 'red'}[{'{:.2f}'.format(undervaluation)}%]")
    st.markdown(f"**Köpkurs (30% marginal):** {buy_at_30:.2f} kr")
    st.markdown(f"**Köpkurs (40% marginal):** {buy_at_40:.2f} kr")

    if st.button("🗑 Ta bort bolaget"):
        df = df[df["Bolagsnamn"] != selected_company]
        save_data(df)
        st.success("Bolaget har tagits bort.")

# Filtrering
if filter_option != "Alla":
    st.subheader("📂 Filtrerade bolag")
    results = []
    for _, row in df.iterrows():
        avg_pe = sum([row[f"P/E {i+1}"] for i in range(5)]) / 5
        avg_ps = sum([row[f"P/S {i+1}"] for i in range(5)]) / 5
        future_profit = row["Vinst nästa år"]
        growth_factor = 1 + row["Omsättningstillväxt nästa år"] / 100
        target_price = ((avg_pe * future_profit) + (avg_ps * future_profit * growth_factor)) / 2
        undervaluation = ((target_price - row["Nuvarande kurs"]) / row["Nuvarande kurs"]) * 100
        if (filter_option == "Undervärderade 30–39,99%" and 30 <= undervaluation < 40) or \
           (filter_option == "Undervärderade ≥40%" and undervaluation >= 40):
            results.append((row["Bolagsnamn"], undervaluation))
    for namn, uv in results:
        st.write(f"{namn}: {uv:.2f}% undervärdering")

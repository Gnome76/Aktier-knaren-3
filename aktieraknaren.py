import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Nuvarande kurs", 
            "Vinst i år", "Vinst nästa år", 
            "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
            "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
            "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
        ])

def save_data(df):
    df = df.sort_values("Bolagsnamn")
    df.to_csv(DATA_FILE, index=False)

def calculate_target_price(row):
    try:
        pe_list = [float(row[f"P/E {i}"]) for i in range(1, 6)]
        ps_list = [float(row[f"P/S {i}"]) for i in range(1, 6)]
        avg_pe = sum(pe_list) / len(pe_list)
        avg_ps = sum(ps_list) / len(ps_list)

        vinst_next = float(row["Vinst nästa år"])
        oms_tillv_next = float(row["Omsättningstillväxt nästa år"])
        current_price = float(row["Nuvarande kurs"])

        target_pe = vinst_next * avg_pe
        target_ps = current_price * (1 + oms_tillv_next / 100) * (avg_ps)

        target_price = (target_pe + target_ps) / 2

        undervaluation_pct = ((target_price - current_price) / current_price) * 100
        buy_price_30 = target_price * 0.7
        buy_price_40 = target_price * 0.6

        return round(target_price, 2), round(undervaluation_pct, 2), round(buy_price_30, 2), round(buy_price_40, 2)
    except:
        return None, None, None, None

st.title("📊 Aktieräknaren")

st.subheader("📁 Filtrera bolag")
filter_option = st.selectbox("Visa bolag som är undervärderade med:", [
    "Alla bolag", "≥ 30%", "≥ 40%"
])

df = load_data()

bolagslista = df["Bolagsnamn"].tolist()
selected_bolag = st.selectbox("Välj bolag att visa eller redigera:", [""] + bolagslista)

if selected_bolag:
    bolag_data = df[df["Bolagsnamn"] == selected_bolag].iloc[0]
else:
    bolag_data = pd.Series(dtype="object")

st.subheader("📝 Nyckeltal och bolagsdata")

with st.form("input_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        bolagsnamn = st.text_input("Bolagsnamn", value=bolag_data.get("Bolagsnamn", ""))
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=bolag_data.get("Nuvarande kurs", 0.0) if selected_bolag else None)
    with col2:
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f", value=bolag_data.get("Vinst i år", 0.0) if selected_bolag else None)
        oms_i_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f", value=bolag_data.get("Omsättningstillväxt i år", 0.0) if selected_bolag else None)
    with col3:
        vinst_next = st.number_input("Vinst nästa år", format="%.2f", value=bolag_data.get("Vinst nästa år", 0.0) if selected_bolag else None)
        oms_next = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f", value=bolag_data.get("Omsättningstillväxt nästa år", 0.0) if selected_bolag else None)

    pe_cols = st.columns(5)
    pe_values = []
    for i in range(5):
        with pe_cols[i]:
            pe_values.append(st.number_input(f"P/E {i+1}", format="%.2f", value=bolag_data.get(f"P/E {i+1}", 0.0) if selected_bolag else None))

    ps_cols = st.columns(5)
    ps_values = []
    for i in range(5):
        with ps_cols[i]:
            ps_values.append(st.number_input(f"P/S {i+1}", format="%.2f", value=bolag_data.get(f"P/S {i+1}", 0.0) if selected_bolag else None))

    submit = st.form_submit_button("Spara bolag")

    if submit:
        new_row = {
            "Bolagsnamn": bolagsnamn,
            "Nuvarande kurs": kurs,
            "Vinst i år": vinst_i_ar,
            "Vinst nästa år": vinst_next,
            "Omsättningstillväxt i år": oms_i_ar,
            "Omsättningstillväxt nästa år": oms_next,
        }
        for i in range(5):
            new_row[f"P/E {i+1}"] = pe_values[i]
            new_row[f"P/S {i+1}"] = ps_values[i]

        df = df[df["Bolagsnamn"] != bolagsnamn]  # Remove old entry if exists
        df = df.append(new_row, ignore_index=True)
        save_data(df)
        st.success(f"{bolagsnamn} har sparats!")

st.button("➕ Lägg till nytt bolag", on_click=lambda: st.experimental_rerun())

st.subheader("📈 Analys")

if filter_option == "≥ 40%":
    df["Target"], df["Undervärdering"], df["Köp 30%"], df["Köp 40%"] = zip(*df.apply(calculate_target_price, axis=1))
    df_filtered = df[df["Undervärdering"] >= 40]
elif filter_option == "≥ 30%":
    df["Target"], df["Undervärdering"], df["Köp 30%"], df["Köp 40%"] = zip(*df.apply(calculate_target_price, axis=1))
    df_filtered = df[(df["Undervärdering"] >= 30)]
else:
    df["Target"], df["Undervärdering"], df["Köp 30%"], df["Köp 40%"] = zip(*df.apply(calculate_target_price, axis=1))
    df_filtered = df

st.dataframe(df_filtered[[
    "Bolagsnamn", "Nuvarande kurs", "Target", 
    "Undervärdering", "Köp 30%", "Köp 40%"
]])

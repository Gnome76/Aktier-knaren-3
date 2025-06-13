import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.csv"

# Ladda data
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

# Spara data
def save_data(df):
    df = df.sort_values("Bolagsnamn")
    df.to_csv(DATA_FILE, index=False)

# Beräkna riktkurs
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
        target_ps = current_price * (1 + oms_tillv_next / 100) * avg_ps

        target_price = (target_pe + target_ps) / 2
        undervaluation_pct = ((target_price - current_price) / current_price) * 100
        buy_price_30 = target_price * 0.7
        buy_price_40 = target_price * 0.6

        return round(target_price, 2), round(undervaluation_pct, 2), round(buy_price_30, 2), round(buy_price_40, 2)
    except:
        return None, None, None, None

# Start
st.set_page_config(page_title="Aktieräknaren", layout="wide")
st.title("📊 Aktieräknaren – Aktieanalys med riktkurs")

# Filtrering
st.subheader("🔎 Filtrera undervärderade bolag")
filter_option = st.selectbox("Visa:", ["Alla bolag", "≥ 30% undervärderade", "≥ 40% undervärderade"])

df = load_data()
df[["Target", "Undervärdering", "Köp 30%", "Köp 40%"]] = df.apply(calculate_target_price, axis=1, result_type='expand')

if filter_option == "≥ 40% undervärderade":
    df_filtered = df[df["Undervärdering"] >= 40]
elif filter_option == "≥ 30% undervärderade":
    df_filtered = df[df["Undervärdering"] >= 30]
else:
    df_filtered = df

selected_bolag = st.selectbox("📂 Välj bolag:", [""] + df["Bolagsnamn"].tolist())

# Visa nyckeltalsformulär
st.subheader("📋 Lägg till eller redigera bolag")
with st.form("bolagsformulär", clear_on_submit=False):
    colA, colB = st.columns(2)
    with colA:
        bolagsnamn = st.text_input("Bolagsnamn", value=df.loc[df["Bolagsnamn"] == selected_bolag, "Bolagsnamn"].values[0] if selected_bolag else "")
        kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=float(df.loc[df["Bolagsnamn"] == selected_bolag, "Nuvarande kurs"].values[0]) if selected_bolag else 0.0)
        vinst_i_ar = st.number_input("Vinst i år", format="%.2f", value=float(df.loc[df["Bolagsnamn"] == selected_bolag, "Vinst i år"].values[0]) if selected_bolag else 0.0)
        vinst_next = st.number_input("Vinst nästa år", format="%.2f", value=float(df.loc[df["Bolagsnamn"] == selected_bolag, "Vinst nästa år"].values[0]) if selected_bolag else 0.0)
    with colB:
        oms_i_ar = st.number_input("Omsättningstillväxt i år (%)", format="%.2f", value=float(df.loc[df["Bolagsnamn"] == selected_bolag, "Omsättningstillväxt i år"].values[0]) if selected_bolag else 0.0)
        oms_next = st.number_input("Omsättningstillväxt nästa år (%)", format="%.2f", value=float(df.loc[df["Bolagsnamn"] == selected_bolag, "Omsättningstillväxt nästa år"].values[0]) if selected_bolag else 0.0)

    pe_cols = st.columns(5)
    pe_values = []
    for i in range(5):
        with pe_cols[i]:
            val = df.loc[df["Bolagsnamn"] == selected_bolag, f"P/E {i+1}"].values[0] if selected_bolag else 0.0
            pe_values.append(st.number_input(f"P/E {i+1}", format="%.2f", value=float(val)))

    ps_cols = st.columns(5)
    ps_values = []
    for i in range(5):
        with ps_cols[i]:
            val = df.loc[df["Bolagsnamn"] == selected_bolag, f"P/S {i+1}"].values[0] if selected_bolag else 0.0
            ps_values.append(st.number_input(f"P/S {i+1}", format="%.2f", value=float(val)))

    submitted = st.form_submit_button("💾 Spara bolag")

    if submitted:
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

        df = df[df["Bolagsnamn"] != bolagsnamn]  # Remove old
        df = df.append(new_row, ignore_index=True)
        save_data(df)
        st.success(f"✅ {bolagsnamn} har sparats.")
        st.experimental_rerun()

if st.button("➕ Lägg till nytt bolag"):
    st.experimental_rerun()

# Visa analys
st.subheader("📈 Analys och riktkurser")
if not df_filtered.empty:
    st.dataframe(df_filtered[[
        "Bolagsnamn", "Nuvarande kurs", "Target", "Undervärdering", "Köp 30%", "Köp 40%"
    ]])
else:
    st.info("Inga bolag matchar filtreringen.")

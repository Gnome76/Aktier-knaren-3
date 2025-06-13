import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.csv"

# Starta CSV om den inte finns
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs",
        "P/E 1", "P/E 2", "P/E 3", "P/E 4",
        "P/S 1", "P/S 2", "P/S 3", "P/S 4",
        "Vinst i år", "Vinst nästa år",
        "Omsättningstillväxt i år", "Omsättningstillväxt nästa år"
    ])
    df.to_csv(DATA_FILE, index=False)

# Läs CSV
df = pd.read_csv(DATA_FILE)

st.title("Aktieräknaren – Enkel version")

st.subheader("📥 Lägg till nytt bolag")

with st.form("add_bolag"):
    bolagsnamn = st.text_input("Bolagsnamn")
    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f")

    pe_values = [st.number_input(f"P/E {i+1}", min_value=0.0, format="%.2f", key=f"pe_{i}") for i in range(4)]
    ps_values = [st.number_input(f"P/S {i+1}", min_value=0.0, format="%.2f", key=f"ps_{i}") for i in range(4)]

    vinst_i_ar = st.number_input("Vinst i år", min_value=0.0, format="%.2f")
    vinst_next = st.number_input("Vinst nästa år", min_value=0.0, format="%.2f")

    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", min_value=0.0, format="%.2f")
    oms_tillv_next = st.number_input("Omsättningstillväxt nästa år (%)", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Spara bolag")

    if submitted:
        new_row = pd.DataFrame([[
            bolagsnamn, nuvarande_kurs,
            *pe_values, *ps_values,
            vinst_i_ar, vinst_next,
            oms_tillv_i_ar, oms_tillv_next
        ]], columns=df.columns)

        df = pd.concat([df, new_row], ignore_index=True)
        df = df.sort_values("Bolagsnamn").reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"{bolagsnamn} har sparats.")

st.divider()
st.subheader("📊 Analys av bolag")

def calc_target_and_diff(row):
    snitt_pe = sum([row[f"P/E {i+1}"] for i in range(4)]) / 4
    snitt_ps = sum([row[f"P/S {i+1}"] for i in range(4)]) / 4

    snitt_vinst = (row["Vinst i år"] + row["Vinst nästa år"]) / 2
    snitt_oms_tillv = (row["Omsättningstillväxt i år"] + row["Omsättningstillväxt nästa år"]) / 2 / 100

    target_pe = snitt_pe * snitt_vinst
    omsättning = row["Vinst i år"] / 0.1  # Anta 10% marginal (förenklad)
    framtida_omsättning = omsättning * (1 + snitt_oms_tillv)
    target_ps = snitt_ps * framtida_omsättning

    target_avg = (target_pe + target_ps) / 2

    diff_pct = (target_avg - row["Nuvarande kurs"]) / row["Nuvarande kurs"] * 100

    return pd.Series([target_pe, target_ps, target_avg, diff_pct])

if not df.empty:
    df[["Target PE", "Target PS", "Target Snitt", "Undervärdering (%)"]] = df.apply(calc_target_and_diff, axis=1)

    filter_option = st.selectbox(
        "Visa bolag med undervärdering:",
        ["Alla", "Minst 30%", "Minst 40%"]
    )

    filtered = df.copy()
    if filter_option == "Minst 30%":
        filtered = filtered[filtered["Undervärdering (%)"] >= 30]
    elif filter_option == "Minst 40%":
        filtered = filtered[filtered["Undervärdering (%)"] >= 40]

    if not filtered.empty:
        filtered = filtered.sort_values("Undervärdering (%)", ascending=False)
        st.dataframe(filtered[[
            "Bolagsnamn", "Nuvarande kurs",
            "Target PE", "Target PS", "Target Snitt",
            "Undervärdering (%)"
        ]], use_container_width=True)
    else:
        st.info("Inga bolag matchar filtret.")
else:
    st.info("Inga bolag har ännu lagts till.")

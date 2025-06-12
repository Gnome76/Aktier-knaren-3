import streamlit as st
import pandas as pd
import os

# --- Initiera databas ---
DATA_FILE = "bolag_data.xlsx"
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande Kurs", 
        "PE_1", "PE_2", "PE_3", "PE_4", "PE_5",
        "PS_1", "PS_2", "PS_3", "PS_4", "PS_5",
        "Vinst_i_år", "Vinst_nästa_år",
        "Omsättningstillväxt_i_år", "Omsättningstillväxt_nästa_år"
    ])

st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("📊 Aktieräknaren")

# --- Filtrering högst upp ---
st.subheader("🔍 Filtrering")
filter_option = st.selectbox("Filtrera efter värdering", [
    "Visa alla bolag",
    "Undervärderade 30–39,99%",
    "Undervärderade ≥ 40%"
])

# --- Rullista för bolag ---
saved_names = sorted(df["Bolagsnamn"].unique())
selected_name = st.selectbox("📂 Välj bolag att visa/redigera", [""] + list(saved_names))

if selected_name:
    selected_row = df[df["Bolagsnamn"] == selected_name].iloc[0]
else:
    selected_row = pd.Series(dtype="float64")

# --- Formulär för nyckeltal ---
st.subheader("🧾 Bolagsdata")
with st.form(key="form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        bolagsnamn = st.text_input("Bolagsnamn", value=selected_row.get("Bolagsnamn", ""))
    with col2:
        kurs = st.number_input("Nuvarande kurs", step=0.01, value=selected_row.get("Nuvarande Kurs", 0.0))

    st.markdown("##### P/E-tal (5 år)")
    pe = []
    cols = st.columns(5)
    for i in range(5):
        pe_val = cols[i].number_input(f"P/E {i+1}", step=0.01, key=f"pe{i}", value=selected_row.get(f"PE_{i+1}", 0.0))
        pe.append(pe_val)

    st.markdown("##### P/S-tal (5 år)")
    ps = []
    cols = st.columns(5)
    for i in range(5):
        ps_val = cols[i].number_input(f"P/S {i+1}", step=0.01, key=f"ps{i}", value=selected_row.get(f"PS_{i+1}", 0.0))
        ps.append(ps_val)

    col_v1, col_v2 = st.columns(2)
    vinst_i_år = col_v1.number_input("Vinst i år", step=0.01, value=selected_row.get("Vinst_i_år", 0.0))
    vinst_nästa_år = col_v2.number_input("Vinst nästa år", step=0.01, value=selected_row.get("Vinst_nästa_år", 0.0))

    col_o1, col_o2 = st.columns(2)
    oms_v1 = col_o1.number_input("Omsättningstillväxt i år (%)", step=0.01, value=selected_row.get("Omsättningstillväxt_i_år", 0.0))
    oms_v2 = col_o2.number_input("Omsättningstillväxt nästa år (%)", step=0.01, value=selected_row.get("Omsättningstillväxt_nästa_år", 0.0))

    submit = st.form_submit_button("💾 Spara bolag")

# --- Spara logik ---
if submit:
    if bolagsnamn and kurs > 0 and all(pe) and all(ps) and vinst_i_år > 0 and vinst_nästa_år > 0:
        ny_rad = {
            "Bolagsnamn": bolagsnamn,
            "Nuvarande Kurs": kurs,
            "Vinst_i_år": vinst_i_år,
            "Vinst_nästa_år": vinst_nästa_år,
            "Omsättningstillväxt_i_år": oms_v1,
            "Omsättningstillväxt_nästa_år": oms_v2
        }
        for i in range(5):
            ny_rad[f"PE_{i+1}"] = pe[i]
            ny_rad[f"PS_{i+1}"] = ps[i]

        df = df[df["Bolagsnamn"] != bolagsnamn]
        df = pd.concat([df, pd.DataFrame([ny_rad])], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Bolaget sparades!")
        st.experimental_rerun()
    else:
        st.error("❌ Alla fält måste fyllas i korrekt!")

# --- Lägg till nytt bolag ---
if st.button("➕ Lägg till nytt bolag"):
    st.experimental_rerun()

# --- Ta bort bolag ---
if selected_name and st.button("🗑️ Radera bolag"):
    df = df[df["Bolagsnamn"] != selected_name]
    df.to_excel(DATA_FILE, index=False)
    st.success("Bolag raderat!")
    st.experimental_rerun()

# --- Beräkning & analys ---
if selected_name:
    avg_pe = sum([selected_row[f"PE_{i+1}"] for i in range(5)]) / 5
    avg_ps = sum([selected_row[f"PS_{i+1}"] for i in range(5)]) / 5

    vinst_kommande = (selected_row["Vinst_i_år"] + selected_row["Vinst_nästa_år"]) / 2
    tillväxt_faktor = (1 + (selected_row["Omsättningstillväxt_i_år"] + selected_row["Omsättningstillväxt_nästa_år"]) / 200)

    target_pe = avg_pe * vinst_kommande * tillväxt_faktor
    target_ps = avg_ps * vinst_kommande * tillväxt_faktor
    targetkurs = round((target_pe + target_ps) / 2, 2)

    kurs = selected_row["Nuvarande Kurs"]
    diff = (targetkurs - kurs) / kurs * 100
    undervärderad = diff >= 0

    color = "green" if diff >= 40 else "orange" if 30 <= diff < 40 else "red"

    st.markdown(f"### 🎯 Targetkurs: **{targetkurs:.2f} kr**")
    st.markdown(f"**Nuvarande kurs:** {kurs:.2f} kr")
    st.markdown(f"**Undervärdering:** `{diff:.2f}%`", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color}; font-weight:bold'>{'Undervärderad' if undervärderad else 'Övervärderad'}</span>", unsafe_allow_html=True)

    st.info(f"📉 Köp vid 30% marginal: **{targetkurs * 0.7:.2f} kr**")
    st.info(f"📉 Köp vid 40% marginal: **{targetkurs * 0.6:.2f} kr**")

# --- Export till Excel ---
if st.button("⬇️ Ladda ner databasen som Excel"):
    df.to_excel("aktiedata_export.xlsx", index=False)
    with open("aktiedata_export.xlsx", "rb") as f:
        st.download_button("📥 Klicka här för att ladda ner", f, file_name="aktiedata_export.xlsx")

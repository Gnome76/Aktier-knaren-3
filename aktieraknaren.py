import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Aktieräknaren", layout="centered")

# Filnamn till CSV
DATAFIL = "bolag_data.csv"

# Ladda eller skapa data
if os.path.exists(DATAFIL):
    df = pd.read_csv(DATAFIL)
else:
    df = pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
        "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
        "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
        "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
    ])

st.title("📈 Aktieräknaren")

# Filter högst upp
st.subheader("🔍 Filtrera bolag")
filter_option = st.selectbox("Välj filter:", ["Visa alla", "Undervärderade 30–39.99%", "Undervärderade ≥ 40%"])

# Välj bolag
bolagslista = sorted(df["Bolagsnamn"].unique())
valt_bolag = st.selectbox("Välj ett sparat bolag:", [""] + bolagslista)

if valt_bolag:
    data = df[df["Bolagsnamn"] == valt_bolag].iloc[0].to_dict()
else:
    data = {col: "" for col in df.columns}

# Formulär för att lägga till/uppdatera bolag
st.subheader("✏️ Ange nyckeltal och info")

col1, col2, col3 = st.columns(3)
with col1:
    namn = st.text_input("Bolagsnamn", value=data["Bolagsnamn"])
with col2:
    kurs = st.number_input("Nuvarande kurs", min_value=0.0, step=0.01, value=float(data["Nuvarande kurs"]) if data["Nuvarande kurs"] else 0.0)
with col3:
    vinst_1 = st.number_input("Vinst i år", step=0.01, value=float(data["Vinst i år"]) if data["Vinst i år"] else 0.0)

col4, col5, col6 = st.columns(3)
with col4:
    vinst_2 = st.number_input("Vinst nästa år", step=0.01, value=float(data["Vinst nästa år"]) if data["Vinst nästa år"] else 0.0)
with col5:
    oms_1 = st.number_input("Omsättningstillväxt i år (%)", step=0.1, value=float(data["Omsättningstillväxt i år"]) if data["Omsättningstillväxt i år"] else 0.0)
with col6:
    oms_2 = st.number_input("Omsättningstillväxt nästa år (%)", step=0.1, value=float(data["Omsättningstillväxt nästa år"]) if data["Omsättningstillväxt nästa år"] else 0.0)

st.markdown("### 📊 P/E-tal (historik)")
pe_cols = st.columns(5)
pe_values = []
for i in range(5):
    with pe_cols[i]:
        pe = st.number_input(f"P/E {i+1}", step=0.1, value=float(data[f"P/E {i+1}"]) if data[f"P/E {i+1}"] else 0.0)
        pe_values.append(pe)

st.markdown("### 💹 P/S-tal (historik)")
ps_cols = st.columns(5)
ps_values = []
for i in range(5):
    with ps_cols[i]:
        ps = st.number_input(f"P/S {i+1}", step=0.1, value=float(data[f"P/S {i+1}"]) if data[f"P/S {i+1}"] else 0.0)
        ps_values.append(ps)

# Beräkna targetkurs
if vinst_2 > 0:
    pe_snitt = sum(pe_values) / len(pe_values)
    ps_snitt = sum(ps_values) / len(ps_values)

    pe_target = pe_snitt * vinst_2
    oms_tillv = 1 + (oms_1 + oms_2) / 200
    ps_target = ps_snitt * vinst_2 * oms_tillv

    target = round((pe_target + ps_target) / 2, 2)

    undervardering = round(((target - kurs) / target) * 100, 2)
    färg = "🟩" if undervardering >= 0 else "🟥"

    st.subheader("📈 Analys")
    st.markdown(f"""
    **Targetkurs:** {target} kr  
    **Undervärdering:** {färg} {undervardering}%  
    **Köp vid (30% marginal):** {round(target * 0.7, 2)} kr  
    **Köp vid (40% marginal):** {round(target * 0.6, 2)} kr
    """)
else:
    st.warning("⚠️ Fyll i Vinst nästa år för att kunna räkna ut targetkurs.")

# Knappar
col_save, col_new, col_delete = st.columns(3)
with col_save:
    if st.button("💾 Spara bolag"):
        if not namn:
            st.error("Bolagsnamn måste anges.")
        else:
            ny_rad = {
                "Bolagsnamn": namn, "Nuvarande kurs": kurs, "Vinst i år": vinst_1, "Vinst nästa år": vinst_2,
                "Omsättningstillväxt i år": oms_1, "Omsättningstillväxt nästa år": oms_2,
            }
            for i in range(5):
                ny_rad[f"P/E {i+1}"] = pe_values[i]
                ny_rad[f"P/S {i+1}"] = ps_values[i]

            df = df[df["Bolagsnamn"] != namn]
            df = pd.concat([df, pd.DataFrame([ny_rad])])
            df = df.sort_values("Bolagsnamn")
            df.to_csv(DATAFIL, index=False)
            st.success("✅ Bolag sparat!")

with col_new:
    if st.button("➕ Lägg till nytt bolag"):
        st.experimental_rerun()

with col_delete:
    if valt_bolag and st.button("🗑️ Ta bort valt bolag"):
        df = df[df["Bolagsnamn"] != valt_bolag]
        df.to_csv(DATAFIL, index=False)
        st.success("🚮 Bolaget har tagits bort.")
        st.experimental_rerun()

# Visa filtrerade bolag
st.subheader("📃 Sparade bolag")

if filter_option == "Undervärderade 30–39.99%":
    visning = df.copy()
    visning["Targetkurs"] = (visning[[f"P/E {i+1}" for i in range(5)]].mean(axis=1) * visning["Vinst nästa år"] +
                             visning[[f"P/S {i+1}" for i in range(5)]].mean(axis=1) *
                             visning["Vinst nästa år"] *
                             (1 + (visning["Omsättningstillväxt i år"] + visning["Omsättningstillväxt nästa år"]) / 200)) / 2
    visning["Undervärdering"] = ((visning["Targetkurs"] - visning["Nuvarande kurs"]) / visning["Targetkurs"]) * 100
    visning = visning[(visning["Undervärdering"] >= 30) & (visning["Undervärdering"] < 40)]
elif filter_option == "Undervärderade ≥ 40%":
    visning = df.copy()
    visning["Targetkurs"] = (visning[[f"P/E {i+1}" for i in range(5)]].mean(axis=1) * visning["Vinst nästa år"] +
                             visning[[f"P/S {i+1}" for i in range(5)]].mean(axis=1) *
                             visning["Vinst nästa år"] *
                             (1 + (visning["Omsättningstillväxt i år"] + visning["Omsättningstillväxt nästa år"]) / 200)) / 2
    visning["Undervärdering"] = ((visning["Targetkurs"] - visning["Nuvarande kurs"]) / visning["Targetkurs"]) * 100
    visning = visning[visning["Undervärdering"] >= 40]
else:
    visning = df

if not visning.empty:
    st.dataframe(visning[["Bolagsnamn", "Nuvarande kurs"]])
else:
    st.info("Ingen data att visa.")

# Ladda ner som Excel
st.download_button("📥 Ladda ner som CSV", data=df.to_csv(index=False), file_name="aktier.csv", mime="text/csv")

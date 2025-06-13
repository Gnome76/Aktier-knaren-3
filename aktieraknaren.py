import streamlit as st
import pandas as pd
import os

# Filnamn där bolagen sparas
DATA_FILE = "bolag_data.xlsx"

# Hjälpfunktioner
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
            "Omsättning i år", "Omsättning nästa år",
            "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
            "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
        ])

def save_data(df):
    df = df.sort_values(by="Bolagsnamn")
    df.to_excel(DATA_FILE, index=False)

def beräkna_targetkurs(vinst_next, omsättning_next, pe_list, ps_list):
    pe_snitt = sum(pe_list) / len(pe_list)
    ps_snitt = sum(ps_list) / len(ps_list)

    target_pe = pe_snitt * vinst_next
    target_ps = ps_snitt * omsättning_next

    return round((target_pe + target_ps) / 2, 2)

def visa_analys(target, nuvarande_kurs):
    undervärdering = ((target - nuvarande_kurs) / nuvarande_kurs) * 100
    undervärdering = round(undervärdering, 2)

    kurs_30 = round(target * 0.7, 2)
    kurs_40 = round(target * 0.6, 2)

    status = "📉 Undervärderad" if undervärdering > 0 else "📈 Övervärderad"
    färg = "green" if undervärdering > 0 else "red"

    st.markdown(f"### 📊 **Analys**")
    st.markdown(f"<span style='color:{färg}'>**{status} med {undervärdering}%**</span>", unsafe_allow_html=True)
    st.markdown(f"🎯 **Targetkurs:** {target} kr")
    st.markdown(f"💰 **Kursnivå för 30% marginal:** {kurs_30} kr")
    st.markdown(f"💰 **Kursnivå för 40% marginal:** {kurs_40} kr")

    return undervärdering

# ⬆️ UI START
st.title("📈 Aktieräknaren")

# Läs in data
df = load_data()
selected_filter = st.selectbox("🔍 Filtrera bolag", ["Alla", "Undervärderade 30–39,99%", "Undervärderade 40%+"])
filtrerat_df = df.copy()

# Filtrering
if selected_filter == "Undervärderade 30–39,99%":
    filtrerat_df["Targetkurs"] = df.apply(
        lambda row: beräkna_targetkurs(
            row["Vinst nästa år"], row["Omsättning nästa år"],
            [row[f"P/E {i}"] for i in range(1, 6)],
            [row[f"P/S {i}"] for i in range(1, 6)]
        ), axis=1
    )
    filtrerat_df["Undervärdering"] = ((filtrerat_df["Targetkurs"] - df["Nuvarande kurs"]) / df["Nuvarande kurs"]) * 100
    filtrerat_df = filtrerat_df[(filtrerat_df["Undervärdering"] >= 30) & (filtrerat_df["Undervärdering"] < 40)]

elif selected_filter == "Undervärderade 40%+":
    filtrerat_df["Targetkurs"] = df.apply(
        lambda row: beräkna_targetkurs(
            row["Vinst nästa år"], row["Omsättning nästa år"],
            [row[f"P/E {i}"] for i in range(1, 6)],
            [row[f"P/S {i}"] for i in range(1, 6)]
        ), axis=1
    )
    filtrerat_df["Undervärdering"] = ((filtrerat_df["Targetkurs"] - df["Nuvarande kurs"]) / df["Nuvarande kurs"]) * 100
    filtrerat_df = filtrerat_df[filtrerat_df["Undervärdering"] >= 40]

# Välj bolag
valda_bolag = filtrerat_df["Bolagsnamn"].tolist()
valt_bolag = st.selectbox("📂 Välj bolag att visa eller redigera", [""] + valda_bolag)

if valt_bolag:
    selected = df[df["Bolagsnamn"] == valt_bolag].iloc[0]
else:
    selected = {}

# Formulär
st.subheader("✏️ Lägg till eller redigera bolag")

with st.form("bolagsformulär", clear_on_submit=False):
    bolagsnamn = st.text_input("Bolagsnamn", value=selected.get("Bolagsnamn", "") if selected else "")
    nuvarande_kurs = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=selected.get("Nuvarande kurs", 0.0) if selected else None)
    vinst_i_ar = st.number_input("Vinst i år", format="%.2f", value=selected.get("Vinst i år", 0.0) if selected else None)
    vinst_next = st.number_input("Vinst nästa år", format="%.2f", value=selected.get("Vinst nästa år", 0.0) if selected else None)
    oms_i_ar = st.number_input("Omsättning i år", format="%.2f", value=selected.get("Omsättning i år", 0.0) if selected else None)
    oms_next = st.number_input("Omsättning nästa år", format="%.2f", value=selected.get("Omsättning nästa år", 0.0) if selected else None)

    col1, col2 = st.columns(2)
    with col1:
        pe_values = [st.number_input(f"P/E {i+1}", format="%.2f", value=selected.get(f"P/E {i+1}", 0.0) if selected else None) for i in range(5)]
    with col2:
        ps_values = [st.number_input(f"P/S {i+1}", format="%.2f", value=selected.get(f"P/S {i+1}", 0.0) if selected else None) for i in range(5)]

    submitted = st.form_submit_button("💾 Spara bolag")

    if submitted:
        if not bolagsnamn:
            st.error("❌ Bolagsnamn måste anges.")
        else:
            new_row = {
                "Bolagsnamn": bolagsnamn,
                "Nuvarande kurs": nuvarande_kurs,
                "Vinst i år": vinst_i_ar,
                "Vinst nästa år": vinst_next,
                "Omsättning i år": oms_i_ar,
                "Omsättning nästa år": oms_next,
            }
            for i in range(5):
                new_row[f"P/E {i+1}"] = pe_values[i]
                new_row[f"P/S {i+1}"] = ps_values[i]

            # Uppdatera befintligt bolag eller lägg till nytt
            df = df[df["Bolagsnamn"] != bolagsnamn]
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ Bolag sparat.")

# Analysera om bolag är valt
if valt_bolag:
    targetkurs = beräkna_targetkurs(
        selected["Vinst nästa år"],
        selected["Omsättning nästa år"],
        [selected[f"P/E {i}"] for i in range(1, 6)],
        [selected[f"P/S {i}"] for i in range(1, 6)],
    )
    visa_analys(targetkurs, selected["Nuvarande kurs"])

# Ta bort bolag
if valt_bolag:
    if st.button("🗑️ Ta bort detta bolag"):
        df = df[df["Bolagsnamn"] != valt_bolag]
        save_data(df)
        st.success("❌ Bolag raderat.")

# Export
st.markdown("---")
if not df.empty:
    st.download_button("📤 Ladda ner bolagsdatabas (Excel)", data=df.to_excel(index=False), file_name="bolag_data.xlsx")

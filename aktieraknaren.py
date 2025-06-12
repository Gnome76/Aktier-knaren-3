import streamlit as st
import pandas as pd

st.set_page_config(page_title="Aktieräknaren", layout="wide")

DATA_FILE = "aktier.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Nuvarande Kurs", 
            "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
            "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5",
            "Vinst i år", "Vinst nästa år", 
            "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
            "Targetkurs", "Undervärdering (%)", "Köp vid -30%", "Köp vid -40%"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def beräkna_targetkurs(pe_list, ps_list, vinst_år, vinst_nästa_år, oms_tillv_år, oms_tillv_nästa_år):
    pe_median = pd.Series(pe_list).median()
    ps_median = pd.Series(ps_list).median()
    snitt_vinst = (vinst_år + vinst_nästa_år) / 2
    snitt_omsättningstillväxt = (oms_tillv_år + oms_tillv_nästa_år) / 2

    target_pe = pe_median * snitt_vinst
    target_ps = ps_median * (snitt_vinst * (1 + snitt_omsättningstillväxt / 100))

    return round((target_pe + target_ps) / 2, 2)

df = load_data()

if "new_entry" not in st.session_state:
    st.session_state.new_entry = False

if st.sidebar.button("➕ Lägg till nytt bolag"):
    st.session_state.new_entry = True

selected = None
data = None
if not st.session_state.new_entry and not df.empty:
    selected = st.sidebar.selectbox("Välj ett bolag att visa/redigera", df["Bolagsnamn"].sort_values())
    if selected:
        data = df[df["Bolagsnamn"] == selected].iloc[0]

if selected:
    st.subheader(f"Redigera bolag: {selected}")
else:
    st.subheader("Lägg till nytt bolag")

bolagsnamn = st.text_input("Bolagsnamn", value=data["Bolagsnamn"] if data is not None else "")
kurs = st.number_input("Nuvarande Kurs", value=data["Nuvarande Kurs"] if data is not None else 0.0, step=0.1)

pe_values = [st.number_input(f"P/E {i+1}", value=data[f"P/E {i+1}"] if data is not None else 0.0, step=0.1) for i in range(5)]
ps_values = [st.number_input(f"P/S {i+1}", value=data[f"P/S {i+1}"] if data is not None else 0.0, step=0.1) for i in range(5)]

vinst_år = st.number_input("Vinst i år (kr/aktie)", value=data["Vinst i år"] if data is not None else 0.0, step=0.1)
vinst_nästa_år = st.number_input("Vinst nästa år (kr/aktie)", value=data["Vinst nästa år"] if data is not None else 0.0, step=0.1)
oms_år = st.number_input("Omsättningstillväxt i år (%)", value=data["Omsättningstillväxt i år"] if data is not None else 0.0, step=0.1)
oms_nästa_år = st.number_input("Omsättningstillväxt nästa år (%)", value=data["Omsättningstillväxt nästa år"] if data is not None else 0.0, step=0.1)

if st.button("💾 Spara & Beräkna"):
    target = beräkna_targetkurs(pe_values, ps_values, vinst_år, vinst_nästa_år, oms_år, oms_nästa_år)
    undervärdering = round((1 - kurs / target) * 100, 2)
    köp_30 = round(target * 0.7, 2)
    köp_40 = round(target * 0.6, 2)

    ny_data = {
        "Bolagsnamn": bolagsnamn,
        "Nuvarande Kurs": kurs,
        "Vinst i år": vinst_år,
        "Vinst nästa år": vinst_nästa_år,
        "Omsättningstillväxt i år": oms_år,
        "Omsättningstillväxt nästa år": oms_nästa_år,
        "Targetkurs": target,
        "Undervärdering (%)": undervärdering,
        "Köp vid -30%": köp_30,
        "Köp vid -40%": köp_40,
    }
    for i in range(5):
        ny_data[f"P/E {i+1}"] = pe_values[i]
        ny_data[f"P/S {i+1}"] = ps_values[i]

    df = df[df["Bolagsnamn"] != bolagsnamn]
    df = pd.concat([df, pd.DataFrame([ny_data])], ignore_index=True)
    df = df.sort_values("Bolagsnamn")
    save_data(df)
    st.success(f"{bolagsnamn} sparades!")
    st.session_state.new_entry = False

if not df.empty:
    st.subheader("📊 Sparade bolag")
    filter_option = st.selectbox("Filtrera undervärderade bolag", ["Visa alla", "Undervärderade 30-39,99%", "Undervärderade >40%"])
    if filter_option == "Undervärderade 30-39,99%":
        visning = df[(df["Undervärdering (%)"] >= 30) & (df["Undervärdering (%)"] < 40)]
    elif filter_option == "Undervärderade >40%":
        visning = df[df["Undervärdering (%)"] >= 40]
    else:
        visning = df

    bolag_lista = visning["Bolagsnamn"].tolist()
    valt_bolag = st.selectbox("Välj bolag för att visa nyckeltal", bolag_lista)
    if valt_bolag:
        st.dataframe(visning[visning["Bolagsnamn"] == valt_bolag])

    if selected:
        if st.button("🗑 Ta bort bolaget"):
            df = df[df["Bolagsnamn"] != selected]
            save_data(df)
            st.success(f"{selected} togs bort.")

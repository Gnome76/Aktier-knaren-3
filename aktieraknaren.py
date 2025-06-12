import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("📈 Aktieräknaren")

DATA_FILE = "bolag_data.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
        "Oms tillväxt i år", "Oms tillväxt nästa år",
        "PE1", "PE2", "PE3", "PE4", "PE5",
        "PS1", "PS2", "PS3", "PS4", "PS5"
    ])

st.sidebar.header("📁 Sparade bolag")
new_entry = st.sidebar.button("➕ Lägg till nytt bolag")

if new_entry:
    selected = None
    data = None
elif not df.empty:
    selected = st.sidebar.selectbox("Välj bolag att visa eller redigera", sorted(df["Bolagsnamn"]))
    data = df[df["Bolagsnamn"] == selected].iloc[0]
    if st.sidebar.button("❌ Ta bort bolag"):
        df = df[df["Bolagsnamn"] != selected]
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Bolaget togs bort. Ladda om sidan.")
        st.stop()
else:
    selected = None
    data = None

with st.form("input_form"):
    namn = st.text_input("Bolagsnamn", value=data["Bolagsnamn"] if data is not None else "")
    kurs = st.number_input("Nuvarande aktiekurs", min_value=0.0, step=0.1, value=data["Nuvarande kurs"] if data is not None else 0.0)
    vinst_i_ar = st.number_input("Förväntad vinst i år", value=data["Vinst i år"] if data is not None else 0.0)
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", value=data["Vinst nästa år"] if data is not None else 0.0)
    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", value=data["Oms tillväxt i år"] if data is not None else 0.0)
    oms_tillv_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", value=data["Oms tillväxt nästa år"] if data is not None else 0.0)

    st.subheader("P/E historik")
    pe_hist = [st.number_input(f"P/E {i+1}", value=data[f"PE{i+1}"] if data is not None else 0.0, key=f"pe{i}") for i in range(5)]

    st.subheader("P/S historik")
    ps_hist = [st.number_input(f"P/S {i+1}", value=data[f"PS{i+1}"] if data is not None else 0.0, key=f"ps{i}") for i in range(5)]

    submitted = st.form_submit_button("💾 Spara & Beräkna")

if submitted:
    pe_snitt = sum(pe_hist) / 5
    ps_snitt = sum(ps_hist) / 5
    oms_tillv_snitt = (oms_tillv_i_ar + oms_tillv_nasta_ar) / 2

    target_pe = vinst_nasta_ar * pe_snitt
    oms_per_aktie_idag = kurs / ps_snitt if ps_snitt != 0 else 0
    oms_per_aktie_framtid = oms_per_aktie_idag * (1 + oms_tillv_snitt / 100)
    target_ps = ps_snitt * oms_per_aktie_framtid

    riktkurs = (target_pe + target_ps) / 2
    diff_procent = ((riktkurs - kurs) / riktkurs) * 100

    buy_lvl_30 = riktkurs * 0.7
    buy_lvl_40 = riktkurs * 0.6

    new_row = {
        "Bolagsnamn": namn, "Nuvarande kurs": kurs, "Vinst i år": vinst_i_ar, "Vinst nästa år": vinst_nasta_ar,
        "Oms tillväxt i år": oms_tillv_i_ar, "Oms tillväxt nästa år": oms_tillv_nasta_ar,
        **{f"PE{i+1}": pe_hist[i] for i in range(5)},
        **{f"PS{i+1}": ps_hist[i] for i in range(5)}
    }

    df = df[df["Bolagsnamn"] != namn]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = df.sort_values("Bolagsnamn")
    df.to_csv(DATA_FILE, index=False)

    st.success(f"{namn} sparat och analyserat!")

    st.subheader("🔍 Analys")
    st.markdown(f"""
    **Targetkurs:** {riktkurs:.2f} kr  
    **Nuvarande kurs:** {kurs:.2f} kr  
    **Undervärderad:** {"✅ Ja" if diff_procent > 0 else "❌ Nej"}  
    **Differens till riktkurs:** {diff_procent:.2f}%  
    **Köp om du vill ha 30% marginal:** {buy_lvl_30:.2f} kr  
    **Köp om du vill ha 40% marginal:** {buy_lvl_40:.2f} kr  
    """)

# === FILTERING UNDERVÄRDERADE BOLAG ===
st.sidebar.header("🔎 Filtrera undervärderade")
if not df.empty:
    df["PE-snitt"] = df[[f"PE{i}" for i in range(1, 6)]].mean(axis=1)
    df["PS-snitt"] = df[[f"PS{i}" for i in range(1, 6)]].mean(axis=1)
    df["Oms tillväxt snitt"] = (df["Oms tillväxt i år"] + df["Oms tillväxt nästa år"]) / 2

    df["Target PE"] = df["Vinst nästa år"] * df["PE-snitt"]
    df["Oms per aktie"] = df["Nuvarande kurs"] / df["PS-snitt"]
    df["Oms framtid"] = df["Oms per aktie"] * (1 + df["Oms tillväxt snitt"] / 100)
    df["Target PS"] = df["PS-snitt"] * df["Oms framtid"]
    df["Riktkurs"] = (df["Target PE"] + df["Target PS"]) / 2
    df["Diff %"] = ((df["Riktkurs"] - df["Nuvarande kurs"]) / df["Riktkurs"]) * 100

    filter_val = st.sidebar.radio("Visa bolag som är undervärderade med:", [
        "Visa alla undervärderade", "30–39,99%", "≥ 40%", "Visa alla"
    ])

    if filter_val == "Visa alla undervärderade":
        filt_df = df[df["Diff %"] > 0]
    elif filter_val == "30–39,99%":
        filt_df = df[(df["Diff %"] >= 30) & (df["Diff %"] < 40)]
    elif filter_val == "≥ 40%":
        filt_df = df[df["Diff %"] >= 40]
    else:
        filt_df = df.copy()

    if not filt_df.empty:
        chosen = st.sidebar.selectbox("📋 Välj bolag från filter", sorted(filt_df["Bolagsnamn"]))
        show = filt_df[filt_df["Bolagsnamn"] == chosen].iloc[0]
        st.sidebar.markdown(f"""
        **{show['Bolagsnamn']}**  
        Targetkurs: {show['Riktkurs']:.2f} kr  
        Diff: {show['Diff %']:.2f}%  
        """)
    else:
        st.sidebar.write("🚫 Inga bolag matchar filtret.")

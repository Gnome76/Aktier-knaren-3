import streamlit as st
import pandas as pd
import os
import json

DATA_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_target_price(pe_values, ps_values, vinst_i_ar, vinst_next_ar, oms_tillv_i_ar, oms_tillv_next_ar):
    avg_pe = sum(pe_values) / len(pe_values)
    avg_ps = sum(ps_values) / len(ps_values)
    snitt_vinst = (vinst_i_ar + vinst_next_ar) / 2
    snitt_tillv = (oms_tillv_i_ar + oms_tillv_next_ar) / 2

    pe_target = avg_pe * snitt_vinst
    ps_target = avg_ps * (1 + snitt_tillv / 100) * snitt_vinst

    final_target = (pe_target + ps_target) / 2
    return final_target

st.title("📊 Aktieräknaren")

data = load_data()
bolag_namn_lista = sorted(data.keys())

if "selected_bolag" not in st.session_state:
    st.session_state.selected_bolag = ""

st.sidebar.header("Navigering")
val = st.sidebar.radio("Välj", ["Lägg till/Redigera bolag", "Visa sparade bolag", "Filtrera undervärderade"])

if val == "Lägg till/Redigera bolag":
    st.header("➕ Lägg till eller redigera ett bolag")

    if st.button("Lägg till nytt bolag"):
        st.session_state.selected_bolag = ""

    bolagsnamn = st.text_input("Bolagsnamn", value=st.session_state.selected_bolag)

    pe_values = [st.number_input(f"P/E kvartal {i+1}", min_value=0.0) for i in range(5)]
    ps_values = [st.number_input(f"P/S kvartal {i+1}", min_value=0.0) for i in range(5)]
    kurs = st.number_input("Nuvarande aktiekurs", min_value=0.0)
    vinst_i_ar = st.number_input("Beräknad vinst i år (kr)", min_value=0.0)
    vinst_next_ar = st.number_input("Beräknad vinst nästa år (kr)", min_value=0.0)
    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", min_value=0.0)
    oms_tillv_next_ar = st.number_input("Omsättningstillväxt nästa år (%)", min_value=0.0)

    if st.button("Spara bolag"):
        target = calculate_target_price(pe_values, ps_values, vinst_i_ar, vinst_next_ar, oms_tillv_i_ar, oms_tillv_next_ar)
        undervärdering = ((target - kurs) / target) * 100
        köp_30 = target * 0.7
        köp_40 = target * 0.6

        data[bolagsnamn] = {
            "pe": pe_values,
            "ps": ps_values,
            "kurs": kurs,
            "vinst_i_ar": vinst_i_ar,
            "vinst_next_ar": vinst_next_ar,
            "oms_tillv_i_ar": oms_tillv_i_ar,
            "oms_tillv_next_ar": oms_tillv_next_ar,
            "target": target,
            "undervärdering": undervärdering,
            "köp_30": köp_30,
            "köp_40": köp_40
        }
        save_data(data)
        st.success(f"{bolagsnamn} sparades!")
        st.session_state.selected_bolag = bolagsnamn

        st.markdown("---")
        st.subheader(f"📈 Analys för {bolagsnamn}")

        st.markdown(f"""
        - 💰 **Nuvarande kurs**: {kurs:.2f} kr  
        - 🎯 **Targetkurs**: **{target:.2f} kr**  
        - 🧮 **Undervärdering**: **{undervärdering:.2f}%**  
        - 📉 **Köpläge (30 % marginal)**: Köp om kursen är **under {köp_30:.2f} kr**  
        - 📉 **Köpläge (40 % marginal)**: Köp om kursen är **under {köp_40:.2f} kr**
        """)

    if bolag_namn_lista:
        st.subheader("Redigera tidigare bolag")
        valt_bolag = st.selectbox("Välj bolag att ladda", [""] + bolag_namn_lista)
        if valt_bolag and valt_bolag in data:
            st.session_state.selected_bolag = valt_bolag
            st.experimental_rerun()

elif val == "Visa sparade bolag":
    st.header("📁 Sparade bolag")
    if not data:
        st.info("Inga bolag sparade ännu.")
    else:
        for namn in sorted(data.keys()):
            bolag = data[namn]
            with st.expander(f"{namn}"):
                st.write(f"🎯 **Targetkurs**: {bolag['target']:.2f} kr")
                st.write(f"💰 **Nuvarande kurs**: {bolag['kurs']:.2f} kr")
                st.write(f"🧮 **Undervärdering**: {bolag['undervärdering']:.2f}%")
                st.write(f"📉 **Köp vid 30% marginal**: {bolag['köp_30']:.2f} kr")
                st.write(f"📉 **Köp vid 40% marginal**: {bolag['köp_40']:.2f} kr")
                if st.button(f"Ta bort {namn}", key=f"remove_{namn}"):
                    data.pop(namn)
                    save_data(data)
                    st.success(f"{namn} har tagits bort.")
                    st.experimental_rerun()

elif val == "Filtrera undervärderade":
    st.header("🔍 Filtrera undervärderade bolag")
    filtrering = st.selectbox("Välj filter", ["Alla undervärderade", "30–39,99%", "40% eller mer"])
    filtrerade = {}

    for namn, info in data.items():
        uv = info["undervärdering"]
        if filtrering == "Alla undervärderade" and uv > 0:
            filtrerade[namn] = info
        elif filtrering == "30–39,99%" and 30 <= uv < 40:
            filtrerade[namn] = info
        elif filtrering == "40% eller mer" and uv >= 40:
            filtrerade[namn] = info

    if not filtrerade:
        st.info("Inga bolag matchar filtret.")
    else:
        for namn, info in filtrerade.items():
            st.markdown(f"- **{namn}**: undervärdering {info['undervärdering']:.2f}%, targetkurs {info['target']:.2f} kr")

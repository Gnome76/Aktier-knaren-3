import streamlit as st

st.set_page_config(page_title="Aktieräknaren", layout="centered")

st.title("📈 Aktieräknaren")
st.markdown("Fyll i nyckeltal för att få en beräknad riktkurs baserat på dina antaganden.")

st.header("🔢 Inmatning av nyckeltal")

kurs = st.number_input("Nuvarande aktiekurs (SEK):", min_value=0.0, step=0.01)

st.subheader("P/E (senaste 5 kvartalen)")
pe_list = [st.number_input(f"P/E kvartal {-i}:", min_value=0.0, step=0.1, key=f"pe{i}") for i in range(5)]

st.subheader("PEG (senaste 5 kvartalen)")
peg_list = [st.number_input(f"PEG kvartal {-i}:", min_value=0.0, step=0.1, key=f"peg{i}") for i in range(5)]

st.subheader("P/S (senaste 5 kvartalen)")
ps_list = [st.number_input(f"P/S kvartal {-i}:", min_value=0.0, step=0.1, key=f"ps{i}") for i in range(5)]

st.header("📊 Vinst och tillväxt")
vinst_år = st.number_input("Beräknad vinst per aktie i år (SEK):", min_value=0.0, step=0.01)
vinst_nästa_år = st.number_input("Beräknad vinst per aktie nästa år (SEK):", min_value=0.0, step=0.01)

tillväxt_oms_iår = st.number_input("Förväntad omsättningstillväxt i år (%):", min_value=-100.0, step=0.1)
tillväxt_oms_nästa = st.number_input("Förväntad omsättningstillväxt nästa år (%):", min_value=-100.0, step=0.1)

st.header("📈 Beräkna riktkurs")

if st.button("Beräkna riktkurs"):
    snitt_pe = sum(pe_list) / len(pe_list)
    snitt_peg = sum(peg_list) / len(peg_list)
    snitt_ps = sum(ps_list) / len(ps_list)

    riktkurs = 0.0
    pe_värde = vinst_nästa_år * snitt_pe
    ps_värde = kurs * (1 + (tillväxt_oms_nästa / 100))
    peg_justering = vinst_nästa_år * (snitt_pe / snitt_peg) if snitt_peg > 0 else 0

    riktkurs = (pe_värde + ps_värde + peg_justering) / 3

    st.success(f"🔮 Beräknad riktkurs: **{riktkurs:.2f} SEK**")
    st.markdown(f"""
    **Detaljer:**
    - Snitt P/E: `{snitt_pe:.2f}`
    - Snitt PEG: `{snitt_peg:.2f}`
    - Snitt P/S: `{snitt_ps:.2f}`
    - Vinst nästa år: `{vinst_nästa_år:.2f} SEK`
    """)

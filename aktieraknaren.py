import streamlit as st

# Initiera session_state om inte redan finns
if "companies" not in st.session_state:
    st.session_state.companies = {}

if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

st.title("📈 Aktieräknaren")

# Funktion för att räkna ut targetkurs
def calculate_target_price(pe_values, ps_values, earnings_this_year, earnings_next_year,
                           growth_this_year, growth_next_year, current_price):
    avg_pe = sum(pe_values) / len(pe_values)
    avg_ps = sum(ps_values) / len(ps_values)
    avg_growth = (growth_this_year + growth_next_year) / 2

    avg_earnings = (earnings_this_year + earnings_next_year) / 2
    avg_sales_growth_factor = 1 + avg_growth / 100

    target_pe = avg_pe * avg_earnings
    target_ps = avg_ps * avg_sales_growth_factor * avg_earnings

    target_price = (target_pe + target_ps) / 2
    undervaluation_percent = ((target_price - current_price) / current_price) * 100

    price_margin_30 = target_price * 0.7
    price_margin_40 = target_price * 0.6

    return round(target_price, 2), round(undervaluation_percent, 2), round(price_margin_30, 2), round(price_margin_40, 2)

# Lägg till nytt bolag-knapp (alltid synlig)
if st.button("➕ Lägg till nytt bolag"):
    st.session_state.selected_company = None
    for key in list(st.session_state.keys()):
        if key.startswith("pe_") or key.startswith("ps_"):
            st.session_state[key] = 0.0
    # Nollställ övriga inputs
    for key in ["Förväntad vinst i år", "Förväntad vinst nästa år", "Omsättningstillväxt i år (%)",
                "Omsättningstillväxt nästa år (%)", "Nuvarande kurs"]:
        if key in st.session_state:
            del st.session_state[key]

# Formulär
with st.form("company_form"):
    st.subheader("Lägg till / redigera bolag")

    name = st.text_input("Bolagsnamn", value="" if st.session_state.selected_company is None else st.session_state.selected_company)

    pe_values = [st.number_input(f"P/E {i+1}", key=f"pe_{i}", value=0.0, format="%.2f") for i in range(5)]
    ps_values = [st.number_input(f"P/S {i+1}", key=f"ps_{i}", value=0.0, format="%.2f") for i in range(5)]

    earnings_this_year = st.number_input("Förväntad vinst i år", value=0.0, format="%.2f")
    earnings_next_year = st.number_input("Förväntad vinst nästa år", value=0.0, format="%.2f")

    growth_this_year = st.number_input("Omsättningstillväxt i år (%)", value=0.0, format="%.2f")
    growth_next_year = st.number_input("Omsättningstillväxt nästa år (%)", value=0.0, format="%.2f")

    current_price = st.number_input("Nuvarande kurs", value=0.0, format="%.2f")

    submitted = st.form_submit_button("💾 Spara bolag")

    if submitted and name:
        st.session_state.companies[name] = {
            "pe": pe_values,
            "ps": ps_values,
            "earnings_this_year": earnings_this_year,
            "earnings_next_year": earnings_next_year,
            "growth_this_year": growth_this_year,
            "growth_next_year": growth_next_year,
            "current_price": current_price
        }
        st.session_state.selected_company = name
        st.success(f"{name} sparad!")

# Lista över sparade bolag
if st.session_state.companies:
    st.subheader("📊 Sparade bolag")

    company_names = sorted(st.session_state.companies.keys())

    selected = st.selectbox("Välj bolag att visa/redigera", company_names)
    if selected:
        st.session_state.selected_company = selected
        data = st.session_state.companies[selected]

        target_price, undervalued_pct, price_30, price_40 = calculate_target_price(
            data["pe"], data["ps"], data["earnings_this_year"], data["earnings_next_year"],
            data["growth_this_year"], data["growth_next_year"], data["current_price"]
        )

        st.markdown(f"""
        ### 📈 Analys för {selected}
        **Targetkurs:** {target_price} kr  
        **Undervärdering:** {undervalued_pct}%  
        **Kursnivå för 30% säkerhetsmarginal:** {price_30} kr  
        **Kursnivå för 40% säkerhetsmarginal:** {price_40} kr  
        """)

        if st.button("🗑️ Ta bort bolag"):
            del st.session_state.companies[selected]
            st.session_state.selected_company = None
            st.success(f"{selected} borttaget.")

# Filtrera undervärderade bolag
if st.session_state.companies:
    st.subheader("🔍 Filtrera undervärderade bolag")
    filter_option = st.selectbox(
        "Välj filter",
        ["Visa alla", "Undervärderade 30–39,99%", "Undervärderade >40%"]
    )

    filtered = []
    for name, data in st.session_state.companies.items():
        try:
            _, undervalued_pct, _, _ = calculate_target_price(
                data["pe"], data["ps"], data["earnings_this_year"], data["earnings_next_year"],
                data["growth_this_year"], data["growth_next_year"], data["current_price"]
            )
            if filter_option == "Visa alla":
                filtered.append(name)
            elif filter_option == "Undervärderade 30–39,99%" and 30 <= undervalued_pct < 40:
                filtered.append(name)
            elif filter_option == "Undervärderade >40%" and undervalued_pct >= 40:
                filtered.append(name)
        except:
            pass

    if filtered:
        st.selectbox("Resultat:", sorted(filtered))
    else:
        st.info("Inga bolag matchar det valda filtret.")

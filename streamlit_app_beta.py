
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Finanzanalyse Beta", layout="wide")

st.title("Finanzanalyse-Tool (Beta-Version)")
st.subheader("Automatische Auswertung von BWA-Daten")

uploaded_file = st.file_uploader("Lade deine BWA-Datei hoch (CSV oder Excel)", type=["csv", "xlsx"])

def steuer_hochrechnung(gewinn_monatlich, form):
    jahresgewinn = gewinn_monatlich * 12
    if form == "Einzelunternehmen":
        steuer = jahresgewinn * 0.30  # 30 % Einkommensteuer (vereinfacht)
    else:
        steuer = jahresgewinn * 0.15 + jahresgewinn * 0.15  # 15 % KSt + 15 % GewSt = ca. 30 %
    return steuer, jahresgewinn - steuer

form = st.selectbox("Wähle die Unternehmensform", ["Einzelunternehmen", "Kapitalgesellschaft (GmbH/UG)"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Vorschau der BWA:")
    st.dataframe(df)

    # Gewinn-Zeile finden
    try:
        gewinn_zeile = df[df["Position"].str.contains("Gewinn", case=False)]
        monatsgewinne = gewinn_zeile.drop(columns=["Position"]).values.flatten().astype(float)
        monatsgewinn_durchschnitt = monatsgewinne.mean()
        
        steuer, netto = steuer_hochrechnung(monatsgewinn_durchschnitt, form)

        st.markdown(f"### Monatlicher Durchschnittsgewinn: {monatsgewinn_durchschnitt:,.2f} €")
        st.markdown(f"### Jährliche Steuer (geschätzt): {steuer:,.2f} €")
        st.markdown(f"### Verfügbares Jahresergebnis nach Steuern: {netto:,.2f} €")

        fig, ax = plt.subplots()
        ax.plot(df.columns[1:], monatsgewinne, marker="o")
        ax.set_title("Monatlicher Gewinnverlauf")
        ax.set_ylabel("Gewinn in €")
        st.pyplot(fig)

        if netto / 12 > 2500:
            st.success("Kapitaldienstfähig (Netto monatlich über 2.500 €)")
        else:
            st.warning("Kapitaldienst unsicher – Netto monatlich unter 2.500 €")
    except:
        st.error("Gewinn-Zeile konnte nicht erkannt werden. Bitte prüfe die Datei.")

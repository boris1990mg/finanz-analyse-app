
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber

st.set_page_config(page_title="Finanzanalyse Beta", layout="wide")
st.title("Finanzanalyse-Tool (Beta-Version mit verbesserter PDF-Verarbeitung)")
st.subheader("Lade deine BWA-Datei hoch (CSV, Excel oder PDF)")

uploaded_file = st.file_uploader("Datei auswählen", type=["csv", "xlsx", "pdf"])

def steuer_hochrechnung(gewinn_monatlich, form):
    jahresgewinn = gewinn_monatlich * 12
    if form == "Einzelunternehmen":
        steuer = jahresgewinn * 0.30
    else:
        steuer = jahresgewinn * 0.15 + jahresgewinn * 0.15
    return steuer, jahresgewinn - steuer

form = st.selectbox("Wähle die Unternehmensform", ["Einzelunternehmen", "Kapitalgesellschaft (GmbH/UG)"])

if uploaded_file:
    df = None
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            lines = text.splitlines()
            data = []
            for line in lines:
                if ";" in line:
                    parts = line.split(";")
                else:
                    parts = [p.strip() for p in line.split("  ") if p.strip() != ""]
                if len(parts) > 1:
                    data.append(parts)

            if len(data) >= 2:
                df = pd.DataFrame(data[1:], columns=["Position"] + data[0][1:])
            else:
                st.warning("Keine geeignete Tabelle im PDF gefunden.")
        except Exception as e:
            st.error(f"PDF konnte nicht verarbeitet werden: {e}")

    if df is not None:
        st.write("Vorschau der Daten:")
        st.dataframe(df)

        try:
            gewinn_zeile = df[df["Position"].str.contains("Gewinn", case=False, na=False)]
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
            st.warning("Die Gewinn-Zeile konnte nicht automatisch ausgewertet werden.")

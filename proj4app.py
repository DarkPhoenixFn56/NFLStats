import streamlit as st
import pandas as pd
import requests
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from bs4 import BeautifulSoup

st.title('NFL Football Stats (Rushing) Explorer')

st.markdown("""
This app fetches NFL Football player rushing stats using a custom backend to avoid web scraping issues.
* **Backend:** FastAPI proxy
* **Frontend:** Streamlit
* **Data source:** [pro-football-reference.com](https://www.pro-football-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2000, 2020))))

@st.cache_data
def load_data(year):
    try:
        backend_url = f"http://localhost:8000/get_nfl_stats?year={year}"  # Update if hosted
        response = requests.get(backend_url)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            st.error(f"Backend Error: {data['error']}")
            return pd.DataFrame()

        soup = BeautifulSoup(data["html"], "lxml")
        table = soup.find("table")
        df = pd.read_html(str(table), header=1)[0]

        df = df[df['Age'] != 'Age']
        df = df.dropna(how='all')
        df = df.fillna(0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.drop(columns=['Rk'], errors='ignore')
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

playerstats = load_data(selected_year)

if not playerstats.empty and 'Tm' in playerstats.columns:
    sorted_unique_team = sorted(playerstats['Tm'].astype(str).unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

    unique_pos = ['RB', 'QB', 'WR', 'FB', 'TE']
    selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

    df_selected_team = playerstats[
        playerstats['Tm'].astype(str).isin(selected_team) &
        playerstats['Pos'].isin(selected_pos)
    ]

    st.header('Display Player Stats of Selected Team(s)')
    st.write(f'Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.')
    st.dataframe(df_selected_team)

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

    if st.button('Intercorrelation Heatmap'):
        st.header('Intercorrelation Matrix Heatmap')
        corr = df_selected_team.corr(numeric_only=True)
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            fig, ax = plt.subplots(figsize=(7, 5))
            sns.heatmap(corr, mask=mask, vmax=1, square=True, ax=ax)
        st.pyplot(fig)
else:
    st.warning("No valid data loaded for selected year.")


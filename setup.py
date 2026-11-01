import os

os.makedirs("data", exist_ok=True)

files = {}

files["requirements.txt"] = """streamlit
pandas
numpy
plotly
scikit-learn
"""

files["generate_data.py"] = r'''import os
import numpy as np
import pandas as pd

np.random.seed(42)

teams = ["LAL","BOS","GSW","MIA","DEN","MIL","PHX","DAL","NYK","PHI",
         "BKN","CHI","ATL","TOR","SAC","POR","UTA","OKC","MEM","NOP",
         "CLE","IND","DET","CHA","ORL","WAS","HOU","SAS","LAC","MIN"]
positions = ["PG","SG","SF","PF","C"]
first_names = ["LeBron","Stephen","Kevin","Giannis","Luka","Nikola","Joel","Jayson",
               "Damian","Jimmy","Anthony","Devin","Trae","Donovan","Zion","Ja",
               "Shai","Tyrese","Jaylen","Bam","Karl","Rudy","Domantas","De'Aaron",
               "Bradley","CJ","Jrue","Khris","Pascal","Fred","D'Angelo","Marcus",
               "Brook","Jonas","Alperen","Chet","Paolo","Scottie","Cade","LaMelo",
               "Evan","Jalen","Tyler","Keldon","Grant","Kyle","Austin","Duncan",
               "Josh","Mikal","OG","Miles","Terry","Bogdan","Bobby"]
last_names = ["James","Curry","Durant","Antetokounmpo","Doncic","Jokic","Embiid",
              "Tatum","Lillard","Butler","Davis","Booker","Young","Mitchell",
              "Williamson","Morant","Gilgeous","Haliburton","Brown","Adebayo",
              "Towns","Gobert","Sabonis","Fox","Beal","McCollum","Holiday",
              "Middleton","Siakam","VanVleet","Russell","Smart","Lopez",
              "Valanciunas","Sengun","Holmgren","Banchero","Barnes","Cunningham",
              "Ball","Mobley","Green","Herro","Johnson","Williams","Lowry",
              "Reaves","Robinson","Giddey","Bridges","Anunoby","Turner",
              "Rozier","Bogdanovic","Portis"]

rows = []
for i in range(120):
    name = f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}"
    team = np.random.choice(teams)
    pos = np.random.choice(positions)
    gp = np.random.randint(45, 82)
    minutes = round(np.random.uniform(18, 37), 1)
    pts = max(4.0, round(np.random.normal(minutes * 0.6, 4), 1))
    ast = round(max(0.5, np.random.normal(minutes * 0.15, 1.5)), 1)
    reb = round(max(0.5, np.random.normal(minutes * 0.2, 1.8)), 1)
    stl = round(max(0.0, np.random.normal(1.0, 0.4)), 1)
    blk = round(max(0.0, np.random.normal(0.5, 0.4)), 1)
    tov = round(max(0.3, np.random.normal(minutes * 0.07, 0.6)), 1)
    fg = round(np.random.uniform(0.38, 0.58), 3)
    tp = round(np.random.uniform(0.28, 0.44), 3)
    ft = round(np.random.uniform(0.65, 0.92), 3)
    per = round(np.random.uniform(10, 32), 1)
    ws = round(np.random.uniform(0.5, 16), 1)
    bpm = round(np.random.uniform(-4, 12), 1)
    vorp = round(max(0.0, np.random.uniform(0, 8)), 1)
    usg = round(np.random.uniform(15, 35), 1)
    ts = round(np.random.uniform(0.48, 0.68), 3)
    rows.append({"Player": name, "Team": team, "Pos": pos, "GP": gp,
                 "MIN": minutes, "PTS": pts, "AST": ast, "REB": reb,
                 "STL": stl, "BLK": blk, "TOV": tov, "FG%": fg, "3P%": tp,
                 "FT%": ft, "PER": per, "WS": ws, "BPM": bpm, "VORP": vorp,
                 "USG%": usg, "TS%": ts})

df = pd.DataFrame(rows)
df.to_csv("data/nba_stats.csv", index=False)
print(f"OK: {len(df)} players -> data/nba_stats.csv")
'''

files["app.py"] = r'''import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from numpy.linalg import norm

st.set_page_config(page_title="NBA MVP Profile", page_icon="🏀", layout="wide")
st.title("🏀 NBA MVP Profile Analyzer")
st.markdown("Сравните профиль игрока с средним профилем MVP и найдите скрытых MVP.")

@st.cache_data
def load_data():
    return pd.read_csv("data/nba_stats.csv")

df = load_data()
MVP_METRICS = ["PTS","AST","REB","PER","WS","BPM","VORP","USG%","TS%"]
df["MVP_SCORE"] = (df["PTS"]*0.25 + df["PER"]*0.25 + df["WS"]*0.25 + df["BPM"]*0.25)
mvp_profile = df.nlargest(5, "MVP_SCORE")[MVP_METRICS].mean()

tab1, tab2 = st.tabs(["📊 Сравнить с MVP", "🔍 Найти скрытого MVP"])
with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        player = st.selectbox("Выберите игрока", sorted(df["Player"].unique()))
    row = df[df["Player"] == player].iloc[0]
    with col2:
        st.subheader(f"{player} — {row['Team']} ({row['Pos']})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Очки", row["PTS"])
        c2.metric("Передачи", row["AST"])
        c3.metric("PER", row["PER"])
        c4.metric("WS", row["WS"])

    categories = MVP_METRICS
    player_vals = [row[m] for m in categories]
    mvp_vals = [mvp_profile[m] for m in categories]
    scaler = StandardScaler()
    scaler.fit(np.array([player_vals, mvp_vals,
                         df[categories].max().values, df[categories].min().values]))
    p_norm = scaler.transform([player_vals])[0]
    m_norm = scaler.transform([mvp_vals])[0]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=p_norm, theta=categories, fill="toself", name=player))
    fig.add_trace(go.Scatterpolar(r=m_norm, theta=categories, fill="toself", name="Профиль MVP"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False)),
                      showlegend=True, height=500,
                      title="Профиль игрока vs Средний MVP")
    st.plotly_chart(fig, use_container_width=True)

    diff = {m: row[m] - mvp_profile[m] for m in categories}
    weak = min(diff, key=diff.get)
    strong = max(diff, key=diff.get)
    st.info(f"💡 Инсайт: Сильнейшая сторона — {strong} "
            f"({row[strong]:.1f} vs {mvp_profile[strong]:.1f} у MVP). "
            f"Слабейшая — {weak} ({row[weak]:.1f} vs {mvp_profile[weak]:.1f}). "
            f"Именно {weak} чаще всего отделяет звёзд от MVP.")

with tab2:
    st.subheader("Игроки, наиболее похожие на MVP по профилю метрик")
    st.markdown("Косинусное сходство вектора метрик игрока со средним вектором MVP.")
    scaler2 = StandardScaler()
    X = scaler2.fit_transform(df[MVP_METRICS])
    mvp_vec = scaler2.transform([mvp_profile.values])[0]
    sims = X @ mvp_vec / (norm(X, axis=1) * norm(mvp_vec) + 1e-9)
    df["MVP_SIMILARITY"] = sims
    df["MVP_RANK"] = df["MVP_SCORE"].rank(ascending=False)
    hidden = df[(df["MVP_RANK"] > 10) & (df["MVP_SIMILARITY"] > 0.9)].copy()
    hidden = hidden.sort_values("MVP_SIMILARITY", ascending=False)
    if hidden.empty:
        hidden = df[df["MVP_RANK"] > 10].nlargest(8, "MVP_SIMILARITY")
    st.dataframe(hidden[["Player","Team","PTS","AST","REB","PER","WS","BPM",
                         "MVP_SIMILARITY","MVP_RANK"]].reset_index(drop=True),
                 use_container_width=True)
    if not hidden.empty:
        t = hidden.iloc[0]
        st.success(f"💡 Скрытый MVP: {t['Player']} ({t['Team']}) — профиль "
                   f"совпадает с MVP на {t['MVP_SIMILARITY']*100:.1f}%, но по "
                   f"комплексному скору лишь {int(t['MVP_RANK'])}-е место.")
'''

files["README.md"] = """# NBA MVP Profile Analyzer

Интерактивное веб-приложение для анализа того, что отличает MVP от элитных игроков,
и поиска «скрытых MVP».

## Запуск
pip install -r requirements.txt
python generate_data.py
streamlit run app.py

## Что делает
- Вкладка 1: radar chart метрик игрока против среднего профиля MVP.
- Вкладка 2: косинусное сходство с профилем MVP и поиск недооценённых игроков.

## Стек
Python, Streamlit, pandas, NumPy, Plotly, scikit-learn.
"""

for name, content in files.items():
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"created: {name}")

print("DONE")
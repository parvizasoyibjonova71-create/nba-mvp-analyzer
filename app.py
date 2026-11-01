import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from numpy.linalg import norm

# Настройка страницы
st.set_page_config(page_title="NBA MVP Profile", page_icon="🏀", layout="wide")

st.title("🏀 NBA MVP Profile Analyzer")
st.markdown(
    "Сравните профиль любого игрока с средним профилем MVP и найдите "
    "игроков, чьи метрики ближе всего к MVP, но кто не получил награду."
)

# Загрузка данных
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/nba_stats.csv")
        return df
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        return None

df = load_data()

if df is not None:
    MVP_METRICS = ["PTS", "AST", "REB", "PER", "WS", "BPM", "VORP", "USG%", "TS%"]

    # Считаем комплексный скор для MVP
    df["MVP_SCORE"] = (
        df["PTS"] * 0.25 + df["PER"] * 0.25 + df["WS"] * 0.25 + df["BPM"] * 0.25
    )
    mvp_profile = df.nlargest(5, "MVP_SCORE")[MVP_METRICS].mean()

    # Создаем вкладки
    tab1, tab2 = st.tabs(["📊 Сравнить с MVP", "🔍 Найти скрытого MVP"])

    # ---------- ВКЛАДКА 1 ----------
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

        # --- ИСПРАВЛЕННЫЙ ГРАФИК ---
        categories = MVP_METRICS
        player_vals = [row[m] for m in categories]
        mvp_vals = [mvp_profile[m] for m in categories]

        # Нормализация к процентам от максимума по лиге, чтобы график был красивым
        max_vals = df[categories].max().values
        p_norm = [(val / max_val) * 100 for val, max_val in zip(player_vals, max_vals)]
        m_norm = [(val / max_val) * 100 for val, max_val in zip(mvp_vals, max_vals)]

        fig = go.Figure()
        
        # Профиль игрока (синий)
        fig.add_trace(go.Scatterpolar(
            r=p_norm, theta=categories,
            fill='toself', name=player,
            line=dict(color='#00d2ff', width=2),
            fillcolor='rgba(0, 210, 255, 0.3)'
        ))
        
        # Профиль MVP (красный)
        fig.add_trace(go.Scatterpolar(
            r=m_norm, theta=categories,
            fill='toself', name="Профиль MVP",
            line=dict(color='#ff4b4b', width=2),
            fillcolor='rgba(255, 75, 75, 0.3)'
        ))
        
        # Настройка внешнего вида (прозрачный фон, белый текст)
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True, 
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Инсайт
        diff = {m: row[m] - mvp_profile[m] for m in categories}
        weak = min(diff, key=diff.get)
        strong = max(diff, key=diff.get)
        st.info(
            f"💡 Инсайт: Сильнейшая сторона относительно MVP — {strong} "
            f"({row[strong]:.1f} vs {mvp_profile[strong]:.1f} в среднем у MVP). "
            f"Слабейшая — {weak} ({row[weak]:.1f} vs {mvp_profile[weak]:.1f}). "
            f"Именно {weak} чаще всего отделяет звёзд от MVP."
        )

    # ---------- ВКЛАДКА 2 ----------
    with tab2:
        st.subheader("Игроки, наиболее похожие на MVP по профилю метрик")
        st.markdown("Косинусное сходство между вектором метрик игрока и средним вектором MVP.")
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
            
        st.dataframe(
            hidden[["Player", "Team", "PTS", "AST", "REB", "PER", "WS", "BPM", "MVP_SIMILARITY", "MVP_RANK"]].reset_index(drop=True),
            use_container_width=True
        )

        if not hidden.empty:
            top_hidden = hidden.iloc[0]
            st.success(
                f"💡 Скрытый MVP: {top_hidden['Player']} ({top_hidden['Team']}) "
                f"имеет профиль метрик, на {top_hidden['MVP_SIMILARITY']*100:.1f}% "
                f"совпадающий со средним профилем MVP, но по комплексному скору "
                f"находится лишь на {int(top_hidden['MVP_RANK'])}-м месте. "
                f"Классические голосования часто недооценивают такие профили."
            )
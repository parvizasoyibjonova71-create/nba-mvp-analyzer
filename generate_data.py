import os
import numpy as np
import pandas as pd

np.random.seed(42)

teams = ["LAL", "BOS", "GSW", "MIA", "DEN", "MIL", "PHX", "DAL",
         "NYK", "PHI", "BKN", "CHI", "ATL", "TOR", "SAC", "POR",
         "UTA", "OKC", "MEM", "NOP", "CLE", "IND", "DET", "CHA",
         "ORL", "WAS", "HOU", "SAS", "LAC", "MIN"]

positions = ["PG", "SG", "SF", "PF", "C"]

first_names = ["LeBron", "Stephen", "Kevin", "Giannis", "Luka", "Nikola",
               "Joel", "Jayson", "Damian", "Jimmy", "Anthony", "Devin",
               "Trae", "Donovan", "Zion", "Ja", "Shai", "Tyrese", "Jaylen",
               "Bam", "Karl", "Rudy", "Domantas", "De'Aaron", "Bradley",
               "CJ", "Jrue", "Khris", "Pascal", "Fred", "D'Angelo",
               "Marcus", "Brook", "Jonas", "Alperen", "Chet", "Paolo",
               "Scottie", "Cade", "LaMelo", "Evan", "Jalen", "Tyler",
               "Keldon", "Grant", "Kyle", "Austin", "Duncan", "Josh",
               "Mikal", "OG", "Miles", "Terry", "Bogdan", "Bobby"]

last_names = ["James", "Curry", "Durant", "Antetokounmpo", "Doncic", "Jokic",
              "Embiid", "Tatum", "Lillard", "Butler", "Davis", "Booker",
              "Young", "Mitchell", "Williamson", "Morant", "Gilgeous", "Haliburton", "Brown",
              "Adebayo", "Towns", "Gobert", "Sabonis", "Fox", "Beal",
              "McCollum", "Holiday", "Middleton", "Siakam", "VanVleet", "Russell",
              "Smart", "Lopez", "Valanciunas", "Sengun", "Holmgren", "Banchero",
              "Barnes", "Cunningham", "Ball", "Mobley", "Green", "Herro",
              "Johnson", "Williams", "Lowry", "Reaves", "Robinson", "Giddey",
              "Bridges", "Anunoby", "Turner", "Rozier", "Bogdanovic", "Portis"]

n_players = 120
rows = []

for i in range(n_players):
    name = f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}"
    team = np.random.choice(teams)
    pos = np.random.choice(positions)

    gp = np.random.randint(45, 82)
    minutes = round(np.random.uniform(18, 37), 1)

    # базовые очки зависят от минут
    pts = round(np.random.normal(minutes * 0.6, 4), 1)
    pts = max(4.0, pts)
    ast = round(max(0.5, np.random.normal(minutes * 0.15, 1.5)), 1)
    reb = round(max(0.5, np.random.normal(minutes * 0.2, 1.8)), 1)
    stl = round(max(0.0, np.random.normal(1.0, 0.4)), 1)
    blk = round(max(0.0, np.random.normal(0.5, 0.4)), 1)
    tov = round(max(0.3, np.random.normal(minutes * 0.07, 0.6)), 1)

    fg_pct = round(np.random.uniform(0.38, 0.58), 3)
    tp_pct = round(np.random.uniform(0.28, 0.44), 3)
    ft_pct = round(np.random.uniform(0.65, 0.92), 3)

    # продвинутые метрики (реалистичные диапазоны)
    per = round(np.random.uniform(10, 32), 1)
    ws = round(np.random.uniform(0.5, 16), 1)
    bpm = round(np.random.uniform(-4, 12), 1)
    vorp = round(max(0.0, np.random.uniform(0, 8)), 1)
    usg = round(np.random.uniform(15, 35), 1)
    ts = round(np.random.uniform(0.48, 0.68), 3)

    rows.append({
        "Player": name, "Team": team, "Pos": pos, "GP": gp,
        "MIN": minutes, "PTS": pts, "AST": ast, "REB": reb,
        "STL": stl, "BLK": blk, "TOV": tov,
        "FG%": fg_pct, "3P%": tp_pct, "FT%": ft_pct,
        "PER": per, "WS": ws, "BPM": bpm, "VORP": vorp,
        "USG%": usg, "TS%": ts
    })

df = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
df.to_csv("data/nba_stats.csv", index=False)
print(f"✅ Создано {len(df)} игроков → data/nba_stats.csv")
print(df.head())
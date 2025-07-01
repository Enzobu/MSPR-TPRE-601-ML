import pandas as pd                         # type: ignore
import psycopg2                             # type: ignore
from prophet import Prophet                 # type: ignore
from db.connection import get_connection    # type: ignore
import joblib                               # type: ignore
import matplotlib.pyplot as plt             # type: ignore
import common.utils as utils
import os
from datetime import datetime

query = utils.read_sql_query('./query/query.sql')

conn = get_connection()
df = pd.read_sql_query(query, conn)
conn.close()

df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
colonnes_numeriques = ['population', 'pib', 'deaths']
df = df[['ds', 'y', 'country_name'] + colonnes_numeriques].copy()

df = df[df['y'].notna()]
df = df[df['y'] > 0]

os.makedirs("models", exist_ok=True)
os.makedirs("predictions", exist_ok=True)
os.makedirs("plots", exist_ok=True)

conn = get_connection()
cur = conn.cursor()

today = datetime.today().date()
# cur.execute("DELETE FROM prediction WHERE ds > %s", (today,))
cur.execute("DELETE FROM prediction")
conn.commit()
print("[INFO] Prédictions futures existantes supprimées.")

for country in df['country_name'].unique():
    print(f"[INFO] Traitement du pays : {country}")

    df_country = df[df['country_name'] == country].copy()

    if len(df_country) < 10:
        print(f"[WARNING] Trop peu de données pour {country}. Prédiction ignorée.")
        continue


    model = Prophet()
    for reg in colonnes_numeriques:
        model.add_regressor(reg)

    model.fit(df_country)

    future = model.make_future_dataframe(periods=90)

    for col in colonnes_numeriques:
        future[col] = df_country[col].iloc[-1]

    forecast = model.predict(future)
    forecast['yhat'] = forecast['yhat'].clip(lower=0)

    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

    safe_country_name = country.replace(" ", "_").replace("/", "_")
    joblib.dump(model, f"models/prophet_model_{safe_country_name}.pkl")
    forecast.to_csv(f"predictions/forecast_{safe_country_name}.csv", index=False)

    fig = model.plot(forecast)
    fig.savefig(f"plots/forecast_plot_{safe_country_name}.png")
    plt.close(fig)

    print(f"[INFO] Modèle sauvegardé pour {country}.")

    cur.execute("SELECT id_country FROM country WHERE name = %s", (country,))
    result = cur.fetchone()
    if not result:
        print(f"[WARNING] id_country non trouvé pour {country}, insertion ignorée.")
        continue

    id_country = result[0]
    id_disease = 1

    for _, row in forecast.iterrows():
        cur.execute("""
            INSERT INTO prediction (
                id_country, id_disease, ds,
                yhat, yhat_lower, yhat_upper,
                trend, trend_lower, trend_upper,
                deaths, deaths_lower, deaths_upper,
                pib, pib_lower, pib_upper,
                population, population_lower, population_upper
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """, (
            id_country, id_disease, row['ds'],
            row.get('yhat'), row.get('yhat_lower'), row.get('yhat_upper'),
            row.get('trend'), row.get('trend_lower'), row.get('trend_upper'),
            row.get('deaths'), row.get('deaths_lower'), row.get('deaths_upper'),
            row.get('pib'), row.get('pib_lower'), row.get('pib_upper'),
            row.get('population'), row.get('population_lower'), row.get('population_upper')
        ))
    
    conn.commit()
    print(f"[INFO] Données sauvegardées en base pour {country}.")

cur.close()
conn.close()

print("[INFO] Tous les modèles sont générés.")

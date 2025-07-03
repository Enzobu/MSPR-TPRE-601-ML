import pandas as pd                         # type: ignore
import psycopg2                             # type: ignore
from prophet import Prophet                 # type: ignore
from db.connection import get_connection    # type: ignore
import joblib                               # type: ignore
import matplotlib.pyplot as plt             # type: ignore
import common.utils as utils
import os
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

query = utils.read_sql_query('./query/query.sql')

conn = get_connection()
df = pd.read_sql_query(query, conn)
conn.close()

df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
colonnes_numeriques = ['population', 'pib', 'deaths']
df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()

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

    # Récupération de l'id_country pour ce pays
    id_country = df_country['id_country'].iloc[0]

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

    # Calcul des métriques RMSE, MAE, R2 sur les données historiques uniquement
    df_country['ds'] = pd.to_datetime(df_country['ds'])
    forecast['ds'] = pd.to_datetime(forecast['ds'])
    
    df_eval = pd.merge(df_country[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')

    if len(df_eval) > 0:
        y_true = df_eval['y'].values
        y_pred = df_eval['yhat'].values

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Calcul R2 uniquement sur les données à partir de 2022
        df_eval_recent = df_eval[df_eval['ds'] >= pd.Timestamp("2022-01-01")]

        if len(df_eval_recent) > 0:
            y_true_recent = df_eval_recent['y'].values
            y_pred_recent = df_eval_recent['yhat'].values
            rmse_bis = np.sqrt(mean_squared_error(y_true_recent, y_pred_recent))
            mae_bis = mean_absolute_error(y_true_recent, y_pred_recent)
            r2_bis = r2_score(y_true_recent, y_pred_recent)
            print(f"[METRICS] {country} -> R2 à partir de 2022 : {r2_bis:.2f}")
        else:
            r2_bis = None
            print(f"[METRICS] {country} -> Pas assez de données depuis 2022 pour R2_bis.")

        print(f"[METRICS] {country} -> RMSE: {rmse:.2f}, MAE: {mae:.2f}, R2: {r2:.2f}")

        # Insertion dans la table metrics
        cur.execute("""
            INSERT INTO public.metrics (_date, RMSE, MAE, R2, id_country, r2_bis, rmse_bis, mae_bis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            today,
            float(rmse),
            float(mae),
            float(r2),
            int(id_country),
            float(r2_bis),
            float(rmse_bis),
            float(mae_bis)
        ))
    else:
        print(f"[METRICS] {country} -> Pas assez de données pour calculer les métriques.")

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

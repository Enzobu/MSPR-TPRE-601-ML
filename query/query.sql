WITH max_values AS (
  SELECT
    MAX(s.deaths) AS max_deaths,
    MAX(c.population) AS max_population,
    MAX(c.pib) AS max_pib
  FROM
    public.statement s
  JOIN
    public.country c ON s.id_country = c.id_country
  WHERE
    s.id_disease = 1
)

SELECT
  s._date AS ds,
  s.confirmed AS y,
  s.deaths::float / NULLIF(m.max_deaths, 0) AS deaths,
  c.population::float / NULLIF(m.max_population, 0) AS population,
  c.pib::float / NULLIF(m.max_pib, 0) AS pib,
  c.name as country_name,
  c.id_country
FROM
  public.statement s
JOIN
  public.country c ON s.id_country = c.id_country
JOIN
  public.disease d ON s.id_disease = d.id_disease
LEFT JOIN
  public.country_climat_type cc ON c.id_country = cc.id_country
CROSS JOIN
  max_values m
WHERE
  s.id_disease = 1
ORDER BY
  c.name, s._date;

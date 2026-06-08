# W/kg Estimator — potencia en subida con incertidumbre honesta

Estima la potencia relativa (vatios por kilo) de un ciclista en una subida a partir
de datos públicos (longitud, desnivel, tiempo) y, lo importante, **devuelve un rango,
no un número de falsa precisión**.

## La idea
Las cuentas de "watts watchers" tiran un número puntual y gritan "¡mutante!". Este
proyecto hace lo mismo, pero propagando la incertidumbre: en vez de "6,4 W/kg", devuelve
"6,4 W/kg, IC 90% 5,9–7,1, P(>6,2) = 67%". El número honesto es una distribución.

## Tres estimadores (de crudo a defendible)
- `ferrari_wkg`  — la regla de pulgar VAM (lo que se usa en redes).
- `physical_wkg` — modelo físico completo: gravedad + rodadura + aero + transmisión.
- `monte_carlo_wkg` — propaga la incertidumbre de lo que no se sabe (masa, CdA, Crr,
  viento, densidad del aire, ruido del DEM) → distribución + intervalo + P(> umbral).

## Correr
```
pip install numpy matplotlib pytest
python wkg_estimator.py      # demo: Alpe d'Huez -> guarda wkg_distribution.png
python compare_climbs.py     # Froome (Ax 3) vs Pogacar (Plateau de Beille) -> froome_vs_pogacar.png
python -m pytest -q          # tests de cordura
```

## Resultado de ejemplo (`compare_climbs.py`)
- **Froome, Ax 3 Domaines 2013** (8,9 km @ 7,5%, 23:14, ~67 kg):
  mediana 6,35 W/kg, IC 90% 5,86–7,05, P(>6,2) = 67% — justo sobre la línea, ambiguo.
- **Pogacar, Plateau de Beille 2024** (15,8 km @ 7,9%, 39:43, ~66 kg):
  mediana 7,00 W/kg, IC 90% 6,46–7,77, P(>6,2) = 100% — inequívocamente por encima del viejo techo.

Mismo método, dos subidas pirenaicas separadas por once años. La de Froome cae sobre la
línea de sospecha (por eso fue ambigua durante años); la de Pogacar la pasa con claridad.

## Datos y límites (honestos)
- Necesitás: longitud, desnivel y pendiente (segmentos de Strava o un DEM), el tiempo de la
  subida (cronometraje/TV) y la masa del corredor (estimada).
- La **masa** es la palanca más grande y los pesos publicados mienten → por eso el rango.
- **Viento y rebufo** cambian la potencia, sobre todo en pendientes suaves.
- Los priors están arriba de `monte_carlo_wkg`, editables en una línea; `unc_scale` los
  ensancha o achica de golpe.

## Postura
Esto **estima con incertidumbre, no acusa**. "Por encima del viejo techo" no es "dopado":
el techo se pudo mover (altitud, calor, nutrición, entrenamiento, aero). Se reporta el
rango; el lector juzga.

## Referencias (`refs.bib`)
Cada cita ancla un claim concreto — esto es lo que separa el proyecto de un artículo de revista:
- `martin1998`     — modelo físico de potencia (gravedad + rodadura + aero + transmisión); columna vertebral de `physical_wkg`.
- `pinot2011`      — Record Power Profile: relación hiperbólica potencia-duración; marco de "W/kg por duración".
- `pinot2015`      — datos reales de un top-10 de Grandes Vueltas (Thibaut Pinot); ancla de validación.
- `valenzuela2022` — gradiente-potencia en pros (óptimo 6-7%); realismo del régimen de subida.
- `leo2022`        — el rendimiento en subida depende del trabajo acumulado previo; respaldo del caveat de fatiga.
- `sanders2021`    — valores normativos de potencia por tipo de etapa; con qué comparar.
- `passfield2017`  — medir rendimiento es estocástico; legitima el "reporto el rango, no la cifra".

Nota honesta: la regla VAM / "factor de Ferrari" NO es peer-reviewed — es heuristica de
entrenador. El rigor esta en `martin1998`, el modelo fisico.

## Archivos
- `wkg_estimator.py`  — los tres estimadores (+ demo)
- `compare_climbs.py` — Froome vs Pogacar + gráfico
- `test_wkg.py`       — tests de cordura
- `refs.bib`          — bibliografía esencial (7 referencias verificadas)

# Preguntas probables y respuestas breves

## ¿Por qué usaron varianza poblacional?

Porque la aplicación describe todos los registros cargados como el conjunto de interés.
También muestra la varianza y desviación muestral para escenarios donde el archivo se
considere una muestra.

## ¿Cómo deciden el número de intervalos?

Para variables con más de 15 valores únicos se usa Sturges:
`k = 1 + 3,322 log10(n)`. Por legibilidad, el resultado se limita a entre 5 y 20 clases.
Con pocos valores únicos se presentan frecuencias por valor.

## ¿Qué significa que el CV sea 91,54 %?

Que la desviación estándar equivale aproximadamente al 91,54 % de la media. Indica
alta heterogeneidad relativa, por lo que la media sola no resume bien la demanda.

## ¿Por qué no eliminan los atípicos?

Un valor atípico estadístico no es necesariamente un error. En este dataset puede ser
una hora real de demanda excepcional. El programa los identifica, pero la decisión de
eliminarlos requiere contexto.

## ¿Cómo detectan atípicos?

Con el criterio de Tukey: valores menores que `Q1 - 1,5 RIC` o mayores que
`Q3 + 1,5 RIC`, donde `RIC = Q3 - Q1`.

## ¿Qué ocurre con datos faltantes?

El perfil informa cuántos hay. Para analizar una variable se omiten temporalmente sus
valores nulos o infinitos, sin modificar el DataFrame original.

## ¿La aplicación funciona con otro dataset?

Sí. No contiene nombres de columnas específicos. Detecta las columnas numéricas del
archivo cargado y actualiza selector, métricas, frecuencias, gráficos e interpretación.

## ¿Qué pasa si un CSV usa otra codificación o separador?

El cargador prueba UTF-8, CP1252 y Latin-1 y detecta automáticamente separadores comunes.
Si no puede interpretar el archivo, muestra un error legible.

## ¿Cuál es la diferencia entre histograma y gráfico de barras?

El histograma representa una variable numérica continua mediante intervalos contiguos.
El gráfico de barras muestra la frecuencia de clases o valores como categorías separadas.

## ¿La correlación prueba que la temperatura causa más alquileres?

No. La correlación mide asociación lineal. Puede haber estacionalidad, hora del día,
feriados u otras variables relacionadas. El informe evita afirmaciones causales.

## ¿Qué pruebas realizaron?

Ocho pruebas automáticas: requisitos del dataset, carga XLSX, exportación PDF, tendencia
central, dispersión, totales de frecuencia, atípicos, variable constante y ranking de
variabilidad. Todas fueron aprobadas.

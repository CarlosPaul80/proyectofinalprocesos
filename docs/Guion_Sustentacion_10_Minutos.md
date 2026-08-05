# Guion de sustentación - StatLab

Duración objetivo: 9 minutos 30 segundos. El margen restante permite responder una
pregunta breve sin superar los 10 minutos.

Reemplacen **Integrante A** y **Integrante B** por sus nombres. Ambos deben practicar la
carga del dataset y la interpretación, por si el docente cambia el orden.

## 0:00-0:45 - Apertura (Integrante A)

> Buenos días. Somos [nombres] y presentamos StatLab, una aplicación de escritorio
> desarrollada en Python para automatizar el análisis estadístico descriptivo de
> cualquier dataset tabular compatible. El problema que resolvemos es que calcular
> manualmente frecuencias, medidas y gráficos consume tiempo, puede introducir errores
> y no siempre ayuda a interpretar los resultados.

Mostrar la portada del informe o la pestaña **Resumen** del área principal.

## 0:45-1:35 - Objetivo y alcance (Integrante A)

> El objetivo fue crear una herramienta reutilizable que cargue CSV o Excel, detecte
> automáticamente las variables numéricas y produzca tablas, medidas, gráficos e
> interpretaciones sin modificar el código. El sistema realiza análisis descriptivo;
> no intenta demostrar causalidad.

Mencionar que el código está separado en carga, cálculos, gráficos, interpretación,
exportación e interfaz.

## 1:35-2:30 - Dataset (Integrante B)

> Para demostrar la aplicación usamos Seoul Bike Sharing Demand, publicado por UCI.
> Contiene 8.760 registros horarios y 14 columnas, de las cuales 10 son numéricas. No
> presenta valores faltantes y tiene licencia CC BY 4.0. La variable principal es el
> número de bicicletas alquiladas por hora, acompañada de temperatura, humedad, viento,
> visibilidad, lluvia, nieve, radiación solar, estación y condición operativa.

Justificación:

- Cumple ampliamente los mínimos de filas, columnas y variables numéricas.
- Es un caso real con utilidad para movilidad urbana.
- Permite estudiar asimetría, dispersión, atípicos y factores contextuales.

## 2:30-4:15 - Demostración de carga y resumen (Integrante A)

1. Abrir `StatLab.exe` desde la carpeta completa `dist/StatLab`.
2. En la barra lateral izquierda, ubicar la sección **FUENTE DE DATOS** y presionar
   **Cargar Datos**.
3. Seleccionar `data/SeoulBikeData.csv`. Como alternativa para la demostración, usar
   **Archivo > Cargar dataset de demostración**.
4. En la pestaña **Resumen**, mostrar:
   - 8.760 registros.
   - 14 columnas.
   - 10 variables numéricas.
   - 0 datos faltantes.
5. En la sección **VARIABLE NUMÉRICA** de la barra lateral, elegir
   `Rented Bike Count`. Si el análisis no se actualiza automáticamente, presionar
   **Actualizar Análisis**.

> La aplicación no tiene columnas específicas programadas. El selector de la barra
> lateral se genera a partir de los tipos de datos del archivo. En Resumen aparecen
> media, mediana, moda, rango, desviación media, varianza, desviación estándar,
> cuartiles, asimetría y atípicos.

## 4:15-5:15 - Frecuencias (Integrante A)

En el área principal, abrir la pestaña **Frecuencias**.

> Como la variable tiene muchos valores distintos, el programa agrupa automáticamente
> mediante la regla de Sturges. Para cada clase calcula frecuencia absoluta, relativa,
> porcentual, acumulada y porcentaje acumulado. La suma de frecuencias absolutas es
> 8.760, las relativas suman 1 y los porcentajes suman 100.

Mostrar el botón **Exportar CSV**, ubicado en la parte superior derecha de la pestaña.

## 5:15-6:20 - Gráficos (Integrante B)

Abrir la pestaña **Gráficos** y mantener seleccionada la subpestaña
**Distribuciones**.

> El histograma muestra que los conteos bajos son los más frecuentes. El gráfico de
> barras representa las clases, el polígono facilita comparar su forma y la curva
> acumulada indica el porcentaje por debajo de cada límite.

Señalar que cada gráfico tiene título, nombres de ejes y escala. Luego abrir la
subpestaña **Diagrama de cajas** para mostrar el boxplot, los cuartiles y los posibles
valores atípicos.

## 6:20-7:45 - Interpretación de resultados (Integrante B)

Abrir la pestaña **Interpretación**. Señalar el botón **Exportar Reporte PDF** en la
parte superior derecha, pero conservar la interpretación visible durante la
explicación.

> Para Rented Bike Count, la media es 704,60 y la mediana 504,50. Que la media sea mayor
> que la mediana, junto con una asimetría de 1,15, indica una cola hacia la derecha. La
> desviación estándar es 644,96 y el coeficiente de variación 91,54 %, por lo que la
> demanda es heterogénea y el promedio debe leerse con cautela.

> El sistema detecta 158 atípicos con el criterio de 1,5 veces el rango
> intercuartílico. No se eliminan automáticamente porque pueden ser horas reales de alta
> demanda. La moda es cero y se explica en parte porque existen 295 horas marcadas como
> no funcionales.

## 7:45-8:35 - Calidad técnica y extras (Integrante A)

> El código está organizado en módulos y cuenta con pruebas automáticas. Verificamos
> carga CSV y Excel, fórmulas de tendencia central y dispersión, totales de frecuencia,
> atípicos, variables constantes, portada del informe y generación de PDF. Se ejecutaron
> diez pruebas y todas
> fueron aprobadas.

Extras para mencionar:

- Boxplot, cuartiles, RIC, asimetría y curtosis.
- Ranking de variabilidad mediante coeficiente de variación.
- Exportación de frecuencia a CSV y análisis a PDF.
- Validación de archivos vacíos, formatos incompatibles y columnas duplicadas.

## 8:35-9:20 - Conclusiones (Integrante B)

> Concluimos que StatLab cumple el objetivo de ser dinámico y reutilizable. En el caso
> de Seúl, la demanda horaria es asimétrica y altamente variable; por eso no basta con
> presentar la media. La combinación de mediana, desviación, atípicos y gráficos permite
> una interpretación más completa. Como mejora futura proponemos filtros por categorías
> y análisis bivariado interactivo.

## 9:20-9:30 - Cierre (ambos)

> Gracias por su atención. Estamos listos para responder sus preguntas.

## Plan de contingencia para la grabación

- Abrir el ejecutable desde su carpeta completa, cargar el dataset y dejar seleccionada
  la variable `Rented Bike Count` antes de empezar a grabar.
- Ensayar el recorrido exacto: barra lateral, Resumen, Frecuencias, Gráficos
  (Distribuciones y Diagrama de cajas) e Interpretación.
- Cerrar notificaciones, mensajería y ventanas personales.
- Usar zoom de Windows al 100 % o 125 % y resolución mínima de 1366 x 768.
- Tener abierto el informe PDF por si falla la demostración en vivo.
- Grabar una prueba de 20 segundos para verificar audio y legibilidad.
- Si el ejecutable tarda en abrir, comenzar con el PDF y volver a la aplicación.

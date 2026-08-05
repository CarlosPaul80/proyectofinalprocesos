# StatLab

Aplicación de escritorio para análisis estadístico descriptivo de archivos CSV y
Excel (.xlsx). Su interfaz gráfica, construida con CustomTkinter y adaptada al modo
oscuro, organiza la carga y la selección de variables en una barra lateral. El sistema
detecta automáticamente las variables numéricas y funciona sin cambios de código con
cualquier dataset tabular compatible.

## Funcionalidades

- Carga de archivos CSV y XLSX con validación de errores.
- Vista previa tabular y perfil general del dataset.
- Selección dinámica de cualquier variable numérica.
- Tabla de frecuencias absoluta, relativa, porcentual y acumulada.
- Histograma, barras, polígono, curva acumulada y boxplot.
- Media, mediana, moda, rango y desviación media.
- Varianza y desviación estándar poblacional y muestral.
- Cuartiles, RIC, coeficiente de variación, asimetría y curtosis.
- Detección de valores atípicos mediante el criterio de 1,5 RIC.
- Interpretaciones automáticas y comparación de variabilidad entre columnas.
- Exportación de la tabla de frecuencias a CSV.
- Exportación del análisis seleccionado a un reporte PDF.

## Inicio rápido en Windows

1. Instale Python 3.11 o superior desde <https://www.python.org/downloads/>.
   Durante la instalación, marque **Add Python to PATH**.
2. Ejecute `setup_windows.bat` una sola vez.
3. Ejecute `run_demo.bat` para abrir el dataset incluido, o `run_app.bat` para
   comenzar sin datos.

También puede usar la terminal:

```powershell
python -m pip install -r requirements.txt
python main.py --demo
```

Si no desea instalar Python, abra `dist\StatLab\StatLab.exe`. Mantenga el ejecutable
dentro de su carpeta `dist\StatLab`, porque allí se encuentran sus dependencias.

## Uso

1. En la barra lateral, presione **Cargar Datos** y elija un CSV o Excel.
2. En la sección **VARIABLE NUMÉRICA** de esa misma barra, seleccione la columna
   que desea analizar. Si es necesario, presione **Actualizar Análisis**.
3. Recorra las pestañas **Resumen**, **Datos**, **Frecuencias**, **Gráficos** e
   **Interpretación** del área principal.
4. Dentro de **Gráficos**, alterne entre **Distribuciones** y
   **Diagrama de cajas**.
5. Exporte la tabla o el reporte PDF desde los botones disponibles o desde el menú
   **Archivo**.

## Reglas estadísticas implementadas

- Para variables con hasta 15 valores únicos, se muestran frecuencias por valor.
- Para variables continuas, el número de intervalos se obtiene con la regla de
  Sturges: `k = 1 + 3,322 log10(n)`, limitado a entre 5 y 20 clases.
- La varianza principal se presenta como poblacional porque la aplicación describe
  todos los registros cargados. También se muestra la versión muestral.
- Los atípicos son valores menores que `Q1 - 1,5 RIC` o mayores que
  `Q3 + 1,5 RIC`.
- La comparación entre variables usa el coeficiente de variación
  `CV = desviación estándar / |media| × 100`; se omiten medias iguales a cero.

## Arquitectura

```text
main.py
└── analizador/
    ├── data_loader.py         carga, validación y perfilado
    ├── statistics_engine.py   cálculos y frecuencias
    ├── visualizations.py      gráficos
    ├── interpretation.py      texto descriptivo automático
    ├── reporting.py           reportes PDF exportables
    └── ui.py                  interfaz gráfica CustomTkinter
```

## Pruebas

Desde la carpeta del proyecto:

```powershell
python -m unittest discover -s tests -v
```

## Crear un ejecutable

Después de instalar las dependencias, ejecute `build_exe.bat`. El resultado se crea
en `dist\StatLab\StatLab.exe`. El proceso puede tardar varios minutos.

## Personalizar el informe

1. Abra `config_informe.json`.
2. Reemplace institución, integrantes y docente.
3. Ejecute `python generar_informe.py`.
4. Revise `docs\Informe_Tecnico_StatLab.pdf`.

El generador crea un informe con portada, índice, objetivos, dataset, arquitectura,
metodología, capturas, resultados, pruebas, conclusiones y bibliografía APA 7. Después
de cambiar la configuración o las capturas, vuelva a generarlo y revise visualmente
todo el PDF antes de entregarlo.

## Entregables incluidos

- Código fuente modular y pruebas.
- Dataset de demostración autorizado y su referencia.
- Carpeta del ejecutable de Windows en `dist\StatLab`.
- Plantilla y generador del informe técnico, además de un reporte de análisis de
  ejemplo.
- Carpeta de capturas del sistema para la versión vigente de la interfaz.
- Guion de sustentación de 10 minutos.
- Preguntas probables de defensa y checklist final.

Antes de crear el paquete de entrega, complete `config_informe.json`, regenere el
informe y confirme que sus capturas corresponden a la interfaz oscura actual. Entregue
la carpeta `dist\StatLab` completa; el archivo `StatLab.exe` no funciona de forma
aislada.

## Dataset incluido

Seoul Bike Sharing Demand, UCI Machine Learning Repository:
<https://doi.org/10.24432/C5F62R>. Consulte `data/README_DATASET.md` para detalles
de licencia y procedencia.

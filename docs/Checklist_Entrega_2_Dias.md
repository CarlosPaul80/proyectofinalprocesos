# Checklist final de presentación y entrega

## Personalización del grupo

- [x] Dataset **Seoul Bike Sharing Demand** confirmado con el docente.
- [x] Editar `config_informe.json` con institución, integrantes y docente.
- [x] Confirmar que `docs/capturas/` muestre la interfaz oscura actual, con barra
  lateral y pestañas.
- [x] Ejecutar `python generar_informe.py` después de completar los datos y verificar
  las capturas.
- [x] Abrir `docs/Informe_Tecnico_StatLab.pdf` y revisar portada, nombres, capturas,
  gráficos, saltos de página y legibilidad.

## Validación de la aplicación

- [x] Ejecutar `python -m unittest discover -s tests -v` y confirmar que las 10 pruebas
  terminen con `OK`.
- [x] Abrir `dist/StatLab/StatLab.exe` desde la carpeta completa.
- [x] Cargar `data/SeoulBikeData.csv` y comprobar 8.760 registros, 14 columnas,
  10 variables numéricas y 0 datos faltantes.
- [x] Cambiar la variable desde la barra lateral y recorrer **Resumen**, **Datos**,
  **Frecuencias**, **Gráficos** e **Interpretación**.
- [x] En **Gráficos**, revisar tanto **Distribuciones** como
  **Diagrama de cajas**, sin recortes ni textos ilegibles.
- [x] Exportar una tabla CSV y un reporte PDF; abrir ambos archivos y comprobar su
  contenido.

## Presentación y video

- [ ] Repartir el guion entre los dos integrantes.
- [ ] Hacer un ensayo completo con cronómetro; meta: 9:00 a 9:30.
- [ ] Practicar las preguntas de `Preguntas_Probables_Defensa.md`.
- [ ] Grabar el video en un lugar silencioso.
- [ ] Comprobar que el video tenga imagen, audio y duración menor o igual a 10 minutos.
- [ ] Guardar una copia del video en dos ubicaciones.

## Antes de subir

- [x] Código fuente completo (`main.py`, carpeta `analizador`, pruebas).
- [x] Ejecutable (`dist/StatLab` completo, no solamente el archivo `.exe`).
- [x] Dataset (`data/SeoulBikeData.csv`).
- [x] Informe PDF regenerado con nombres reales y capturas actuales.
- [ ] Video final.
- [x] Eliminar del paquete archivos temporales o exportaciones de prueba que no formen
  parte de la entrega.
- [ ] Verificar que el enlace o archivo enviado pueda abrirse.

## Importante sobre el ejecutable

El ejecutable usa una carpeta de dependencias. Debe entregarse **toda** la carpeta
`dist/StatLab`, no solo `StatLab.exe`. Para moverlo a otro equipo, compriman esa carpeta
en ZIP y descomprímanla antes de ejecutar.

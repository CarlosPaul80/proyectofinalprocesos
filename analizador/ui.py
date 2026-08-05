"""Interfaz gráfica principal de StatLab construida con CustomTkinter."""

from __future__ import annotations

from pathlib import Path
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from . import __version__
from .data_loader import DataLoadError, DatasetProfile, load_dataset, profile_dataset
from .interpretation import generate_interpretation
from .reporting import export_variable_report
from .statistics_engine import AnalysisResult, analyze_variable
from .visualizations import create_analysis_figure, create_boxplot_figure


class StatisticalApp(ctk.CTk):
    """Aplicación dinámica para explorar cualquier dataset tabular compatible."""

    def __init__(self, load_demo: bool = False) -> None:
        super().__init__()
        self.title("StatLab · Análisis estadístico descriptivo")

        # CustomTkinter escala las dimensiones según el DPI de Windows. Un tamaño
        # fijo grande puede superar el área útil; maximizar delega el ajuste al SO.
        self._configure_window_size()
        
        # Grid layout de 1 fila x 2 columnas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.data: pd.DataFrame | None = None
        self.profile: DatasetProfile | None = None
        self.analysis: AnalysisResult | None = None
        self.file_path: Path | None = None
        self.chart_canvas: FigureCanvasTkAgg | None = None
        self.boxplot_canvas: FigureCanvasTkAgg | None = None

        self._configure_styles()
        self._build_menu()
        self._build_sidebar()
        self._build_main_area()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        if load_demo:
            self.after(250, self.load_demo_dataset)

    def _configure_window_size(self) -> None:
        """Ajusta la ventana al escritorio respetando el escalado DPI de CTk."""
        window_scale = max(float(self._get_window_scaling()), 1.0)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # CTk vuelve a multiplicar geometry/minsize por window_scale. Por eso
        # expresamos el tamaño solicitado en unidades lógicas antes de aplicarlo.
        # Conserva espacio para los bordes y la barra de tareas, aprovechando
        # el resto del área para que las cuatro gráficas se vean completas.
        usable_width = max(1080, screen_width - 40)
        usable_height = max(680, screen_height - 25)
        logical_width = int(usable_width / window_scale)
        logical_height = int(usable_height / window_scale)
        minimum_width = int(960 / window_scale)
        minimum_height = int(620 / window_scale)

        self.geometry(f"{logical_width}x{logical_height}")
        self.minsize(minimum_width, minimum_height)

    def _configure_styles(self) -> None:
        """Configura el estilo de los elementos ttk (como Treeview) para que hagan match con CustomTkinter Dark Mode."""
        style = ttk.Style(self)
        style.theme_use("clam")
        
        bg_color = "#2B2B2B"
        fg_color = "#DCE4EE"
        selected_bg = "#3B82F6"
        header_bg = "#1F1F1F"
        
        style.configure(".", font=("Segoe UI", 10))
        style.configure(
            "Treeview",
            background=bg_color,
            fieldbackground=bg_color,
            foreground=fg_color,
            rowheight=32,
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Treeview.Heading",
            background=header_bg,
            foreground=fg_color,
            font=("Segoe UI Semibold", 10),
            padding=(8, 8),
            borderwidth=0,
            relief="flat"
        )
        style.map("Treeview", background=[("selected", selected_bg)])
        style.map("Treeview.Heading", background=[("active", "#2A2A2A")])
        
        # Scrollbars para que coincidan (oscuros)
        style.configure("Vertical.TScrollbar", background=header_bg, troughcolor=bg_color, bordercolor=bg_color, arrowcolor=fg_color)
        style.configure("Horizontal.TScrollbar", background=header_bg, troughcolor=bg_color, bordercolor=bg_color, arrowcolor=fg_color)

    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Abrir CSV o Excel…", command=self.choose_file)
        file_menu.add_command(label="Cargar dataset de demostración", command=self.load_demo_dataset)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar análisis a PDF…", command=self.export_analysis)
        file_menu.add_command(label="Exportar tabla de frecuencias…", command=self.export_frequency)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.destroy)
        menu.add_cascade(label="Archivo", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="Acerca de StatLab", command=self.show_about)
        menu.add_cascade(label="Ayuda", menu=help_menu)
        self.config(menu=menu)

    def _build_sidebar(self) -> None:
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Brand
        brand_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="STATLAB", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#3B82F6"
        )
        brand_label.grid(row=0, column=0, padx=20, pady=(30, 0), sticky="w")
        subtitle_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Análisis Estadístico", 
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")

        # Dataset Section
        dataset_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        dataset_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(dataset_frame, text="FUENTE DE DATOS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", pady=(0, 5))
        
        self.file_label = ctk.CTkLabel(dataset_frame, text="Ningún archivo cargado", font=ctk.CTkFont(size=12))
        self.file_label.pack(anchor="w", pady=(0, 10))
        
        load_btn = ctk.CTkButton(dataset_frame, text="Cargar Datos", command=self.choose_file, fg_color="#3B82F6", hover_color="#2563EB")
        load_btn.pack(fill="x")
        
        self.selection_hint = ctk.CTkLabel(dataset_frame, text="Carga un CSV o Excel.", text_color="#94A3B8", font=ctk.CTkFont(size=11))
        self.selection_hint.pack(anchor="w", pady=(5, 0))

        # Variable Selection Section
        variable_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        variable_frame.grid(row=3, column=0, padx=20, pady=30, sticky="ew")
        
        ctk.CTkLabel(variable_frame, text="VARIABLE NUMÉRICA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", pady=(0, 5))
        
        self.variable = ctk.StringVar()
        self.variable_combo = ctk.CTkOptionMenu(
            variable_frame, 
            variable=self.variable,
            values=["-"],
            state="disabled",
            command=self._on_variable_selected,
            dynamic_resizing=False
        )
        self.variable_combo.pack(fill="x", pady=(0, 10))
        
        self.update_btn = ctk.CTkButton(variable_frame, text="Actualizar Análisis", command=self.analyze_selected, fg_color="transparent", border_width=1, border_color="#3B82F6", text_color="#3B82F6", hover_color="#1E3A8A")
        self.update_btn.pack(fill="x")

        # Status
        self.status_var = ctk.StringVar(value="Listo · Esperando dataset")
        status_label = ctk.CTkLabel(self.sidebar_frame, textvariable=self.status_var, font=ctk.CTkFont(size=11), text_color="#94A3B8", wraplength=240)
        status_label.grid(row=6, column=0, padx=20, pady=20, sticky="sw")

    def _build_main_area(self) -> None:
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.summary_tab = self.notebook.add("Resumen")
        self.data_tab = self.notebook.add("Datos")
        self.frequency_tab = self.notebook.add("Frecuencias")
        self.charts_tab = self.notebook.add("Gráficos")
        self.interpretation_tab = self.notebook.add("Interpretación")

        self._build_summary_tab()
        self._build_data_tab()
        self._build_frequency_tab()
        self._build_charts_tab()
        self._build_interpretation_tab()

    def _build_summary_tab(self) -> None:
        self.summary_tab.grid_columnconfigure((0, 1), weight=1)
        self.summary_tab.grid_rowconfigure(1, weight=1)
        
        # Tarjetas Superiores
        self.cards_frame = ctk.CTkFrame(self.summary_tab, fg_color="transparent")
        self.cards_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(10, 20))
        self.card_values: dict[str, ctk.CTkLabel] = {}
        
        cards = [
            ("Registros", "0", "#3B82F6"),
            ("Columnas", "0", "#06B6D4"),
            ("Numéricas", "0", "#8B5CF6"),
            ("Datos faltantes", "0", "#F59E0B"),
            ("Atípicos", "0", "#EF4444"),
        ]
        
        for index, (title, initial, color) in enumerate(cards):
            self.cards_frame.grid_columnconfigure(index, weight=1)
            card = ctk.CTkFrame(self.cards_frame, corner_radius=8)
            card.grid(row=0, column=index, sticky="nsew", padx=5)
            
            # Accent line
            ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=4).pack(fill="x", padx=1, pady=1)
            
            ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(10, 0))
            value = ctk.CTkLabel(card, text=initial, font=ctk.CTkFont(size=24, weight="bold"))
            value.pack(anchor="w", padx=15, pady=(0, 15))
            self.card_values[title] = value

        # Tablas y Textos inferiores
        metrics_container = ctk.CTkFrame(self.summary_tab)
        metrics_container.grid(row=1, column=0, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        ctk.CTkLabel(metrics_container, text="Indicadores de la variable", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        tree_frame1 = ctk.CTkFrame(metrics_container, fg_color="transparent")
        tree_frame1.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.metrics_tree = ttk.Treeview(tree_frame1, columns=("metric", "value"), show="headings")
        self.metrics_tree.heading("metric", text="Indicador")
        self.metrics_tree.heading("value", text="Resultado")
        self.metrics_tree.column("metric", width=250, anchor="w")
        self.metrics_tree.column("value", width=150, anchor="e")
        metrics_scroll = ttk.Scrollbar(tree_frame1, orient="vertical", command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=metrics_scroll.set)
        self.metrics_tree.pack(side="left", fill="both", expand=True)
        metrics_scroll.pack(side="right", fill="y")

        profile_container = ctk.CTkFrame(self.summary_tab)
        profile_container.grid(row=1, column=1, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        ctk.CTkLabel(profile_container, text="Perfil del dataset", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.profile_text = ctk.CTkTextbox(profile_container, wrap="word", font=ctk.CTkFont(size=13), fg_color="#1F1F1F")
        self.profile_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.profile_text.configure(state="disabled")

    def _build_data_tab(self) -> None:
        header = ctk.CTkFrame(self.data_tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 15))
        
        ctk.CTkLabel(header, text="Vista previa del dataset", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        self.preview_label = ctk.CTkLabel(header, text="Se mostrarán hasta 500 registros.", text_color="#94A3B8")
        self.preview_label.pack(side="right")

        table_frame = ctk.CTkFrame(self.data_tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.data_tree = ttk.Treeview(table_frame, show="headings")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.data_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        y_scroll.grid(row=0, column=1, sticky="ns", pady=(10, 0), padx=(0, 10))
        x_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _build_frequency_tab(self) -> None:
        header = ctk.CTkFrame(self.frequency_tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 15))
        
        ctk.CTkLabel(header, text="Distribución de frecuencias", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Exportar CSV", command=self.export_frequency, width=120, fg_color="#334155", hover_color="#475569").pack(side="right")
        self.frequency_note = ctk.CTkLabel(header, text="", text_color="#94A3B8")
        self.frequency_note.pack(side="right", padx=15)

        frame = ctk.CTkFrame(self.frequency_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.frequency_tree = ttk.Treeview(frame, show="headings")
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.frequency_tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.frequency_tree.xview)
        self.frequency_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        self.frequency_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        y_scroll.grid(row=0, column=1, sticky="ns", pady=(10, 0), padx=(0, 10))
        x_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 10))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _build_charts_tab(self) -> None:
        self.chart_notebook = ctk.CTkTabview(self.charts_tab)
        self.chart_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.main_charts_frame = self.chart_notebook.add("Distribuciones")
        self.boxplot_frame = self.chart_notebook.add("Diagrama de cajas")
        
        self.chart_placeholder: ctk.CTkLabel | None = ctk.CTkLabel(
            self.main_charts_frame,
            text="Los gráficos aparecerán al seleccionar una variable.",
            text_color="#94A3B8",
            font=ctk.CTkFont(size=13)
        )
        self.chart_placeholder.pack(expand=True)

    def _build_interpretation_tab(self) -> None:
        header = ctk.CTkFrame(self.interpretation_tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 15))
        
        ctk.CTkLabel(header, text="Análisis automático de resultados", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Exportar Reporte PDF", command=self.export_analysis, width=140, fg_color="#3B82F6", hover_color="#2563EB").pack(side="right")

        body = ctk.CTkFrame(self.interpretation_tab)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.interpretation_text = ctk.CTkTextbox(
            body,
            wrap="word",
            font=ctk.CTkFont(size=13),
            fg_color="#1F1F1F",
            spacing1=5,
            spacing3=10
        )
        self.interpretation_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.interpretation_text.configure(state="disabled")
        
        # Tags for textbox to simulate styling (Tkinter Text underlying)
        self.interpretation_text.tag_config("heading", foreground="#3B82F6", spacing1=15, spacing3=5)

    def choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccionar dataset",
            filetypes=[
                ("Archivos compatibles", "*.csv *.xlsx"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if file_path:
            self.load_file(Path(file_path))

    def load_demo_dataset(self) -> None:
        path = Path(__file__).resolve().parents[1] / "data" / "SeoulBikeData.csv"
        if not path.exists():
            messagebox.showerror("Dataset no encontrado", f"No se encuentra el archivo de demostración:\n{path}")
            return
        self.load_file(path)

    def load_file(self, path: Path) -> None:
        self.status_var.set(f"Cargando {path.name}…")
        self.update_idletasks()
        try:
            data = load_dataset(path)
            profile = profile_dataset(data)
        except DataLoadError as exc:
            self.status_var.set("Error durante la carga")
            messagebox.showerror("No se pudo cargar el dataset", str(exc))
            return
        except Exception as exc:
            self.status_var.set("Error inesperado")
            messagebox.showerror("Error inesperado", str(exc))
            return

        self.data = data
        self.profile = profile
        self.file_path = path
        self.file_label.configure(text=path.name)
        
        self.variable_combo.configure(values=profile.numeric_columns, state="normal")
        self.variable.set(profile.numeric_columns[0])
        self.selection_hint.configure(text=f"{profile.rows:,} filas · {len(profile.numeric_columns)} var numéricas")
        
        self._populate_preview()
        self._update_profile()
        self.analyze_selected()
        self.status_var.set(f"Dataset cargado · {profile.rows:,} registros · {profile.columns} columnas")

    def _populate_preview(self) -> None:
        assert self.data is not None
        columns = [str(column) for column in self.data.columns]
        self.data_tree.delete(*self.data_tree.get_children())
        self.data_tree.configure(columns=columns)
        for column in columns:
            self.data_tree.heading(column, text=column)
            width = min(220, max(100, len(column) * 9))
            self.data_tree.column(column, width=width, minwidth=80, anchor="center")
        for row in self.data.head(500).itertuples(index=False, name=None):
            values = ["" if pd.isna(value) else self._format_cell(value) for value in row]
            self.data_tree.insert("", "end", values=values)
        self.preview_label.configure(text=f"Mostrando {min(len(self.data), 500):,} de {len(self.data):,} registros.")

    def _update_profile(self) -> None:
        assert self.profile is not None
        p = self.profile
        self.card_values["Registros"].configure(text=f"{p.rows:,}")
        self.card_values["Columnas"].configure(text=str(p.columns))
        self.card_values["Numéricas"].configure(text=str(len(p.numeric_columns)))
        self.card_values["Datos faltantes"].configure(text=f"{p.missing_values:,}")

        lines = [
            f"DIMENSIONES",
            f"{p.rows:,} filas × {p.columns} columnas\n",
            f"VARIABLES NUMÉRICAS ({len(p.numeric_columns)})",
            ", ".join(p.numeric_columns) + "\n",
            f"VARIABLES NO NUMÉRICAS ({len(p.categorical_columns)})",
            (", ".join(p.categorical_columns) or "Ninguna") + "\n",
            f"CALIDAD DE DATOS",
            f"• {p.missing_values:,} valores faltantes",
            f"• {p.duplicated_rows:,} filas duplicadas",
            f"• {p.memory_mb:.2f} MB en memoria"
        ]
        self.profile_text.configure(state="normal")
        self.profile_text.delete("1.0", "end")
        self.profile_text.insert("1.0", "\n".join(lines))
        self.profile_text.configure(state="disabled")

    def _on_variable_selected(self, _event=None) -> None:
        self.analyze_selected()

    def analyze_selected(self) -> None:
        if self.data is None or not self.variable.get() or self.variable.get() == "-":
            return
        self.status_var.set(f"Analizando {self.variable.get()}…")
        self.update_idletasks()
        try:
            self.analysis = analyze_variable(self.data, self.variable.get())
        except Exception as exc:
            messagebox.showerror("No se pudo analizar la variable", str(exc))
            self.status_var.set("Error durante el análisis")
            return

        self._update_metrics()
        self._update_frequency()
        self._update_charts()
        self._update_interpretation()
        self.card_values["Atípicos"].configure(text=f"{int(self.analysis.metrics['Valores atípicos']):,}")
        self.status_var.set(f"Análisis actualizado · Variable: {self.analysis.variable}")

    def _update_metrics(self) -> None:
        assert self.analysis is not None
        self.metrics_tree.delete(*self.metrics_tree.get_children())
        for name, value in self.analysis.metrics.items():
            label = f"{name} (%)" if name == "Coeficiente de variación" else name
            self.metrics_tree.insert("", "end", values=(label, self._format_metric(value)))

    def _update_frequency(self) -> None:
        assert self.analysis is not None
        table = self.analysis.frequency_table
        columns = list(table.columns)
        self.frequency_tree.delete(*self.frequency_tree.get_children())
        self.frequency_tree.configure(columns=columns)
        for column in columns:
            self.frequency_tree.heading(column, text=column)
            width = 190 if column == "Clase" else max(125, len(column) * 8)
            self.frequency_tree.column(column, width=width, anchor="center")
        for row in table.itertuples(index=False, name=None):
            self.frequency_tree.insert("", "end", values=[self._format_cell(value) for value in row])
        
        method = "Datos agrupados (Regla de Sturges)" if self.analysis.grouped else "Frecuencias por valor exacto"
        self.frequency_note.configure(text=f"{method} · {len(table)} clases")

    def _update_charts(self) -> None:
        assert self.analysis is not None
        if self.chart_placeholder is not None:
            self.chart_placeholder.destroy()
            self.chart_placeholder = None
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        if self.boxplot_canvas:
            self.boxplot_canvas.get_tk_widget().destroy()

        figure = create_analysis_figure(self.analysis)
        self.chart_canvas = FigureCanvasTkAgg(figure, master=self.main_charts_frame)
        self.chart_canvas.draw()
        chart_widget = self.chart_canvas.get_tk_widget()
        chart_widget.configure(background="#2B2B2B", highlightthickness=0)
        # Mantener la altura natural del lienzo evita que el Tabview anidado
        # lo estire por debajo del borde visible de la ventana.
        chart_widget.pack(anchor="n", expand=False)

        boxplot = create_boxplot_figure(self.analysis)
        self.boxplot_canvas = FigureCanvasTkAgg(boxplot, master=self.boxplot_frame)
        self.boxplot_canvas.draw()
        boxplot_widget = self.boxplot_canvas.get_tk_widget()
        boxplot_widget.configure(background="#2B2B2B", highlightthickness=0)
        boxplot_widget.pack(anchor="n", expand=False)

    def _update_interpretation(self) -> None:
        assert self.analysis is not None and self.data is not None
        sections = generate_interpretation(self.analysis, self.data)
        self.interpretation_text.configure(state="normal")
        self.interpretation_text.delete("1.0", "end")
        for heading, body in sections:
            self.interpretation_text.insert("end", heading + "\n", "heading")
            self.interpretation_text.insert("end", body + "\n\n")
        self.interpretation_text.configure(state="disabled")

    def export_frequency(self) -> None:
        if self.analysis is None:
            messagebox.showinfo("Sin análisis", "Primero cargue y analice un dataset.")
            return
        initial = f"frecuencias_{self._safe_name(self.analysis.variable)}.csv"
        path = filedialog.asksaveasfilename(
            title="Exportar tabla de frecuencias",
            defaultextension=".csv",
            initialfile=initial,
            filetypes=[("CSV", "*.csv")],
        )
        if path:
            self.analysis.frequency_table.to_csv(path, index=False, encoding="utf-8-sig")
            self.status_var.set(f"Tabla exportada · {Path(path).name}")
            messagebox.showinfo("Exportación completa", f"Archivo guardado en:\n{path}")

    def export_analysis(self) -> None:
        if self.analysis is None or self.data is None:
            messagebox.showinfo("Sin análisis", "Primero cargue y analice un dataset.")
            return
        initial = f"analisis_{self._safe_name(self.analysis.variable)}.pdf"
        path = filedialog.asksaveasfilename(
            title="Exportar reporte",
            defaultextension=".pdf",
            initialfile=initial,
            filetypes=[("PDF", "*.pdf")],
        )
        if not path:
            return
        try:
            export_variable_report(
                path,
                self.file_path.name if self.file_path else "Dataset",
                self.data,
                self.analysis,
            )
        except Exception as exc:
            messagebox.showerror("No se pudo exportar el reporte", str(exc))
            return
        self.status_var.set(f"Reporte exportado · {Path(path).name}")
        messagebox.showinfo("Reporte generado", f"PDF guardado en:\n{path}")

    def show_about(self) -> None:
        messagebox.showinfo(
            "Acerca de StatLab",
            f"StatLab {__version__}\n\n"
            "Sistema dinámico de análisis estadístico descriptivo.\n"
            "Admite archivos CSV y Excel, calcula distribuciones, medidas,\n"
            "gráficos, atípicos e interpretaciones automáticas.\n\n"
            "Proyecto académico de Probabilidad y Procesos Estocásticos."
        )

    @staticmethod
    def _format_metric(value: float | int | str) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return f"{value:,}"
        if math.isnan(value):
            return "No calculable"
        return f"{value:,.4f}"

    @staticmethod
    def _format_cell(value: object) -> str:
        if isinstance(value, float):
            if math.isnan(value):
                return ""
            return f"{value:,.4f}".rstrip("0").rstrip(".")
        return str(value)

    @staticmethod
    def _safe_name(value: str) -> str:
        return "".join(
            character if character.isalnum() else "_" for character in value
        ).strip("_")

"""Generate page."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QProgressBar, QTextEdit, QTableWidget,
                               QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
                               QSplitter, QTabWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
import asyncio
import json

from answer_dataset.pipeline.generator import Generator
from answer_dataset.exporters.jsonl_exporter import JSONLExporter
from answer_dataset.exporters.json_exporter import JSONExporter
from answer_dataset.exporters.csv_exporter import CSVExporter


class GenerateWorker(QThread):
    progress = Signal(int, int, str)
    log = Signal(str)
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, generator, documents):
        super().__init__()
        self.generator = generator
        self.documents = documents
        self._stopped = False
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            rows = loop.run_until_complete(
                self.generator.generate(self.documents, self._progress, self._log)
            )
            loop.close()
            if not self._stopped:
                self.finished.emit(rows)
            else:
                self.finished.emit(rows)
        except Exception as e:
            if not self._stopped:
                self.error.emit(str(e))
    
    def _progress(self, current, total, msg):
        if not self._stopped:
            self.progress.emit(current, total, msg)
    
    def _log(self, msg):
        if not self._stopped:
            self.log.emit(msg)
    
    def stop(self):
        self._stopped = True
        if self.generator:
            self.generator.cancel()
        if self.isRunning():
            self.requestInterruption()


class GeneratePage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.rows = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Generate Dataset")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Start Generation")
        self.generate_btn.clicked.connect(self.start_generation)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Results tab
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Index", "Data"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        self.tabs.addTab(results_widget, "Results")
        
        # Log tab
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.tabs.addTab(log_widget, "Log")
        
        # Stats tab
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        self.stats_label = QLabel("No data")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        self.tabs.addTab(stats_widget, "Statistics")
        
        layout.addWidget(self.tabs)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_jsonl_btn = QPushButton("Export JSONL")
        self.export_jsonl_btn.clicked.connect(lambda: self.export("jsonl"))
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(lambda: self.export("json"))
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export("csv"))
        export_layout.addWidget(self.export_jsonl_btn)
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)
    
    def start_generation(self):
        # Get parent window to access other pages
        main_win = self.window()
        if not hasattr(main_win, 'provider_page'):
            QMessageBox.warning(self, "Error", "Cannot access configuration")
            return
        
        provider_config = main_win.provider_page.get_config()
        gen_config = main_win.format_page.get_config()
        documents = main_win.documents_page.get_documents()
        
        if not documents:
            QMessageBox.warning(self, "Error", "Please add documents first")
            return
        if not provider_config.model:
            QMessageBox.warning(self, "Error", "Please select a model")
            return
        
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.rows = []
        self.results_table.setRowCount(0)
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.tabs.setCurrentIndex(1)  # Show log tab
        
        self.generator = Generator(provider_config, gen_config)
        self.worker = GenerateWorker(self.generator, documents)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.on_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def stop_generation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.on_log("Stopping generation...")
            self.stop_btn.setEnabled(False)
            self.progress_label.setText("Stopping...")
    def on_progress(self, current, total, msg):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current + 1)
        self.progress_label.setText(msg)
    
    def on_log(self, msg):
        self.log_text.append(f"[{QTimer().remainingTime() if False else ''}] {msg}")
        # Simple logging
        from datetime import datetime
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def on_finished(self, rows):
        self.rows = rows
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_label.setText(f"Completed - {len(rows)} rows generated")
        self.update_results()
        self.update_stats()
        self.tabs.setCurrentIndex(0)
    
    def on_error(self, err):
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.on_log(f"Error: {err}")
        QMessageBox.critical(self, "Error", err)
    
    def update_results(self):
        self.results_table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            data_str = json.dumps(row.data, ensure_ascii=False)
            if len(data_str) > 200:
                data_str = data_str[:200] + "..."
            self.results_table.setItem(i, 1, QTableWidgetItem(data_str))
    
    def update_stats(self):
        if not self.rows:
            self.stats_label.setText("No data")
            return
        stats = self.generator.get_stats() if hasattr(self, 'generator') else {}
        text = f"Total rows: {len(self.rows)}\n"
        text += f"Input tokens: {stats.get('input_tokens', 0)}\n"
        text += f"Output tokens: {stats.get('output_tokens', 0)}\n"
        text += f"Total tokens: {stats.get('total_tokens', 0)}\n"
        self.stats_label.setText(text)
    
    def export(self, fmt):
        if not self.rows:
            QMessageBox.warning(self, "Error", "No rows to export")
            return
        
        ext_map = {"jsonl": "JSONL (*.jsonl)", "json": "JSON (*.json)", "csv": "CSV (*.csv)"}
        path, _ = QFileDialog.getSaveFileName(self, "Export Dataset", f"dataset.{fmt}", ext_map[fmt])
        if not path:
            return
        
        try:
            if fmt == "jsonl":
                JSONLExporter.export_from_dataset_rows(self.rows, path)
            elif fmt == "json":
                JSONExporter.export_from_dataset_rows(self.rows, path)
            elif fmt == "csv":
                CSVExporter.export_from_dataset_rows(self.rows, path)
            QMessageBox.information(self, "Success", f"Exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

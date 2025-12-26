import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QStatusBar
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PowerRegressionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Степенева регресія y = a * x^b")
        self.setFixedSize(900, 650)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # поля вводу
        self.label_x = QLabel("X:")
        self.input_x = QLineEdit("1, 2, 3, 4, 5, 6, 7, 8")
        self.label_y = QLabel("Y:")
        self.input_y = QLineEdit("56.9, 67.3, 81.6, 201, 240, 474, 490, 518")

        self.btn_calc = QPushButton("Обчислити степеневу регресію")
        self.btn_calc.clicked.connect(self.calculate_regression)

        self.btn_save = QPushButton("Зберегти результати")
        self.btn_save.clicked.connect(self.save_results)

        # таблиця результатів
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Параметр", "Значення"])

        # поле для графіка
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # розташування елементів
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.label_x)
        input_layout.addWidget(self.input_x)
        input_layout.addWidget(self.label_y)
        input_layout.addWidget(self.input_y)
        input_layout.addWidget(self.btn_calc)
        input_layout.addWidget(self.btn_save)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.canvas)

        central_widget.setLayout(main_layout)

        # рядок стану
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def calculate_regression(self):
        try:
            x_values = np.array([float(i.strip()) for i in self.input_x.text().split(",")])
            y_values = np.array([float(i.strip()) for i in self.input_y.text().split(",")])
        except ValueError:
            self.status_bar.showMessage("Помилка: введіть числа через кому!")
            return

        if len(x_values) != len(y_values):
            self.status_bar.showMessage("Помилка: кількість X і Y має співпадати!")
            return

        if np.any(x_values <= 0) or np.any(y_values <= 0):
            self.status_bar.showMessage("Помилка: усі значення X та Y мають бути > 0 для логарифмування!")
            return

        # Лінійне перетворення: ln(y) = ln(a) + b * ln(x)
        X = np.log(x_values)
        Y = np.log(y_values)

        n = len(X)
        b = (n * np.sum(X * Y) - np.sum(X) * np.sum(Y)) / (n * np.sum(X ** 2) - (np.sum(X)) ** 2)
        A = (np.sum(Y) - b * np.sum(X)) / n
        a = np.exp(A)

        # Обчислення прогнозних значень і коефіцієнта детермінації
        y_pred = a * x_values ** b
        ss_res = np.sum((y_values - y_pred) ** 2)
        ss_tot = np.sum((y_values - np.mean(y_values)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        # Оновлення таблиці
        self.table.setRowCount(3)
        self.table.setItem(0, 0, QTableWidgetItem("Коефіцієнт a"))
        self.table.setItem(0, 1, QTableWidgetItem(f"{a:.6f}"))
        self.table.setItem(1, 0, QTableWidgetItem("Коефіцієнт b"))
        self.table.setItem(1, 1, QTableWidgetItem(f"{b:.6f}"))
        self.table.setItem(2, 0, QTableWidgetItem("R²"))
        self.table.setItem(2, 1, QTableWidgetItem(f"{r2:.6f}"))

        # Побудова графіка
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.scatter(x_values, y_values, color="blue", label="Експериментальні точки")
        ax.plot(x_values, y_pred, color="red", label=f"y = {a:.2f} * x^{b:.2f}")
        ax.set_title("Степенева регресія y = a * x^b")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

        self.status_bar.showMessage("Обчислення завершено!")
        self.results = {"a": a, "b": b, "R2": r2}

    def save_results(self):
        if not hasattr(self, "results"):
            self.status_bar.showMessage("Спочатку виконайте обчислення!")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти результати", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write("Результати степеневої регресії y = a * x^b\n\n")
                f.write(f"a = {self.results['a']:.6f}\n")
                f.write(f"b = {self.results['b']:.6f}\n")
                f.write(f"R² = {self.results['R2']:.6f}\n")
            self.status_bar.showMessage("Результати збережено.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerRegressionApp()
    window.show()
    sys.exit(app.exec())

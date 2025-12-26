import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QStatusBar
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# -------- Диференціальне рівняння (варіант 5) --------
def f(x, y):
    return (1 + y) / np.tan(x)


# аналітичний розв’язок
def y_exact(x):
    C = 1 / np.sin(1)
    return C * np.sin(x) - 1


# метод Ейлера
def euler(x0, y0, h, n):
    x = np.zeros(n + 1)
    y = np.zeros(n + 1)
    x[0], y[0] = x0, y0

    for i in range(n):
        y[i + 1] = y[i] + h * f(x[i], y[i])
        x[i + 1] = x[i] + h

    return x, y


# метод Рунге–Кутта 4-го порядку
def runge_kutta_4(x0, y0, h, n):
    x = np.zeros(n + 1)
    y = np.zeros(n + 1)
    x[0], y[0] = x0, y0

    for i in range(n):
        k1 = f(x[i], y[i])
        k2 = f(x[i] + h/2, y[i] + h*k1/2)
        k3 = f(x[i] + h/2, y[i] + h*k2/2)
        k4 = f(x[i] + h, y[i] + h*k3)

        y[i + 1] = y[i] + h * (k1 + 2*k2 + 2*k3 + k4) / 6
        x[i + 1] = x[i] + h

    return x, y


# ---------------- GUI ----------------
class DifferentialEquationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Розв’язування ДР (Ейлер, Рунге–Кутта)")
        self.setFixedSize(900, 650)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Поля вводу
        self.input_x0 = QLineEdit("1")
        self.input_y0 = QLineEdit("0")
        self.input_x_end = QLineEdit("2")

        self.btn_calc = QPushButton("Обчислити")
        self.btn_calc.clicked.connect(self.calculate)

        self.btn_save = QPushButton("Зберегти результати")
        self.btn_save.clicked.connect(self.save_results)

        # Підписи
        layout_inputs = QHBoxLayout()
        layout_inputs.addWidget(QLabel("x₀:"))
        layout_inputs.addWidget(self.input_x0)
        layout_inputs.addWidget(QLabel("y(x₀):"))
        layout_inputs.addWidget(self.input_y0)
        layout_inputs.addWidget(QLabel("x кінцеве:"))
        layout_inputs.addWidget(self.input_x_end)
        layout_inputs.addWidget(self.btn_calc)
        layout_inputs.addWidget(self.btn_save)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "x", "Ейлер (h=0.1)", "РК4 (h=0.1)", "Аналітичний"
        ])

        # Графік
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # Головний layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_inputs)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.canvas)

        central_widget.setLayout(main_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def calculate(self):
        try:
            x0 = float(self.input_x0.text())
            y0 = float(self.input_y0.text())
            x_end = float(self.input_x_end.text())
        except ValueError:
            self.status_bar.showMessage("Помилка введення!")
            return

        h = 0.1
        n = int((x_end - x0) / h)

        x_e, y_e = euler(x0, y0, h, n)
        x_rk, y_rk = runge_kutta_4(x0, y0, h, n)
        y_an = y_exact(x_e)

        # Таблиця
        self.table.setRowCount(len(x_e))
        for i in range(len(x_e)):
            self.table.setItem(i, 0, QTableWidgetItem(f"{x_e[i]:.4f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{y_e[i]:.6f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{y_rk[i]:.6f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{y_an[i]:.6f}"))

        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x_plot = np.linspace(x0, x_end, 500)
        ax.plot(x_plot, y_exact(x_plot), 'k', label="Аналітичний")
        ax.plot(x_e, y_e, 'o--', label="Ейлер h=0.1")
        ax.plot(x_rk, y_rk, 's-', label="Рунге–Кутта 4")

        ax.set_title("y′ = (1 + y) / tan(x)")
        ax.grid(True)
        ax.legend()

        self.canvas.draw()

        self.results = list(zip(x_e, y_e, y_rk, y_an))
        self.status_bar.showMessage("Обчислення виконано")

    def save_results(self):
        if not hasattr(self, "results"):
            self.status_bar.showMessage("Немає даних для збереження")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write("x\tEuler\tRK4\tExact\n")
                for row in self.results:
                    f.write(f"{row[0]:.6f}\t{row[1]:.6f}\t{row[2]:.6f}\tz{row[3]:.6f}\n")

            self.status_bar.showMessage("Файл збережено")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DifferentialEquationApp()
    window.show()
    sys.exit(app.exec())

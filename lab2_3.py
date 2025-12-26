import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QStatusBar
)
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# функція для інтегрування
def f(x):
    return 1 / math.sqrt(12 * x ** 2 + 0.5)


# метод прямокутників
def rectangle_method(a, b, n):
    h = (b - a) / n
    x = np.linspace(a + h/2, b - h/2, n)  # середні прямокутники
    y = [f(xi) for xi in x]
    return h * sum(y)


# метод трапецій
def trapezoid_method(a, b, n):
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = [f(xi) for xi in x]
    return (h / 2) * (y[0] + 2 * sum(y[1:-1]) + y[-1])


# метод Монте-Карло
def monte_carlo_method(a, b, n):
    x = np.random.uniform(a, b, n)
    y = [f(xi) for xi in x]
    return (b - a) * np.mean(y)


# головне вікно
class IntegralSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Integral Solver – 1 / √(12x² + 0.5)")
        self.setFixedSize(850, 650)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # поля вводу
        self.label_a = QLabel("Початок a:")
        self.input_a = QLineEdit("0.6")
        self.label_b = QLabel("Кінець b:")
        self.input_b = QLineEdit("1.4")
        self.label_n = QLabel("Кількість підінтервалів N:")
        self.input_n = QLineEdit("10")

        self.btn_calc = QPushButton("Обчислити")
        self.btn_calc.clicked.connect(self.calculate)

        self.btn_save = QPushButton("Зберегти результат")
        self.btn_save.clicked.connect(self.save_results)

        # таблиця результатів
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["N", "Прямокутники", "Трапеції", "Монте-Карло"])

        # поле для графіка
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # розташування елементів
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.label_a)
        input_layout.addWidget(self.input_a)
        input_layout.addWidget(self.label_b)
        input_layout.addWidget(self.input_b)
        input_layout.addWidget(self.label_n)
        input_layout.addWidget(self.input_n)
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

    def calculate(self):
        a = float(self.input_a.text())
        b = float(self.input_b.text())

        # значення N для обчислення
        Ns = [10, 20, 50, 100, 1000]
        self.table.setRowCount(len(Ns))

        results = []
        for i, n in enumerate(Ns):
            rect = rectangle_method(a, b, n)
            trap = trapezoid_method(a, b, n)
            monte = monte_carlo_method(a, b, n)
            self.table.setItem(i, 0, QTableWidgetItem(str(n)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{rect:.6f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{trap:.6f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{monte:.6f}"))
            results.append((n, rect, trap, monte))

        self.results = results
        self.plot_function(a, b)
        self.status_bar.showMessage("Обчислення завершено!")

    def plot_function(self, a, b):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_vals = np.linspace(a, b, 400)
        y_vals = [f(x) for x in x_vals]
        ax.plot(x_vals, y_vals, color="blue", label="f(x) = 1 / √(12x² + 0.5)")
        ax.set_title(f"Графік функції на [{a}, {b}]")
        ax.legend()
        self.canvas.draw()

    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти результати", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as file:
                file.write("Результати чисельного інтегрування:\n")
                file.write("f(x) = 1 / √(12x² + 0.5)\n\n")
                file.write("N\tПрямокутники\tТрапеції\tМонте-Карло\n")
                for n, rect, trap, monte in self.results:
                    file.write(f"{n}\t{rect:.6f}\t{trap:.6f}\t{monte:.6f}\n")
            self.status_bar.showMessage("Результати збережено.")


# запуск програми
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IntegralSolver()
    window.show()
    sys.exit(app.exec())

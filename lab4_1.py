import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QStatusBar
)
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def lagrange_interpolation(x, y, xi):
    # Обчислення значень полінома Лагранжа у точках xi.
    # x, y — вузли інтерполяції, xi — точки для обчислення.
    n = len(x)
    yi = np.zeros_like(xi, dtype=float)
    for k in range(len(xi)):
        s = 0.0
        for i in range(n):
            # обчислити базисний многочлен L_i(xi[k])
            L = 1.0
            for j in range(n):
                if j != i:
                    L *= (xi[k] - x[j]) / (x[i] - x[j])
            s += y[i] * L
        yi[k] = s
    return yi


class LagrangeInterpolationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Інтерполяція поліномом Лагранжа")
        self.setFixedSize(900, 650)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Поля вводу вузлів інтерполяції
        self.label_x = QLabel("Вузли x (через кому):")
        self.input_x = QLineEdit("1, 2, 3, 4, 5")  # приклад

        self.label_y = QLabel("Вузли y = f(x) (через кому):")
        self.input_y = QLineEdit("1, 4, 9, 16, 25")  # приклад

        self.btn_calc = QPushButton("Обчислити інтерполяцію")
        self.btn_calc.clicked.connect(self.calculate_interpolation)

        self.btn_save = QPushButton("Зберегти результати")
        self.btn_save.clicked.connect(self.save_results)

        # Таблиця для відображення результатів
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["x_i", "f(x_i) (інтерполяція)"])

        # Поле для графіка
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # Розташування елементів
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

        # Рядок стану
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def calculate_interpolation(self):
        try:
            x_nodes = np.array([float(i.strip()) for i in self.input_x.text().split(",")])
            y_nodes = np.array([float(i.strip()) for i in self.input_y.text().split(",")])
        except ValueError:
            self.status_bar.showMessage("Помилка: введіть коректні числа через кому!")
            return

        if len(x_nodes) != len(y_nodes):
            self.status_bar.showMessage("Помилка: кількість x і y має співпадати!")
            return

        a, b = np.min(x_nodes), np.max(x_nodes)
        h = (b - a) / 10

        x_eval = np.array([a + h * i for i in range(11)])  # 11 точок
        y_eval = lagrange_interpolation(x_nodes, y_nodes, x_eval)

        # Оновити таблицю
        self.table.setRowCount(len(x_eval))
        for i in range(len(x_eval)):
            self.table.setItem(i, 0, QTableWidgetItem(f"{x_eval[i]:.6f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{y_eval[i]:.6f}"))

        # Побудова графіка
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Малюємо вузли інтерполяції
        ax.scatter(x_nodes, y_nodes, color="blue", label="Вузли інтерполяції")

        # Малюємо інтерполяційний поліном (плавна крива)
        x_smooth = np.linspace(a, b, 500)
        y_smooth = lagrange_interpolation(x_nodes, y_nodes, x_smooth)
        ax.plot(x_smooth, y_smooth, color="red", label="Поліном Лагранжа")

        ax.set_title("Інтерполяція поліномом Лагранжа")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

        self.status_bar.showMessage("Інтерполяція виконана!")

        # Зберігаємо результати для експорту
        self.results = list(zip(x_eval, y_eval))

    def save_results(self):
        if not hasattr(self, "results"):
            self.status_bar.showMessage("Спочатку виконайте обчислення!")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти результати", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write("Результати інтерполяції поліномом Лагранжа\n\n")
                f.write("x_i\tf(x_i)\n")
                for x_val, y_val in self.results:
                    f.write(f"{x_val:.6f}\t{y_val:.6f}\n")
            self.status_bar.showMessage("Результати збережено.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LagrangeInterpolationApp()
    window.show()
    sys.exit(app.exec())

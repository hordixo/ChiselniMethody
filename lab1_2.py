import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QStatusBar, QComboBox
)
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Функція рівняння
def f(x):
    # if abs(math.sin(x)) < 1e-3:  # пропускаємо точки де функція не визначена
    #     return None
    #  return 1 / math.tan(x) - (1 / x - x / 2)
    return math.cos(x) - x

    # if abs(math.sin(x)) < 1e-2 or abs(x) < 1e-3:
    #     return None
    # try:
    #     return 1 / math.tan(x) - (1 / x - x / 2)
    # except:
    #     return None



# Метод бісекції
def bisection(a, b, eps):
    results = []
    if f(a) * f(b) > 0:
        return None, []
    while abs(b - a) > eps:
        c = (a + b) / 2
        results.append((a, b, c, f(c)))
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    x_root = (a + b) / 2
    return x_root, results


# Метод простої ітерації
def iteration_method(f, x0, eps=1e-6, max_iter=1000):
    """
    x_{n+1} = g(x_n), де g(x) = x + f(x) (можна змінити, залежно від рівняння)
    Повертає кортеж (корінь або None, список ітерацій)
    """
    results = []
    x = x0
    for i in range(max_iter):
        # g(x) = x + f(x) (стандартний підхід для простої ітерації)
        try:
            x_next = x + f(x)
        except:
            return None, results
        results.append((x, x_next))
        if abs(x_next - x) < eps:
            return x_next, results
        x = x_next
    return None, results


def newton_method(x0, eps, max_iter=1000):
    """
    Метод Ньютона: x_{n+1} = x_n - f(x_n)/f'(x_n)
    """
    def df(x):
        h = 1e-6  # малий крок для чисельної похідної
        if f(x + h) is None or f(x - h) is None:
            return None
        return (f(x + h) - f(x - h)) / (2 * h)

    x = x0
    for _ in range(max_iter):
        fx = f(x)
        dfx = df(x)
        if fx is None or dfx is None or dfx == 0:
            return None
        x_next = x - fx / dfx
        if abs(x_next - x) < eps:
            return x_next
        x = x_next
    return x


# --- ГОЛОВНЕ ВІКНО ---
class EquationSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Equation Solver – x² - sin(5x) = 0")
        self.setFixedSize(850, 650)
        self.initUI()

    def initUI(self):
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Поля вводу
        self.label_a = QLabel("Початок пошуку:")
        self.input_a = QLineEdit("1") 
        self.label_b = QLabel("Кінець пошуку:")
        self.input_b = QLineEdit("6")
        self.label_eps = QLabel("Точність ε:")
        self.input_eps = QLineEdit("0.0001")

        self.btn_calc = QPushButton("Обчислити")
        self.btn_calc.clicked.connect(self.find_intervals)

        self.btn_solve = QPushButton("Знайти корінь і побудувати графік")
        self.btn_solve.clicked.connect(self.calculate)
        self.btn_solve.setEnabled(False)

        self.btn_save = QPushButton("Зберегти результат")
        self.btn_save.clicked.connect(self.save_results)

        # Список відрізків
        self.combo_intervals = QComboBox()

        # Таблиця результатів
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["a", "b", "c", "f(c)"])

        # Поле для графіка
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # Розташування елементів
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.label_a)
        input_layout.addWidget(self.input_a)
        input_layout.addWidget(self.label_b)
        input_layout.addWidget(self.input_b)
        input_layout.addWidget(self.label_eps)
        input_layout.addWidget(self.input_eps)
        input_layout.addWidget(self.btn_calc)
        input_layout.addWidget(self.btn_solve)
        input_layout.addWidget(self.btn_save)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(QLabel("Виберіть відрізок з коренем:"))
        main_layout.addWidget(self.combo_intervals)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.canvas)

        central_widget.setLayout(main_layout)

        # Рядок стану
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # --- 1. Пошук інтервалів з коренями ---
    def find_intervals(self):
        a = float(self.input_a.text())
        b = float(self.input_b.text())
        eps = float(self.input_eps.text())

        step = 0.5  # крок пошуку
        x = a
        intervals = []

        while x < b:
            x_next = x + step
            if f(x) * f(x_next) < 0:
                intervals.append((x, x_next))
            x = x_next

            

        if not intervals:
            self.status_bar.showMessage("Коренів не знайдено на цьому проміжку.")
            self.btn_solve.setEnabled(False)
            self.combo_intervals.clear()
        else:
            self.status_bar.showMessage(f"Знайдено {len(intervals)} коренів.")
            self.combo_intervals.clear()
            for i, (a_i, b_i) in enumerate(intervals):
                self.combo_intervals.addItem(f"[{a_i:.2f}, {b_i:.2f}]")
            self.btn_solve.setEnabled(True)
            self.intervals = intervals

    # --- 2. Обчислення обраного кореня ---
    def calculate(self):
        eps = float(self.input_eps.text())
        idx = self.combo_intervals.currentIndex()
        a, b = self.intervals[idx]

        # Метод дихотомії
        root_bis, results = bisection(a, b, eps)
        if root_bis is None:
            self.status_bar.showMessage("На цьому відрізку не знайдено корінь.")
            return

        # Метод ітерацій
        x0 = (a + b) / 2
        root_iter, results_iter = iteration_method(f, x0, eps)

        # # Метод Ньютона
        root_newton = newton_method(x0, eps)

        # # Вивід у статус-бар
        # self.status_bar.showMessage(
        #     f"Бісекція: x = {root_bis:.6f} | Ітерації: x = {root_iter:.6f} | Ньютон: x = {root_newton:.6f}"
        # )

        msg = []
        msg.append(f"Бісекція: x = {root_bis:.3f}")
        if root_iter is not None:
            msg.append(f"Ітерації: x = {root_iter:.3f}")
        else:
            msg.append("Ітерації: не збігається")

        if root_newton is not None:
            msg.append(f"Ньютон: x = {root_newton:.3f}")
        else:
            msg.append("Ньютон: не збігається")

        self.status_bar.showMessage(" | ".join(msg))

        # Таблиця результатів
        self.table.setRowCount(len(results))
        for i, (a_i, b_i, c, fc) in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(f"{a_i:.6f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{b_i:.6f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{c:.6f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{fc:.6f}"))

        # Побудова графіка
        self.plot_function(a, b, root_bis)

        self.results = results
        self.root = root_bis

    # --- 3. Побудова графіка ---
    def plot_function(self, a, b, root):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_vals = np.linspace(a, b, 400)
        y_vals = [f(x) for x in x_vals]
        ax.plot(x_vals, y_vals, label="f(x) = x² - sin(5x)")
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(root, color='red', linestyle='--', label=f"x = {root:.4f}")
        ax.legend()
        ax.set_title(f"Графік на відрізку [{a:.2f}, {b:.2f}]")
        self.canvas.draw()

    # --- 4. Збереження результатів ---
    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти файл", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w") as f:
                f.write("Результати обчислень (метод бісекції)\n")
                f.write(f"Корінь: x = {self.root:.6f}\n\n")
                f.write("a\tb\tc\tf(c)\n")
                for a_i, b_i, c, fc in self.results:
                    f.write(f"{a_i:.6f}\t{b_i:.6f}\t{c:.6f}\t{fc:.6f}\n")
            self.status_bar.showMessage("Результати збережено.")


# --- Запуск програми ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EquationSolver()
    window.show()
    sys.exit(app.exec())

import psycopg2
import matplotlib.pyplot as plt
import os
from config.config import db_config
import numpy as np

# Создаем папку для сохранения графиков, если ее нет
os.makedirs('plots', exist_ok=True)


def execute_query(query, params=None):
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            return columns, data


def save_plot(filename):
    """Сохраняет текущий график в файл и очищает фигуру"""
    plt.tight_layout()
    plt.savefig(f'plots/{filename}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"График сохранен как: plots/{filename}.png")


def plot_scatter_task_price_vs_grade():
    query = """
    SELECT 
        t.price AS task_price,
        AVG(wt.grade) AS average_grade
    FROM WrittenTask wt
    JOIN Task t ON wt.task_id = t.task_id
    GROUP BY t.price
    ORDER BY t.price;
    """
    columns, data = execute_query(query)

    # Конвертируем decimal.Decimal в float
    prices = [float(row[0]) for row in data]
    avg_grades = [float(row[1]) for row in data]

    plt.figure(figsize=(10, 6))
    plt.scatter(prices, avg_grades, color='coral', s=100, alpha=0.7)
    plt.xlabel('Цена задачи (сложность)')
    plt.ylabel('Средняя оценка')
    plt.title('Зависимость оценки от сложности задания')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Добавляем линию тренда (теперь с конвертированными float значениями)
    if len(prices) > 1:  # Проверяем, что есть достаточно точек для построения линии
        z = np.polyfit(prices, avg_grades, 1)
        p = np.poly1d(z)
        plt.plot(prices, p(prices), "r--")

    # Сохраняем в файл
    save_plot('task_price_vs_grade')


def plot_pie_chart_exam_statuses():
    query = """
    SELECT
    status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / total.total, 2) AS percentage
    FROM ExamResult
    CROSS JOIN (SELECT COUNT(*) AS total FROM ExamResult) AS total
    GROUP BY status, total.total;
    """
    columns, data = execute_query(query)

    statuses = [row[0] for row in data]
    counts = [row[1] for row in data]
    percentages = [row[2] for row in data]
    labels = [f"{status}\n{count} ({percentage}%)"
              for status, count, percentage in zip(statuses, counts, percentages)]

    plt.figure(figsize=(10, 8))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Распределение статусов экзаменов')
    plt.axis('equal')

    # Сохраняем в файл
    save_plot('exam_statuses_distribution')


def plot_bar_chart_students_per_school():
    query = """
    SELECT s.school_name, COUNT(p.person_id) AS student_count
    FROM School s
    JOIN Person p ON s.school_id = p.school_id
    WHERE p.role = 'SchoolChild'
    GROUP BY s.school_name
    ORDER BY student_count DESC;
    """
    columns, data = execute_query(query)

    schools = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(schools, counts, color='lightgreen')
    plt.xlabel('Школа')
    plt.ylabel('Количество учащихся')
    plt.title('Распределение количества учащихся по школам')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Добавляем значения на столбцы
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}',
                 ha='center', va='bottom')

    # Сохраняем в файл
    save_plot('students_per_school')


if __name__ == "__main__":
    # Примеры вызова функций
    print("1. Точечная диаграмма: зависимость оценки от сложности задания")
    plot_scatter_task_price_vs_grade()

    print("\n2. Круговая диаграмма статусов экзаменов")
    plot_pie_chart_exam_statuses()

    print("\n3. Столбчатая диаграмма распределения учащихся по школам")
    plot_bar_chart_students_per_school()
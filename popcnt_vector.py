def popcnt(x):
    """
    Функция для подсчёта количества установленных (1) битов в числе.

    Параметры:
        x (int): Входное число.

    Возвращает:
        int: Количество установленных битов.
    """
    return bin(x).count('1')


def apply_popcnt_to_vector(vector):
    """
    Применяет операцию popcnt поэлементно к вектору длины 8 и возвращает обновлённый вектор.

    Параметры:
        vector (list[int]): Список целых чисел длиной 8.

    Возвращает:
        list[int]: Обновлённый список, где каждый элемент заменён результатом операции popcnt.
    """
    if len(vector) != 8:
        raise ValueError("Vector length must be 8.")

    return [popcnt(x) for x in vector]


if __name__ == "__main__":
    # Пример использования
    input_vector = [3, 7, 15, 31, 63, 127, 255, 511]
    output_vector = apply_popcnt_to_vector(input_vector)
    print("Input Vector:", input_vector)
    print("Output Vector:", output_vector)
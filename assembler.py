import argparse  # Модуль для парсинга аргументов командной строки
import json  # Модуль для работы с JSON-форматом
import sys  # Модуль для взаимодействия с интерпретатором Python


def assemble_instruction(line):
    """
    Функция для ассемблирования одной строки исходного кода УВМ.

    Параметры:
        line (str): Одна строка исходного кода.

    Возвращает:
        tuple: Содержит бинарную инструкцию и словарь с полями инструкции.
               Если строка является комментарием или пустой, возвращает (None, None).

    Исключения:
        ValueError: Если обнаружены некорректные значения полей или неизвестный opcode.
    """
    # Разделяем строку на токены по пробелам и удаляем начальные/конечные пробелы
    tokens = line.strip().split()

    # Если строка пустая или начинается с символа '#', считаем её комментарием и пропускаем
    if not tokens or tokens[0].startswith('#'):
        return None, None

    # Получаем opcode (команду) и приводим его к верхнему регистру для стандартизации
    opcode = tokens[0].upper()

    if opcode == 'LOAD_CONST':
        # Формат команды: LOAD_CONST B C
        A = 10  # Устанавливаем фиксированное значение для поля A
        B = int(tokens[1])  # Получаем значение поля B из второго токена
        C = int(tokens[2])  # Получаем значение поля C из третьего токена

        # Проверяем, что значения полей находятся в допустимых диапазонах
        if not (0 <= A <= 0x7F):
            raise ValueError(f"Field A={A} out of range for LOAD_CONST (0-127)")
        if not (0 <= B <= 0x7):
            raise ValueError(f"Field B={B} out of range for LOAD_CONST (0-7)")
        if not (0 <= C <= 0xFFFFFF):
            raise ValueError(f"Field C={C} out of range for LOAD_CONST (0-16777215)")

        # Формируем бинарную инструкцию путем объединения полей A, B и C
        # A занимает биты 0-6, B — биты 7-9, C — биты 10-33
        instruction = (A << 0) | (B << 7) | (C << 10)

        # Преобразуем инструкцию в байты (5 байт) с порядком байтов 'little endian'
        binary = instruction.to_bytes(5, byteorder='little')

        # Создаем запись для лога с разобранными полями
        log_entry = {'A': A, 'B': B, 'C': C}

    elif opcode == 'READ_MEM':
        # Формат команды: READ_MEM B C
        A = 54  # Устанавливаем фиксированное значение для поля A
        B = int(tokens[1])  # Получаем значение поля B из второго токена
        C = int(tokens[2])  # Получаем значение поля C из третьего токена

        # Проверяем, что значения полей находятся в допустимых диапазонах
        if not (0 <= A <= 0x7F):
            raise ValueError(f"Field A={A} out of range for READ_MEM (0-127)")
        if not (0 <= B <= 0xFFFFFFFF):
            raise ValueError(f"Field B={B} out of range for READ_MEM (0-4294967295)")
        if not (0 <= C <= 0x7):
            raise ValueError(f"Field C={C} out of range for READ_MEM (0-7)")

        # Формируем бинарную инструкцию
        # A занимает биты 0-6, B — биты 7-38, C — биты 39-41
        instruction = (A & 0x7F) | ((B & 0xFFFFFFFF) << 7) | ((C & 0x7) << 39)

        # Преобразуем инструкцию в байты (6 байт) с порядком байтов 'little endian'
        binary = instruction.to_bytes(6, byteorder='little')

        # Создаем запись для лога с разобранными полями
        log_entry = {'A': A, 'B': B, 'C': C}

    elif opcode == 'WRITE_MEM':
        # Формат команды: WRITE_MEM B C
        A = 39  # Устанавливаем фиксированное значение для поля A
        B = int(tokens[1])  # Получаем значение поля B из второго токена
        C = int(tokens[2])  # Получаем значение поля C из третьего токена

        # Проверяем, что значения полей находятся в допустимых диапазонах
        if not (0 <= A <= 0x7F):
            raise ValueError(f"Field A={A} out of range for WRITE_MEM (0-127)")
        if not (0 <= B <= 0x7):
            raise ValueError(f"Field B={B} out of range for WRITE_MEM (0-7)")
        if not (0 <= C <= 0x7):
            raise ValueError(f"Field C={C} out of range for WRITE_MEM (0-7)")

        # Формируем бинарную инструкцию
        # A занимает биты 0-6, B — биты 7-9, C — биты 10-12
        instruction = (A & 0x7F) | ((B & 0x7) << 7) | ((C & 0x7) << 10)

        # Преобразуем инструкцию в байты (2 байта) с порядком байтов 'little endian'
        binary = instruction.to_bytes(2, byteorder='little')

        # Создаем запись для лога с разобранными полями
        log_entry = {'A': A, 'B': B, 'C': C}

    elif opcode == 'POPCNT':
        # Формат команды: POPCNT B C
        A = 18  # Устанавливаем фиксированное значение для поля A
        B = int(tokens[1])  # Получаем значение поля B из второго токена
        C = int(tokens[2])  # Получаем значение поля C из третьего токена

        # Проверяем, что значения полей находятся в допустимых диапазонах
        if not (0 <= A <= 0x7F):
            raise ValueError(f"Field A={A} out of range for POPCNT (0-127)")
        if not (0 <= B <= 0x7):
            raise ValueError(f"Field B={B} out of range for POPCNT (0-7)")
        if not (0 <= C <= 0xFFFFFFFF):
            raise ValueError(f"Field C={C} out of range for POPCNT (0-4294967295)")

        # Формируем бинарную инструкцию
        # A занимает биты 0-6, B — биты 7-9, C — биты 10-41
        instruction = (A & 0x7F) | ((B & 0x7) << 7) | ((C & 0xFFFFFFFF) << 10)

        # Преобразуем инструкцию в байты (6 байт) с порядком байтов 'little endian'
        binary = instruction.to_bytes(6, byteorder='little')

        # Создаем запись для лога с разобранными полями
        log_entry = {'A': A, 'B': B, 'C': C}

    else:
        # Если opcode не распознан, выбрасываем исключение
        raise ValueError(f"Unknown opcode: {opcode}")

    return binary, log_entry


def main():
    """
    Основная функция ассемблера.

    Выполняет следующие шаги:
        1. Парсит аргументы командной строки.
        2. Читает исходный файл с инструкциями УВМ.
        3. Ассемблирует каждую инструкцию в бинарный формат.
        4. Записывает бинарные данные в выходной файл.
        5. Если указан, записывает лог с разобранными полями инструкций в JSON-файл.

    При возникновении ошибки в процессе ассемблирования выводит сообщение об ошибке и завершает работу с кодом 1.
    """
    # Создаём парсер для обработки аргументов командной строки
    parser = argparse.ArgumentParser(description='Assembler for EVM.')

    # Определяем обязательные аргументы: путь к исходному файлу и путь к бинарному выходному файлу
    parser.add_argument('source_file', help='Path to the source code file.')
    parser.add_argument('binary_file', help='Path to the output binary file.')

    # Определяем необязательный аргумент: путь к лог-файлу
    parser.add_argument('--log_file', help='Path to the assembler log file.')

    # Парсим переданные аргументы
    args = parser.parse_args()

    # Инициализируем переменные для хранения бинарного кода и лог-записей
    binary_code = b''
    log_entries = []

    # Открываем исходный файл для чтения
    with open(args.source_file, 'r') as f:
        # Проходим по каждой строке в файле
        for line in f:
            try:
                # Ассемблируем текущую строку
                binary_instr, log_entry = assemble_instruction(line)

                # Если инструкция успешно ассемблирована, добавляем её бинарное представление
                if binary_instr:
                    binary_code += binary_instr

                # Если требуется логирование, добавляем запись в лог
                if log_entry:
                    log_entries.append(log_entry)

            except Exception as e:
                # В случае ошибки выводим сообщение об ошибке и завершаем работу с кодом 1
                print(f"Error assembling line: {line.strip()} - {e}", file=sys.stderr)
                sys.exit(1)

    # Записываем собранный бинарный код в выходной файл
    with open(args.binary_file, 'wb') as f:
        f.write(binary_code)

    # Если указан лог-файл, записываем туда лог-записи в формате JSON
    if args.log_file:
        with open(args.log_file, 'w') as f:
            json.dump(log_entries, f, indent=2)


# Проверяем, что скрипт запускается непосредственно, а не импортируется как модуль
if __name__ == '__main__':
    main()

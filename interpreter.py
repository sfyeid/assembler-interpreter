import argparse  # Модуль для парсинга аргументов командной строки
import json  # Модуль для работы с JSON-форматом
import sys  # Модуль для взаимодействия с интерпретатором Python


def popcnt(x):
    """
    Функция для подсчёта количества установленных (1) битов в числе.

    Параметры:
        x (int): Входное число.

    Возвращает:
        int: Количество установленных битов.
    """
    return bin(x).count('1')


def main():
    """
    Основная функция интерпретатора УВМ.

    Выполняет следующие шаги:
        1. Парсит аргументы командной строки.
        2. Инициализирует память и регистры УВМ.
        3. Загружает бинарный файл с командами УВМ.
        4. Исполняет команды последовательно, изменяя состояние регистров и памяти.
        5. Сохраняет значения из указанного диапазона памяти в файл-результат в формате JSON.

    Аргументы командной строки:
        binary_file (str): Путь к бинарному файлу с командами УВМ.
        result_file (str): Путь к файлу для сохранения результата выполнения.
        mem_range (str): Диапазон памяти для вывода в формате "start:end".
    """
    # Создаём парсер для обработки аргументов командной строки
    parser = argparse.ArgumentParser(description='Interpreter for EVM.')

    # Определяем обязательные аргументы: путь к бинарному файлу, путь к файлу результата и диапазон памяти
    parser.add_argument('binary_file', help='Path to the binary file.')
    parser.add_argument('result_file', help='Path to the result file.')
    parser.add_argument('mem_range', help='Memory range to output (start:end).')

    # Парсим переданные аргументы
    args = parser.parse_args()

    # Инициализируем память и регистры УВМ
    memory = [0] * 1024  # Память УВМ: 1024 ячейки, инициализированные нулями
    registers = [0] * 8  # Регистры УВМ: 8 регистров, инициализированных нулями

    # Открываем бинарный файл и считываем все команды
    with open(args.binary_file, 'rb') as f:
        code = f.read()

    # Инициализируем счётчик команд (Program Counter)
    pc = 0
    code_length = len(code)

    # Главный цикл интерпретатора: выполняем команды до конца бинарного кода
    while pc < code_length:
        # Извлекаем opcode текущей команды (7 младших битов первого байта)
        opcode = code[pc] & 0x7F

        if opcode == 10:  # LOAD_CONST
            """
            Команда LOAD_CONST:
                Формат: LOAD_CONST B C
                Описание: Загружает константу C в регистр по адресу B.

                Биты команды:
                    A (7 бит): 10 (уже обработано через opcode)
                    B (3 бита): адрес регистра
                    C (24 бита): константа
            """
            # Извлекаем байты команды (5 байт для LOAD_CONST)
            instr_bytes = code[pc:pc + 5]
            # Преобразуем байты в целое число (little endian)
            instr = int.from_bytes(instr_bytes, byteorder='little')
            # Извлекаем поля A, B и C из инструкции
            A = instr & 0x7F
            B = (instr >> 7) & 0x7
            C = (instr >> 10) & 0xFFFFFF
            # Загружаем константу C в регистр B
            registers[B] = C
            # Увеличиваем счётчик команд на размер команды (5 байт)
            pc += 5

        elif opcode == 54:  # READ_MEM
            """
            Команда READ_MEM:
                Формат: READ_MEM B C
                Описание: Читает значение из памяти по адресу B и сохраняет его в регистр по адресу C.

                Биты команды:
                    A (7 бит): 54 (уже обработано через opcode)
                    B (32 бита): адрес в памяти
                    C (3 бита): адрес регистра
            """
            # Извлекаем байты команды (6 байт для READ_MEM)
            instr_bytes = code[pc:pc + 6]
            # Преобразуем байты в целое число (little endian)
            instr = int.from_bytes(instr_bytes, byteorder='little')
            # Извлекаем поля A, B и C из инструкции
            A = instr & 0x7F
            B = (instr >> 7) & 0xFFFFFFFF
            C = (instr >> 39) & 0x7
            # Читаем значение из памяти по адресу B и сохраняем в регистр C
            if B >= len(memory):
                print(f"Memory read error: Address {B} out of bounds.", file=sys.stderr)
                sys.exit(1)
            registers[C] = memory[B]
            # Увеличиваем счётчик команд на размер команды (6 байт)
            pc += 6

        elif opcode == 39:  # WRITE_MEM
            """
            Команда WRITE_MEM:
                Формат: WRITE_MEM B C
                Описание: Записывает значение из регистра по адресу B в память по адресу, хранящемуся в регистре по адресу C.

                Биты команды:
                    A (7 бит): 39 (уже обработано через opcode)
                    B (3 бита): адрес регистра источника
                    C (3 бита): адрес регистра с адресом памяти
            """
            # Извлекаем байты команды (2 байта для WRITE_MEM)
            instr_bytes = code[pc:pc + 2]
            # Преобразуем байты в целое число (little endian)
            instr = int.from_bytes(instr_bytes, byteorder='little')
            # Извлекаем поля A, B и C из инструкции
            A = instr & 0x7F
            B = (instr >> 7) & 0x7
            C = (instr >> 10) & 0x7
            # Получаем адрес памяти из регистра C
            addr = registers[C]
            if addr >= len(memory):
                print(f"Memory write error: Address {addr} out of bounds.", file=sys.stderr)
                sys.exit(1)
            # Записываем значение из регистра B в память по адресу addr
            memory[addr] = registers[B]
            # Увеличиваем счётчик команд на размер команды (2 байта)
            pc += 2

        elif opcode == 18:  # POPCNT
            """
            Команда POPCNT:
                Формат: POPCNT B C
                Описание: Выполняет операцию popcnt на значении из памяти по адресу C и сохраняет результат в регистр по адресу B.

                Биты команды:
                    A (7 бит): 18 (уже обработано через opcode)
                    B (3 бита): адрес регистра для результата
                    C (32 бита): адрес в памяти для операции popcnt
            """
            # Извлекаем байты команды (6 байт для POPCNT)
            instr_bytes = code[pc:pc + 6]
            # Преобразуем байты в целое число (little endian)
            instr = int.from_bytes(instr_bytes, byteorder='little')
            # Извлекаем поля A, B и C из инструкции
            A = instr & 0x7F
            B = (instr >> 7) & 0x7
            C = (instr >> 10) & 0xFFFFFFFF
            # Получаем адрес памяти из регистра C
            if C >= len(memory):
                print(f"Memory popcnt error: Address {C} out of bounds.", file=sys.stderr)
                sys.exit(1)
            # Выполняем popcnt на значении из памяти по адресу C и сохраняем результат в регистр B
            memory[C] = popcnt(memory[C])
            registers[B] = memory[C]  # Обновляем регистр B
            # Увеличиваем счётчик команд на размер команды (6 байт)
            pc += 6

        else:
            # Если opcode не распознан, выводим сообщение об ошибке и завершаем работу
            print(f"Unknown opcode at pc={pc}: {opcode}", file=sys.stderr)
            sys.exit(1)

    # После выполнения всех команд, извлекаем указанный диапазон памяти
    try:
        start, end = map(int, args.mem_range.split(':'))
    except ValueError:
        print(f"Invalid memory range format: {args.mem_range}. Expected format 'start:end'.", file=sys.stderr)
        sys.exit(1)

    # Проверяем, что диапазон памяти корректен
    if not (0 <= start <= end <= len(memory)):
        print(f"Memory range out of bounds: {args.mem_range}.", file=sys.stderr)
        sys.exit(1)

    # Извлекаем значения из памяти в указанном диапазоне
    result = memory[start:end]

    # Записываем результат в файл-результат в формате JSON
    with open(args.result_file, 'w') as f:
        json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()

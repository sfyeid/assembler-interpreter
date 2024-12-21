import unittest
import subprocess
import tempfile
import os
import json

class TestFullSystem(unittest.TestCase):
    def test_full_assembly_and_execution(self):
        # Тестовая программа на ассемблере
        source_code = """
        # Тестовая программа для УВМ

        # Загружаем константу 25 в регистр 0
        LOAD_CONST 0 25

        # Загружаем адрес памяти 10 в регистр 1
        LOAD_CONST 1 10

        # Записываем значение из регистра 0 в память по адресу из регистра 1
        WRITE_MEM 0 1

        # Читаем значение из памяти по адресу 10 в регистр 2
        READ_MEM 10 2

        # Выполняем popcnt на значении из регистра 2 и сохраняем результат в регистр 3
        POPCNT 2 3
        """
        expected_log = [
            {"A": 10, "B": 0, "C": 25},
            {"A": 10, "B": 1, "C": 10},
            {"A": 39, "B": 0, "C": 1},
            {"A": 54, "B": 10, "C": 2},
            {"A": 18, "B": 2, "C": 3}
        ]

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as src:
            src.write(source_code)
            src_name = src.name

        with tempfile.NamedTemporaryFile(delete=False) as bin_f:
            bin_name = bin_f.name

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as log_f:
            log_name = log_f.name

        with tempfile.NamedTemporaryFile(delete=False) as res_f:
            res_name = res_f.name

        try:
            # Ассемблируем программу
            assemble_result = subprocess.run([
                'python', 'assembler.py',
                src_name,
                bin_name,
                '--log_file', log_name
            ], capture_output=True, text=True)
            self.assertEqual(assemble_result.returncode, 0, f"Assembler failed with error: {assemble_result.stderr}")

            # Проверяем лог ассемблирования
            with open(log_name, 'r') as log_f_read:
                log_data = json.load(log_f_read)
            self.assertEqual(log_data, expected_log, "Assembler log does not match expected.")

            # Выполняем интерпретатор
            interpreter_result = subprocess.run([
                'python', 'interpreter.py',
                bin_name,
                res_name,
                "0:15"
            ], capture_output=True, text=True)
            self.assertEqual(interpreter_result.returncode, 0,
                             f"Interpreter failed with error: {interpreter_result.stderr}")

            # Проверяем результат выполнения
            with open(res_name, 'r') as res_f_read:
                result_data = json.load(res_f_read)
            # Диапазон 0:15 включает memory[0] до memory[14]
            expected_memory = [0] * 15
            expected_memory[10] = 25  # Результат popcnt
            self.assertEqual(result_data, expected_memory,
                             "Full system execution did not produce expected memory state.")

        finally:
            # Удаляем временные файлы
            os.unlink(src_name)
            os.unlink(bin_name)
            os.unlink(log_name)
            os.unlink(res_name)

if __name__ == '__main__':
    unittest.main()

import unittest
import subprocess
import tempfile
import os
import json


class TestAssembler(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для исходного кода, бинарного вывода и лога
        self.source_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.binary_file = tempfile.NamedTemporaryFile(delete=False)
        self.log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)

    

    def run_assembler(self):
        # Запускаем ассемблер с временными файлами
        result = subprocess.run([
            'python', 'assembler.py',
            self.source_file.name,
            self.binary_file.name,
            '--log_file', self.log_file.name
        ], capture_output=True, text=True)
        if result.returncode != 0:
            self.fail(f"Assembler failed with error: {result.stderr}")

    def read_binary(self, expected_bytes):
        with open(self.binary_file.name, 'rb') as f:
            binary_data = f.read()
        self.assertEqual(binary_data, expected_bytes, "Binary output does not match expected.")

    def read_log(self, expected_log):
        with open(self.log_file.name, 'r') as f:
            log_data = json.load(f)
        self.assertEqual(log_data, expected_log, "Log output does not match expected.")

    def test_load_const(self):
        # Тест для команды LOAD_CONST
        self.source_file.write("LOAD_CONST 6 632\n")
        self.source_file.flush()
        self.run_assembler()
        expected_binary = bytes([0x0A, 0xE3, 0x09, 0x00, 0x00])  # 0x0A, 0xE3, 0x09, 0x00, 0x00
        expected_log = [{"A": 10, "B": 6, "C": 632}]
        self.read_binary(expected_binary)
        self.read_log(expected_log)

    def test_read_mem(self):
        # Тест для команды READ_MEM
        self.source_file.write("READ_MEM 328 3\n")
        self.source_file.flush()
        self.run_assembler()
        expected_binary = bytes([0x36, 0xA4, 0x00, 0x00, 0x80, 0x01])  # 0x36, 0xA4, 0x00, 0x00, 0x80, 0x01
        expected_log = [{"A": 54, "B": 328, "C": 3}]
        self.read_binary(expected_binary)
        self.read_log(expected_log)

    def test_write_mem(self):
        # Тест для команды WRITE_MEM
        self.source_file.write("WRITE_MEM 1 5\n")
        self.source_file.flush()
        self.run_assembler()
        expected_binary = bytes([0xA7, 0x14])  # 0xA7, 0x14
        expected_log = [{"A": 39, "B": 1, "C": 5}]
        self.read_binary(expected_binary)
        self.read_log(expected_log)

    def test_popcnt(self):
        # Тест для команды POPCNT
        self.source_file.write("POPCNT 6 310\n")
        self.source_file.flush()
        self.run_assembler()
        expected_binary = bytes([0x12, 0xDB, 0x04, 0x00, 0x00, 0x00])  # 0x12, 0xDB, 0x04, 0x00, 0x00, 0x00
        expected_log = [{"A": 18, "B": 6, "C": 310}]
        self.read_binary(expected_binary)
        self.read_log(expected_log)

    def test_multiple_instructions(self):
        # Тест с несколькими инструкциями
        self.source_file.write(
            "LOAD_CONST 6 632\n"
            "READ_MEM 328 3\n"
            "WRITE_MEM 1 5\n"
            "POPCNT 6 310\n"
        )
        self.source_file.flush()
        self.run_assembler()
        expected_binary = (
                bytes([0x0A, 0xE3, 0x09, 0x00, 0x00]) +
                bytes([0x36, 0xA4, 0x00, 0x00, 0x80, 0x01]) +
                bytes([0xA7, 0x14]) +
                bytes([0x12, 0xDB, 0x04, 0x00, 0x00, 0x00])
        )
        expected_log = [
            {"A": 10, "B": 6, "C": 632},
            {"A": 54, "B": 328, "C": 3},
            {"A": 39, "B": 1, "C": 5},
            {"A": 18, "B": 6, "C": 310}
        ]
        self.read_binary(expected_binary)
        self.read_log(expected_log)

    def test_invalid_opcode(self):
        # Тест с неизвестной командой
        self.source_file.write("INVALID_CMD 1 2\n")
        self.source_file.flush()
        result = subprocess.run([
            'python', 'assembler.py',
            self.source_file.name,
            self.binary_file.name,
            '--log_file', self.log_file.name
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Assembler should fail with invalid opcode.")
        self.assertIn("Unknown opcode", result.stderr)

    def test_overflow_fields(self):
        # Тест с превышением значений полей
        # Например, поле B для LOAD_CONST должно быть 3 бита, максимальное значение 7
        self.source_file.write("LOAD_CONST 8 123456\n")  # B=8 (превышает 3 бита)
        self.source_file.flush()
        result = subprocess.run([
            'python', 'assembler.py',
            self.source_file.name,
            self.binary_file.name,
            '--log_file', self.log_file.name
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Assembler should fail when fields overflow.")
        self.assertIn("Field B=8 out of range for LOAD_CONST (0-7)", result.stderr)


if __name__ == '__main__':
    unittest.main()

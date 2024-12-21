import unittest
from unittest.mock import mock_open, patch
from io import StringIO
import interpreter


class TestUVMInterpreter(unittest.TestCase):

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_load_const(self, mock_file):
        # Подготовка бинарных данных для LOAD_CONST
        # A=10, B=1, C=5
        instr = 10 + (1 <<7) + (5 <<10)  # 10 + 128 + 5120 = 5258
        binary_data = instr.to_bytes(5, byteorder='little')
        mock_file().read.return_value = binary_data

        # Mock для записи результата
        m = mock_open()
        with patch('interpreter.open', m):
            with patch('interpreter.json.dump') as mock_json_dump:
                interpreter.main()

                # Проверяем, что результат записан корректно
                expected_result = [0] * 10  # Поскольку LOAD_CONST не изменяет память
                mock_json_dump.assert_called_once_with(expected_result, m(), indent=2)

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_read_write_mem(self, mock_file):
        # Подготовка бинарных данных для:
        # 1. LOAD_CONST рег 0 = 100
        # 2. LOAD_CONST рег 1 = 50 (адрес памяти)
        # 3. WRITE_MEM B=0, C=1 (записываем из рег 0 в память по адресу из рег 1)
        # 4. READ_MEM B=2, C=1 (читаем из памяти по адресу из рег 1 в рег 2)

        # Инструкция LOAD_CONST для рег 0 = 100
        instr1 = 10 + (0 <<7) + (100 <<10)
        load_const_reg0 = instr1.to_bytes(5, byteorder='little')

        # Инструкция LOAD_CONST для рег 1 = 50
        instr2 = 10 + (1 <<7) + (50 <<10)
        load_const_reg1 = instr2.to_bytes(5, byteorder='little')

        # Инструкция WRITE_MEM: A=39, B=0, C=1
        # instr = 39 + (0 <<7) + (1 <<10) = 39 + 0 + 1024 = 1063
        instr3 = 39 + (0 <<7) + (1 <<10)
        write_mem = instr3.to_bytes(2, byteorder='little')

        # Инструкция READ_MEM: A=54, B=2, C=1
        # instr = 54 + (2 <<7) + (1 <<39)
        # Но C - 3 бита, поэтому (1 <<39) может быть слишком большим.
        # В коде, C для READ_MEM извлекается из битов 39- это 3 бита
        # Для READ_MEM:
        # A=54 (7 бит), B=2 (3 бита), C=1 (32 бита)
        # Таким образом:
        # instr = A + (B <<7) + (C <<10)
        # где C занимает 32 бита, но нам нужно всего 6 байт (48 бит)

        # A=54, B=2, C=1
        instr4 = 54 + (2 <<7) + (1 <<10)
        read_mem = instr4.to_bytes(6, byteorder='little')

        binary_data = load_const_reg0 + load_const_reg1 + write_mem + read_mem
        mock_file().read.return_value = binary_data

        # Mock JSON dump
        m = mock_open()
        with patch('interpreter.open', m):
            with patch('interpreter.json.dump') as mock_json_dump:
                interpreter.main()

                # После WRITE_MEM, memory[50] = 100
                # После READ_MEM, reg 2 = memory[50] = 100
                # Диапазон памяти '0:10' остаётся неизменным, так как адрес 50 вне диапазона
                expected_result = [0] * 10
                mock_json_dump.assert_called_once_with(expected_result, m(), indent=2)

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_popcnt(self, mock_file):
        # Подготовка бинарных данных для:
        # 1. LOAD_CONST рег 0 = 11 (0b1011)
        # 2. POPCNT B=1, C=0 (popcnt(memory[0]) -> reg 1)
        # 3. LOAD_CONST рег 1 = 11 (запись результата popcnt)

        # Инструкция LOAD_CONST для рег 0 = 11
        instr1 = 10 + (0 <<7) + (11 <<10)
        load_const_reg0 = instr1.to_bytes(5, byteorder='little')

        # Инструкция POPCNT: A=18, B=1, C=0
        instr2 = 18 + (1 <<7) + (0 <<10)
        popcnt = instr2.to_bytes(6, byteorder='little')

        binary_data = load_const_reg0 + popcnt
        mock_file().read.return_value = binary_data

        # Mock JSON dump
        m = mock_open()
        with patch('interpreter.open', m):
            with patch('interpreter.json.dump') as mock_json_dump:
                interpreter.main()

                # После POPCNT, memory[0] = popcnt(0) =0
                # Диапазон памяти '0:10' остаётся [0,0,0,0,0,0,0,0,0,0]
                expected_result = [0] * 10
                mock_json_dump.assert_called_once_with(expected_result, m(), indent=2)

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_unknown_opcode(self, mock_file):
        # Подготовка бинарных данных с неизвестным opcode=99
        binary_data = bytes([99])
        mock_file().read.return_value = binary_data

        with patch('interpreter.sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                interpreter.main()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn("Unknown opcode", mock_stderr.getvalue())

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '1000:2000'])
    def test_invalid_memory_range(self, mock_file):
        # Подготовка пустых бинарных данных
        binary_data = bytes([])
        mock_file().read.return_value = binary_data

        with patch('interpreter.sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                interpreter.main()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn("Memory range out of bounds", mock_stderr.getvalue())

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_memory_address_out_of_bounds_read(self, mock_file):
        # Подготовка бинарных данных для READ_MEM с адресом вне диапазона
        # Инструкция READ_MEM: A=54, B=0, C=1024
        instr = 54 + (0 <<7) + (1024 <<10)
        read_mem_instr = instr.to_bytes(6, byteorder='little')

        binary_data = read_mem_instr
        mock_file().read.return_value = binary_data

        with patch('interpreter.sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                interpreter.main()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn("Memory read error", mock_stderr.getvalue())

    @patch('interpreter.open', new_callable=mock_open)
    @patch('interpreter.sys.argv', ['interpreter.py', 'binary.bin', 'result.json', '0:10'])
    def test_memory_address_out_of_bounds_write(self, mock_file):
        # Подготовка бинарных данных для:
        # 1. LOAD_CONST рег 0 = 5
        # 2. LOAD_CONST рег 1 = 1024 (адрес памяти)
        # 3. WRITE_MEM B=0, C=1 (записываем из рег 0 в память по адресу из рег 1)

        # Инструкция LOAD_CONST для рег 0 = 5
        instr1 = 10 + (0 <<7) + (5 <<10)
        load_const_reg0 = instr1.to_bytes(5, byteorder='little')

        # Инструкция LOAD_CONST для рег 1 = 1024
        instr2 = 10 + (1 <<7) + (1024 <<10)
        load_const_reg1 = instr2.to_bytes(5, byteorder='little')

        # Инструкция WRITE_MEM: A=39, B=0, C=1
        instr3 = 39 + (0 <<7) + (1 <<10)
        write_mem = instr3.to_bytes(2, byteorder='little')

        binary_data = load_const_reg0 + load_const_reg1 + write_mem
        mock_file().read.return_value = binary_data

        with patch('interpreter.sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit) as cm:
                interpreter.main()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertIn("Memory write error", mock_stderr.getvalue())

if __name__ == '__main__':
    unittest.main()

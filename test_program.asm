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

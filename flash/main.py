from machine import Pin, Timer, PWM
import tm1637
import utime
import uos
from rotary_irq_rp2 import RotaryIRQ
import json

# Инициализация дисплея
def init_tm(dio_pin=9, clk_pin=10):
    """
    Инициализирует дисплей TM1637.
    
    Параметры:
        dio_pin (int): номер GPIO для DIO (по умолчанию 9).
        clk_pin (int): номер GPIO для CLK (по умолчанию 10).
    
    Возвращает:
        объект TM1637 или None, если инициализация не удалась.
    """
    try:
        tm = tm1637.TM1637(clk=Pin(clk_pin), dio=Pin(dio_pin))
        tm.brightness(5)  # Устанавливаем яркость (0-7)
        return tm
    except Exception as e:
        print(f"Ошибка инициализации дисплея: {e}")
        return None

def show_text(tm, text):
    tm.show(text)
    
CONFIG_DICT = {}

# Приветствие на экране дисплея
def scroll_text(tm, text, seq=1):
    # Добавляем пробелы в начале и конце для плавного появления/исчезновения
    begin = 0
    padded_text = "    " + text + "    "
    while begin < seq:
        tm.scroll(padded_text, 250)
        begin += 1

# Конфигурация пинов
RGB_ANODES = (
    Pin(18, Pin.OUT),
    Pin(19, Pin.OUT),
    Pin(20, Pin.OUT),
    Pin(21, Pin.OUT)
)

COLOR_PINS = {
    'red': Pin(6, Pin.OUT),
    'green': Pin(7, Pin.OUT),
    'blue': Pin(8, Pin.OUT)
}

BUTTON_PINS = (
    Pin(0, Pin.IN, Pin.PULL_UP),
    Pin(1, Pin.IN, Pin.PULL_UP),
    Pin(2, Pin.IN, Pin.PULL_UP),
    Pin(3, Pin.IN, Pin.PULL_UP)
    )

SERVO_PIN = PWM(Pin(14))
SERVO_PIN.freq(50)

ROTARY_KEY = Pin(13, Pin.IN, Pin.PULL_UP)

PUMP_PIN = Pin(15, Pin.OUT)

# Состояния диодов [R, G, B] для каждого из 4 диодов
led_states = [
    [0, 0, 0],  # Диод 0
    [0, 0, 0],  # Диод 1
    [0, 0, 0],  # Диод 2
    [0, 0, 0]   # Диод 3
]

# Текущий активный диод
current_led = 0

def init_led():
    """Инициализация светодиодов - все выключено"""
    for anode in RGB_ANODES:
        anode.off()
    for pin in COLOR_PINS.values():
        pin.on()  # Общий анод - цвета выключены по умолчанию

def set_color(r, g, b):
    """Установка цвета (инвертированная логика для общего анода)"""
    COLOR_PINS['red'].value(not r)
    COLOR_PINS['green'].value(not g)
    COLOR_PINS['blue'].value(not b)

def refresh_led(timer):
    """Обработчик прерывания таймера для динамической индикации"""
    global current_led
    
    # Выключаем предыдущий диод
    RGB_ANODES[current_led].off()
    
    # Переходим к следующему диоду
    current_led = (current_led + 1) % len(RGB_ANODES)
    
    # Устанавливаем цвет для нового диода
    r, g, b = led_states[current_led]
    set_color(r, g, b)
    
    # Включаем анод нового диода
    RGB_ANODES[current_led].on()


def read_buttons():
    buttons_state = []
    for button_index, button in enumerate(BUTTON_PINS):        
        if button.value() == 0:
            utime.sleep_ms(20)
            if button.value() == 0:
                led_states[button_index] = [0, 1, 0]
                buttons_state.append(1)
        else:
            led_states[button_index] = [1, 0, 0]
            buttons_state.append(0)
    return buttons_state

def init_rotary():
    rotary = RotaryIRQ(
                        pin_num_clk = 11,
                        pin_num_dt = 12,
                        min_val = 0,
                        max_val = 180,
                        reverse = False,
                        range_mode = RotaryIRQ.RANGE_WRAP
                        )
    return rotary
                    

def rotate_to_angle(angle: int, pwm_pin):
    """
    Функция поворачивает (устанавливает) сервопирвод на заданый угол
    Args:
        angle(int): угол установки серво
    """
    min_duty = 1638
    max_duty = 8192
    duty = int(min_duty + (max_duty - min_duty) * (angle / 180))
    pwm_pin.duty_u16(duty)


# Проверка наличия файла cal.conf
def check_config():
    global CONFIG_DICT
    try:
        # Попытка открыть файл для чтения
        with open("cal.conf", "r") as f:
            CONFIG_DICT = json.load(f)
            return True  # Файл существует
    except OSError:
        return False  # Файл не найден
    
def calibration(tm1637, rotary):
    global CONFIG_DICT
    tm1637.show("CAL ")  # Вывод "CAL" на дисплей
    utime.sleep(2)
    tm1637.show("ANGL")  # Вывод "ANGLE" на дисплей
    
    CONFIG_DICT.setdefault('place_angle', {})
    
    for position in range(0,4):
        tm1637.show(f"POS{position + 1}")
        while ROTARY_KEY.value() == 1:
            position_angle = rotary.value()
            rotate_to_angle(position_angle, SERVO_PIN)
        CONFIG_DICT.get('place_angle').update({position:position_angle})
        utime.sleep(1)
    tm1637.write([0, 0, 0, 0])
    
    tm1637.show("VOL")
    while read_buttons() == [0, 0, 0, 0]:
        for position in range(0, 4):
            led_states[position] = [1, 0, 0]
    
    cal_pos = 0
    for button in read_buttons():
        if button == 1:
            break
        else:
            cal_pos += 1
            
    led_states[cal_pos] = [0, 1, 0]
    rotate_to_angle(CONFIG_DICT.get('place_angle').get(cal_pos), SERVO_PIN)
    
    while ROTARY_KEY.value() == 1:
        pass
    if ROTARY_KEY.value() == 0:
        utime.sleep_ms(20)
        if ROTARY_KEY.value() == 0:
            start_time = utime.ticks_ms()  
            PUMP_PIN.value(1)
            while ROTARY_KEY.value() == 0:
                pass

    PUMP_PIN.value(0)
    stop_time = utime.ticks_ms()
    elapsed_ms = utime.ticks_diff(stop_time, start_time)
    CONFIG_DICT.update({'full_volume': elapsed_ms})
    
    tm1637.write([0, 0, 0, 0])
            
    with open("cal.conf", "w") as f:
        json.dump(CONFIG_DICT, f)
        
    print(CONFIG_DICT)

def main():
    # Инициализация дисплея TM1637
    tm1637 = init_tm()
    message = "HELLO"
    scrolls = 1  # Количество пробежек сообщения
    scroll_text(tm1637, message, scrolls)

    # Инициализация светодиодов
    init_led()
    
    # Инициализация энкодера
    rotary = init_rotary()

    # Настройка таймера для обновления светодиодов (частота 200 Гц)
    led_timer = Timer()
    led_timer.init(freq=200, mode=Timer.PERIODIC, callback=refresh_led)
    
    if ROTARY_KEY.value() == 0:
        print("Выбран режим калибровки...")
        calibration(tm1637, rotary)
    elif not check_config():
        print("Файл cal.conf не найден!")
        if tm1637:
            calibration(tm1637, rotary)
    else:
        print("Файл cal.conf найден.")
        if tm1637:
            tm1637.write([0, 0, 0, 0])  # Очистка дисплея
    
    # Основной цикл программы
    while True:
        read_buttons()
        button_states = read_buttons()
        rotate_to_angle(rotary.value(), SERVO_PIN)
        utime.sleep_ms(100)

if __name__ == '__main__':
    main()
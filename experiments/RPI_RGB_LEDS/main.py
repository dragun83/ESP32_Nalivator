from machine import Pin, Timer
import utime

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

# Состояния диодов [R, G, B] для каждого из 4 диодов
led_states = [
    [0, 0, 0],  # Диод 0
    [0, 0, 0],  # Диод 1
    [0, 0, 0],  # Диод 2
    [0, 0, 0]   # Диод 3
]

# Текущий активный диод
current_led = 0

def init_display():
    """Инициализация дисплея - все выключено"""
    for anode in RGB_ANODES:
        anode.off()
    for pin in COLOR_PINS.values():
        pin.on()  # Общий анод - цвета выключены по умолчанию

def set_color(r, g, b):
    """Установка цвета (инвертированная логика для общего анода)"""
    COLOR_PINS['red'].value(not r)
    COLOR_PINS['green'].value(not g)
    COLOR_PINS['blue'].value(not b)

def refresh_display(timer):
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

def main():
    init_display()
    
    # Настройка таймера для обновления дисплея (частота 200 Гц)
    display_timer = Timer()
    display_timer.init(freq=800, mode=Timer.PERIODIC, callback=refresh_display)
    
    # Основной цикл программы может делать другие вещи
    counter = 0
    while True:
        print(f"Основная программа работает... {counter}")
        counter += 1
        led_states[3] = [0,0,1]
        # Пример изменения цветов в реальном времени
        if counter % 10 == 0:
            led_states[0][0] = not led_states[0][0]  # Мигаем красным на 1-м диоде
        
        utime.sleep_ms(100)

if __name__ == '__main__':
    main()
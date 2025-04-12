#Тестирование ЛГБТ подсветки в динамическом режиме
import esp32
from machine import Timer
from machine import Pin

LED_ANODES = (0, 1, 2, 3)
RGB_PINS = (5, 6, 7)

def initial_leds(anode_pins: tuple, rgb_pins: tuple) -> list:
    """
    Функция инициализирует пины к которым подключены светодиоды
    """
    led_anodes_list = []
    rgb_pins_list = []
    for la in anode_pins:
        led_anode = Pin(la, Pin.Out)
        led_anodes_list.append(led_anode)
    for rgbp in rgb_pins:
        rgb_pin = Pin(rgbp, Pin.OUT)
    return led_anodes_list 

def led_tick(anode_list):
    """
    Функция вызывается по таймеру - он-же задает частоту
    Функция должна переключать аноды светодиодов с заданой частотой
    Одновременно гореть должен только 1 диод
    """
    pass




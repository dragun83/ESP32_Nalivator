#This is main prog
#Тут пишем основную прогу
import esp32
import machine
from rotary_irq_esp import RotaryIRQ
#from rotary_irq_esp import RotaryIRQ
import time





def setup_pwm():
    pwm_pin = machine.PWM(machine.Pin(0),50)
    return pwm_pin

def rotate_to_angle(angle: int, pwm_pin):
    """
    Функция поворачивает (устанавливает) сервопирвод на заданый угол
    Args:
        angle(int): угол установки серво
    """
    duty = int(40 + (angle * 100 / 180))
    pwm_pin.duty(duty)

def read_input() -> int:
    """
    Функция читает ввод в порт валидирует и возвращает введеный угол
    """
    angle = int(input("Input angle from 0 to 180 :"))
    if angle < 0 or angle > 180:
        print(f"{angle} - -s wrong angle! Input from 0 to 180")
    else:
        return angle
    
def save_position_list(config_json: str):
    with open('config.json', 'w') as config_file:
        config_file.write('testing testings')
        
       
    
def main():
    pwm_pin = setup_pwm()
    rotate_to_angle(90, pwm_pin)
    sleep_time = 0.05
    step = 2
    
    rotary = RotaryIRQ(
                        pin_num_clk = 5,
                        pin_num_dt = 6,
                        min_val = 0,
                        max_val = 180,
                        reverse = False,
                        range_mode = RotaryIRQ.RANGE_WRAP
                        )
    val_old = rotary.value()
    while True:
        val_new = rotary.value()
        if val_old != val_new:
            val_old = val_new
            print(val_old)
            rotate_to_angle(val_old, pwm_pin)
        time.sleep_ms(50)
main()
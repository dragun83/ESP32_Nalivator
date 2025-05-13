#This is main prog
#Тут пишем основную прогу
import esp32
import machine
import time





def setup_pwm():
    pwm_pin = machine.PWM(machine.Pin(32),50)
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
    rotate_to_angle(0, pwm_pin)
    sleep_time = 0.05
    step = 2
    save_position_list()
    while True:
        for angle in range(0, 180, step):
            print(angle)
            rotate_to_angle(angle, pwm_pin)
            time.sleep(sleep_time)
        time.sleep(sleep_time * 100)
        for angle in range(180, -2, 0 - step):
            print(angle)
            rotate_to_angle(angle, pwm_pin)
            time.sleep(sleep_time)
        time.sleep(sleep_time * 10)
main()
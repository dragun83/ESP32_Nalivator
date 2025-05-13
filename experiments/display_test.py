from machine import Pin
import tm1637

display = tm1637.TM1637(clk=Pin(1), dio=Pin(0))

display.brightness(254)
display.write([127, 255, 127, 127])
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2005-2021 BelSD - Jean-Pierre Waldorf
#
# Raspberry Temperature PiFan Control
# 
PRG_VERSION = '1.0' # Programm Version
#
import os
import sys
from os.path import getmtime
from time import sleep
from gpiozero import OutputDevice

STARTING = True
LOOP = True
FAN_ON = 65   # Température d'activation du/des ventilateur(s) (en degrés Celcius).
FAN_OFF = 55  # Température de déactivation du/des ventilateur(s) (en degrés Celcius).
GPIO_PIN = 14 # GPIO où est branché le contrôleur du/des ventilateur(s)

fan = OutputDevice(GPIO_PIN)
fan.on()

# Info sur le chier actuel pour voir si une modification du code est présente
# et le cas échéant, redémarrer le programme pour la prise en considération du 
# nouveau code source
WATCHED_FILE_TIME = getmtime(__file__)

def read_temp():
    # 
    # Lecture de la température du processeur en millièmes de degrés Celcius
    #
    with open('/sys/class/thermal/thermal_zone0/temp') as READ_CPU_TEMP:
        CPU_TEMP = READ_CPU_TEMP.read()

    try:
        return int(CPU_TEMP) / 1000
    except (IndexError, ValueError,) as ERROR_STR:
        raise RuntimeError('Impossible d\'analyser la sortie de température.') from ERROR_STR

if __name__ == '__main__':

    # Valider les seuils d'activation et de désactivation
    if FAN_OFF >= FAN_ON:
        raise RuntimeError('FAN_OFF doit-être inférieur à FAN_ON')
        LOOP = False

    while LOOP:
        # Check si le code source a changé, si oui, on redémare le programme
        # pour la prise en considération du nouveau code
        if getmtime(__file__) != WATCHED_FILE_TIME:
            os.execv(sys.executable, ['python3'] + sys.argv)

        if STARTING == True:
            STARTING = False
        else:
            CPU_TEMPERATURE = read_temp()
            # Active le(s) ventilateur(s) si le seuil de température est atteint
            # et qu'il(s) n'est/ne sont pas déjà activé(s)
            # NOTE: `fan.value` retourne 1 pour "on" et 0 pour "off"
            if CPU_TEMPERATURE > FAN_ON and not fan.value:
                fan.on()
            # Arrête le(s) ventilateur(s) si la température est en dessous su seuil de température
            elif fan.value and CPU_TEMPERATURE < FAN_OFF:
                fan.off()

        sleep(5)
    
    fan.off()
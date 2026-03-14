import random
import math
from werkzeug.security import generate_password_hash

def generar_password(letras, digitos, simbolos, letras_set, digitos_set, simbolos_set):
    letras_sel = ''.join(random.sample(letras_set, letras))
    digitos_sel = ''.join(random.sample(digitos_set, digitos))
    simbolos_sel = ''.join(random.sample(simbolos_set, simbolos))

    password = letras_sel + digitos_sel + simbolos_sel
    password_hash = generate_password_hash(password)
    return password, password_hash


def calcular_combinaciones(letras, digitos, simbolos, letras_set, digitos_set, simbolos_set):
    letras_total = math.perm(len(letras_set), letras)
    digitos_total = math.perm(len(digitos_set), digitos)
    simbolos_total = math.perm(len(simbolos_set), simbolos)
    return letras_total * digitos_total * simbolos_total
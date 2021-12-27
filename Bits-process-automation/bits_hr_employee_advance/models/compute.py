from datetime import datetime, date


# Funcion que calcula edad a partir de la fecha de nacimiento y la fecha actual
def calculeAge(birthday):
    today = datetime.today()
    return (today.year - birthday.year -
            ((today.month, today.day) < (birthday.month, birthday.day)))

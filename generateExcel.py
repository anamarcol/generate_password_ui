import pandas as pd
import random
import string

correos = []

for _ in range(100):

    # generar nombre aleatorio (5 a 8 letras)
    nombre = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5,8)))

    # generar número aleatorio
    numero = random.randint(10,999)

    correo = f"{nombre}{numero}@gmail.com"

    correos.append(correo)

# crear dataframe
df = pd.DataFrame({
    "email": correos
})

# guardar excel
df.to_excel("./data/correos_prueba.xlsx", index=False)

print("Excel generado: correos_prueba.xlsx")
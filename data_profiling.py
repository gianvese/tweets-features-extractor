import pandas as pd
import pandas_profiling
import sys

# Check dei parametri
if len(sys.argv) != 3:
    print('USAGE: data_profiling.py input_file.csv output_file.html')
    sys.exit(2)

# file contenente la matrice
input_file = sys.argv[1]
# file di output
output_file = sys.argv[2]

# importiamo la matrice contenente le features per ciascun tweet ottenuta da nome_file.py
df = pd.read_csv(input_file)

# titolo della pagina html nel browser
profile = df.profile_report(title = 'Pandas Profiling Report')
# percorso di destinazione del file HTML contenente il data profiling
profile.to_file(output_file)

print('Profiling creato in', sys.argv[2], '!')

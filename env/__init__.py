import_commmand="from .snakes import *\n"


for i in import_commmand.split('\n'):
    try:
        exec(i)
    except:
        print(f'FAIL: {i}')

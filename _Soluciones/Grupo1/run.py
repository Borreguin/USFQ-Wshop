from Taller1.P1_TSP.TSP import study_case_1
from Taller1.P3_Torres.Torres import main as torres_main

def main():
    print('Bienvenido al taller 1 de Inteligencia Artificial')
    print('\nEstudio de casos')
    print('1. TSP')
    print('2. N-body')
    print('3. Juego 2048')
    print('4. Otro')
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    if study_case == '1':
        print('\n=========================')
        print('Viaje del vendedor (TSP)')
        print('=========================')
        study_case_1()
        print('\nFin del estudio de caso 1\n')
        print('=========================')
        print('Viaje del vendedor (TSP) caso 2')
        print('=========================')
        study_case_2()
        print('\nFin del estudio de caso 2\n')
        print('=========================')
    elif study_case == '2':
        print('\n=========================')
        print('N-body')
        print('=========================')
        study_case_2()
        print('\nFin del estudio de caso 2\n')
    elif study_case == '3':
        print('\n=========================')
        print('Juego 2048')
        print('=========================')
        torres_main()
        print('\nFin del estudio de caso 3\n')
        print('=========================')
    else:
        print('No hay el texto')

if __name__ == "__main__":
    main()
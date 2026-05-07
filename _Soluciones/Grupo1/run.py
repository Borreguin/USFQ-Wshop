from Taller1.P1_TSP.TSP import study_case_1, study_case_2
from Taller1.P2_Granjero.Acertijo import main as granjero_main
from Taller1.P3_Torres.Torres import main as torres_main
from Taller2.P2.P2_ACO import study_case_1 as aco_study_case_1, study_case_2 as aco_study_case_2

def taller_1():
    print('Bienvenido al taller 1 de Inteligencia Artificial')
    print('\nEstudio de casos')
    print('1. TSP')
    print('2. Acertijo del granjero y el bote')
    print('3. Juego 2048')
    print('4. Otro')
    print('5. Salir')
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    while study_case != '5':
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
            print('Acertijo del granjero y el bote')
            print('=========================')
            granjero_main()
            print('\nFin del estudio de caso 2\n')
        elif study_case == '3':
            print('\n=========================')
            print('Torres de Hanoi')
            print('=========================')
            torres_main()
            print('\nFin del estudio de caso 3\n')
            print('=========================')
        else :
            print('No hay el texto')
        study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    print('Saliendo del taller 1')

def taller_2():
    print('Bienvenido al taller 2 de Inteligencia Artificial')
    print('\nEstudio de casos')
    print('1. Laberinto')
    print('2. Colonia de Hormigas')
    print('3. Otro')
    print('4. Salir')
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    while study_case != '4':
        if study_case == '1':
            print('\n=========================')
            print('Llamado al laberinto ')
            print('=========================')
        elif study_case == '2':
            print('\n=========================')
            print('Colonia de Hormigas')
            print('=========================')
            aco_study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Colonia de Hormigas caso 2')
            print('=========================')
            aco_study_case_2()
            print('\nFin del estudio de caso 2\n')
        else :
            print('No hay el texto')
        study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    print('Saliendo del taller 2')

def main():
    print('Bienvenido al taller de Inteligencia Artificial')
    print('1. Taller 1')
    print('2. Taller 2')
    print('3. Salir')
    option = input('Ingrese el taller que desea ejecutar: ')
    while option != '3':
        if option == '1':
            taller_1()
        elif option == '2':
            taller_2()
        else:
            print('No hay el texto')
        option = input('Ingrese el taller que desea ejecutar: ')
    print('Fin del programa')

if __name__ == "__main__":
    main()
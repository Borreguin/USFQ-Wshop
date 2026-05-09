from Taller1.P1_TSP.TSP import study_case_1, study_case_2
from Taller1.P2_Granjero.Acertijo import main as granjero_main
from Taller1.P3_Torres.Torres import main as torres_main
from Taller2.P1.P1 import study_case_1 as p1_study_case_1, study_case_2 as p1_study_case_2, study_case_3 as p1_study_case_3, study_case_4 as p1_study_case_4
from Taller2.P2.P2_ACO import study_case_1 as aco_study_case_1, study_case_2 as aco_study_case_2, find_optimized_path as study_case_optimized

def print_options(arr, header = None):
    if header:
        print(header)
    _ = [print(f'{i+1}. {option}') for i, option in enumerate(arr)]

def taller_1():
    options = ['TSP', 'Acertijo del granjero y el bote', 'Torres de Hanoi', 'Otro', 'Salir']
    header = 'Bienvenido al taller 1 de Inteligencia Artificial'
    print_options(options, header)
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
        print_options(options)
        study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    print('Saliendo del taller 1')

def taller_2():
    options = ['Laberinto', 'Colonia de Hormigas', 'Otro', 'Salir']
    header = 'Bienvenido al taller 2 de Inteligencia Artificial'
    print_options(options, header)
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    while study_case != '4':
        if study_case == '1':
            print('\n=========================')
            print('Llamado al laberinto ')
            print('=========================')
            p1_study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Llamado al laberinto caso 2')
            print('=========================')
            p1_study_case_2()
            print('\nFin del estudio de caso 2\n')
            print('=========================')
            print('Llamado al laberinto caso 3')
            print('=========================')
            p1_study_case_3()
            print('\nFin del estudio de caso 3\n')
            print('=========================')
            print('Llamado al laberinto caso 4')
            print('=========================')
            p1_study_case_4()
            print('\nFin del estudio de caso 4\n')
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
            print('=========================')
            print('Colonia de Hormigas caso de optimización')
            print('=========================')
            study_case_optimized()
            print('\nFin del estudio de optimización 2\n')
        else :
            print('No hay el texto')
        print_options(options)
        study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    print('Saliendo del taller 2')

def main():
    options = ['Taller 1', 'Taller 2', 'Salir']
    print_options(options, 'Bienvenido al taller de Inteligencia Artificial')
    option = input('Ingrese el taller que desea ejecutar: ')
    while option != '3':
        if option == '1':
            taller_1()
        elif option == '2':
            taller_2()
        else:
            print('No hay el texto')
        print_options(options)
        option = input('Ingrese el taller que desea ejecutar: ')
    print('Fin del programa')

if __name__ == "__main__":
    main()
from Taller1.P1_TSP.TSP import study_case_1, study_case_2
from Taller1.P2_Granjero.Acertijo import main as granjero_main
from Taller1.P3_Torres.Torres import main as torres_main
from Taller2.P1.P1 import study_case_1 as p1_study_case_1, study_case_3 as p1_study_case_3
from Taller2.P2.P2_ACO import study_case_1 as aco_study_case_1, study_case_2 as aco_study_case_2, study_case_optimized as study_case_optimized
from Taller3.P1_UML.p1_uml import start as start_p1_uml
from Taller3.P2_TSP.TSP import study_case_1 as gr1_study_case_1, study_case_2 as gr1_study_case_2, study_case_3 as gr1_study_case_3, study_nearest_neighbor

def print_options(arr, header = None):
    if header:
        print(header)
    _ = [print(f'{i+1}. {option}') for i, option in enumerate(arr)]
    print('0. Salir')

def taller_1():
    options = ['TSP', 'Acertijo del granjero y el bote', 'Torres de Hanoi', 'Otro']
    header = 'Bienvenido al taller 1 de Inteligencia Artificial'
    print_options(options, header)
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    while study_case != '0':
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
    options = ['Laberinto', 'Colonia de Hormigas', 'Otro']
    header = 'Bienvenido al taller 2 de Inteligencia Artificial'
    print_options(options, header)
    study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    while study_case != '0':
        if study_case == '1':
            print('\n=========================')
            print('Llamado al laberinto ')
            print('=========================')
            p1_study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Llamado al laberinto caso 3')
            print('=========================')
            p1_study_case_3()
            print('\nFin del estudio de caso 3\n')
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

def taller_3():
    options = ['Data de edificios', 'Otro']
    header = 'Bienvenido al taller 3 de Inteligencia Artificial'
    print_options(options, header)
    exercise = input('Ingrese el ejercicio que desea ejecutar: ')
    while exercise != '0':
        if exercise == '1':
            print('\n=========================')
            print('Llamado al dataset de edificios ')
            print('=========================')
            start_p1_uml()
            print('\nFin del estudio de caso 1\n')
        elif exercise == '2':
            study_case = input('Ingrese el caso de estudio que desea ejecutar: ')
            if study_case == '1':
                 print('\n=========================')
                 print('Resolución del TSP sin heurísticas')
                 print('=========================')
                 gr1_study_case_1()
                 print('\nFin del estudio de caso 1\n')
            elif study_case == '2':
                print('\n=========================')
                print('Resolución del TSP con heurísticas (limitar_funcion_objetivo)')
                print('=========================')
                gr1_study_case_2()
                print('\nFin del estudio de caso 2\n')
            elif study_case == '3':
                print('\n=========================')
                print('Resolución del TSP con heurísticas (vecino más cercano)')
                print('=========================')
                gr1_study_case_3()
                print('\nFin del estudio de caso 3\n')
        else :
            print('No hay el texto')
        print_options(options)
        exercise = input('Ingrese el ejercicio que desea ejecutar: ')
    print('Saliendo del taller 3')

def main():
    options = ['Taller 1', 'Taller 2', 'Taller 3']
    print_options(options, 'Bienvenido al taller de Inteligencia Artificial')
    option = input('Ingrese el taller que desea ejecutar: ')
    while option != '0':
        if option == '1':
            taller_1()
        elif option == '2':
            taller_2()
        elif option == '3':
            taller_3()
        else:
            print('No hay el texto')
        print_options(options)
        option = input('Ingrese el taller que desea ejecutar: ')
    print('Fin del programa')

if __name__ == "__main__":
    main()
import Taller1.P1_TSP.TSP as T1_P1
import Taller1.P2_Granjero.Acertijo as T1_P2
import Taller1.P3_Torres.Torres as T1_P3
import Taller2.P1.P1 as T2_P1
import Taller2.P2.P2_ACO as T2_P2
import Taller3.P1_UML.p1_uml as T3_P1
import Taller3.P2_TSP.TSP as T3_P2

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
            T1_P1.study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Viaje del vendedor (TSP) caso 2')
            print('=========================')
            T1_P1.study_case_2()
            print('\nFin del estudio de caso 2\n')
            print('=========================')
        elif study_case == '2':
            print('\n=========================')
            print('Acertijo del granjero y el bote')
            print('=========================')
            T1_P2.main()
            print('\nFin del estudio de caso 2\n')
        elif study_case == '3':
            print('\n=========================')
            print('Torres de Hanoi')
            print('=========================')
            T1_P3.main()
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
            T2_P1.study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Llamado al laberinto caso 3')
            print('=========================')
            T2_P1.study_case_3()
            print('\nFin del estudio de caso 3\n')
        elif study_case == '2':
            print('\n=========================')
            print('Colonia de Hormigas')
            print('=========================')
            T2_P2.study_case_1()
            print('\nFin del estudio de caso 1\n')
            print('=========================')
            print('Colonia de Hormigas caso 2')
            print('=========================')
            T2_P2.study_case_2()
            print('\nFin del estudio de caso 2\n')
            print('=========================')
            print('Colonia de Hormigas caso de optimización')
            print('=========================')
            T2_P2.study_case_optimized()
            print('\nFin del estudio de optimización 2\n')
        else :
            print('No hay el texto')
        print_options(options)
        study_case = input('Ingrese el estudio de caso que desea ejecutar: ')
    print('Saliendo del taller 2')

def taller_3():
    options = ['Data de edificios', 'TSP', 'Algoritmos Genéticos']
    header = 'Bienvenido al taller 3 de Inteligencia Artificial'
    print_options(options, header)
    exercise = input('Ingrese el ejercicio que desea ejecutar: ')
    while exercise != '0':
        if exercise == '1':
            print('\n=========================')
            print('Llamado al dataset de edificios ')
            print('=========================')
            T3_P1.start()
            print('\nFin del estudio de caso 1\n')
        elif exercise == '2':
            study_case = input('Ingrese el caso de estudio que desea ejecutar: ')
            if study_case == '1':
                 print('\n=========================')
                 print('Resolución del TSP sin heurísticas')
                 print('=========================')
                 T3_P2.study_case_1()
                 print('\nFin del estudio de caso 1\n')
            elif study_case == '2':
                print('\n=========================')
                print('Resolución del TSP con heurísticas (limitar_funcion_objetivo)')
                print('=========================')
                T3_P2.study_case_2()
                print('\nFin del estudio de caso 2\n')
            elif study_case == '3':
                print('\n=========================')
                print('Resolución del TSP con heurísticas (vecino más cercano)')
                print('=========================')
                T3_P2.study_case_3()
                print('\nFin del estudio de caso 3\n')
            if exercise == '3':
                print('Pendiente por implementar en run.py')
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
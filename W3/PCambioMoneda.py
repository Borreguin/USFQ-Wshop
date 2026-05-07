from pyomo.environ import *

def resolver_cambio_moneda(cantidad, monedas):
    # Crear un modelo de Pyomo
    model = ConcreteModel()

    # Variable de decisión: cantidad de cada tipo de moneda a usar
    model.x = Var(monedas, within=NonNegativeIntegers)

    # Función objetivo: minimizar la cantidad total de monedas
    model.obj = Objective(expr=sum(model.x[moneda] for moneda in monedas), sense=minimize)

    # Restricción: la suma de las monedas debe ser igual a la cantidad
    model.restriccion = Constraint(expr=sum(moneda*model.x[moneda] for moneda in monedas) == cantidad)

    # Restricción: 5 monedas de 5 centavo
    def restriccion_centavos(_model, coin):
        if coin == 5:
            return _model.x[coin] == 5
        else:
            return Constraint.Skip

    # model.restriccion_5_centavos = Constraint( monedas, rule=restriccion_centavos)

    # Resolver el modelo
    solver = SolverFactory('glpk')
    result = solver.solve(model)

    # Imprimir resultados
    if result.solver.status == SolverStatus.ok and result.solver.termination_condition == TerminationCondition.optimal:
        for moneda in monedas:
            if model.x[moneda].value > 0:
                print('Cantidad de monedas de', moneda, ':', int(model.x[moneda].value))
    else:
        print('No se encontró solución')


if __name__ == '__main__':
    cantidad = 83
    monedas = [1, 5, 10, 25, 50, 100]
    resolver_cambio_moneda(cantidad, monedas)

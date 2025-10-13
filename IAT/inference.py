from pgmpy.inference import VariableElimination
from model import model

def calcular_probabilidades():
    """
    Calcula las probabilidades solicitadas en el ejercicio
    """
    # Crear objeto de inferencia
    inferencia = VariableElimination(model)

    print(f'\n{"="*70}')
    print(f'SOLUCIÓN DEL EJERCICIO - REDES BAYESIANAS')
    print(f'{"="*70}\n')

    # PREGUNTA 1: P(FS="Si" | CE="Si")

    print("PREGUNTA 1:")
    print("Calcular la probabilidad de que el servidor falle si")
    print("se sabe que hubo un corte de energía.\n")

    resultado1 = inferencia.query(
        variables=['FS'],
        evidence={'CE': 1}  # CE="Si" (1=Si, 0=No)
    )

    prob1 = resultado1.values[1]  # Probabilidad de FS="Si"

    print(f'P(FS="Si" | CE="Si") = {prob1:.6f}')
    print(f'\n Respuesta: Hay un {prob1*100:.2f}% de probabilidad')
    print(f'de que el servidor falle.\n')


    # PREGUNTA 2: P(FS="Si" | CE="Si", ACT="No")

    print(f'  {"─"*66}\n')
    print("PREGUNTA 2:")
    print("Calcular la probabilidad de que el servidor falle si")
    print("se sabe que:")
    print("- Hubo un corte de energía")
    print("- NO hubo alta carga de trabajo\n")

    resultado2 = inferencia.query(
        variables=['FS'],
        evidence={'CE': 1, 'ACT': 0}  # CE="Si", ACT="No"
    )

    prob2 = resultado2.values[1]  # Probabilidad de FS="Si"

    print(f' P(FS="Si" | CE="Si", ACT="No") = {prob2:.6f}')
    print(f'\n Respuesta: Hay un {prob2*100:.2f}% de probabilidad')
    print(f' de que el servidor falle.\n')


    # ANÁLISIS COMPARATIVO

    print(f' {"─"*66}\n')
    print(" ANÁLISIS:")
    print(f' {"─"*62}\n')

    diferencia = prob1 - prob2
    print(f' Con corte de energía solamente:    {prob1*100:.2f}%')
    print(f' Con corte + SIN alta carga:        {prob2*100:.2f}%')
    print(f'\n Diferencia:                        {abs(diferencia)*100:.2f}%\n')

    if diferencia > 0:
        print(f'La AUSENCIA de alta carga de trabajo REDUCE')
        print(f'la probabilidad de falla en {abs(diferencia)*100:.2f}%.')
    else:
        print(f'La AUSENCIA de alta carga de trabajo AUMENTA')
        print(f'la probabilidad de falla en {abs(diferencia)*100:.2f}%.')

    print(f'\n{"="*70}\n')

    return prob1, prob2

if __name__ == "__main__":
    calcular_probabilidades()
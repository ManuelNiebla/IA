from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD

# Crear la estructura de la red
model = DiscreteBayesianNetwork([
    ('CE', 'MF'),   # Corte de Energía -> Mal Funcionamiento
    ('ACT', 'SC'),  # Actividad -> Sobrecarga
    ('MF', 'SC'),   # Mal Funcionamiento -> Sobrecarga
    ('SC', 'FS'),   # Sobrecarga -> Falla del Servidor
    ('MF', 'FS')    # Mal Funcionamiento -> Falla del Servidor
])

# P(CE) - Corte de Energía
cpd_ce = TabularCPD(
    variable='CE',
    variable_card=2,
    values=[[0.90],  # No
            [0.10]]  # Si
)

# P(ACT) - Actividad
cpd_act = TabularCPD(
    variable='ACT',
    variable_card=2,
    values=[[0.70],  # No
            [0.30]]  # Si
)

# P(MF | CE) - Mal Funcionamiento dado Corte de Energía
cpd_mf = TabularCPD(
    variable='MF',
    variable_card=2,
    values=[
        [0.95, 0.20],  # No: [CE=No, CE=Si]
        [0.05, 0.80]   # Si: [CE=No, CE=Si]
    ],
    evidence=['CE'],
    evidence_card=[2]
)

# P(SC | ACT, MF) - Sobrecarga dado Actividad y Mal Funcionamiento
cpd_sc = TabularCPD(
    variable='SC',
    variable_card=2,
    values=[
        #  ACT=No      ACT=Si
        #  MF=No MF=Si MF=No MF=Si
        [0.90, 0.40, 0.30, 0.10],  # No
        [0.10, 0.60, 0.70, 0.90]   # Si
    ],
    evidence=['ACT', 'MF'],
    evidence_card=[2, 2]
)

# P(FS | SC, MF) - Falla del Servidor dado Sobrecarga y Mal Funcionamiento
cpd_fs = TabularCPD(
    variable='FS',
    variable_card=2,
    values=[
        #  SC=No       SC=Si
        #  MF=No MF=Si MF=No MF=Si
        [0.95, 0.20, 0.30, 0.05],  # No
        [0.05, 0.80, 0.70, 0.95]   # Si
    ],
    evidence=['SC', 'MF'],
    evidence_card=[2, 2]
)

# Agregar CPDs al modelo
model.add_cpds(cpd_ce, cpd_act, cpd_mf, cpd_sc, cpd_fs)

# Verificar que el modelo es válido
assert model.check_model()

print("Modelo de Red Bayesiana creado exitosamente")
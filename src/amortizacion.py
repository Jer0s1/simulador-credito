import pandas as pd
from dateutil.relativedelta import relativedelta

DELTA_PERIODICIDAD = {
    "mensual": relativedelta(months=1),
    "bimestral": relativedelta(months=2),
    "trimestral": relativedelta(months=3),
    "semestral": relativedelta(months=6),
    "anual": relativedelta(years=1),
}


def cuota_francesa(capital, tasa, periodos):
    if tasa == 0:
        return capital / periodos
    return capital * tasa / (1 - (1 + tasa) ** -periodos)


def generar_periodos_pactada(inicio, frecuencia, limite=500):
    periodos = set()
    p = inicio
    while p <= limite:
        periodos.add(p)
        p += frecuencia
    return periodos


def tabla_francesa(capital, tasa_periodica, periodos, fecha_desembolso, periodicidad,
                   abonos_extraordinarios=None, cuota_pactada=None,
                   cuota_pactada_inicio=1, cuota_pactada_frecuencia=1,
                   recalculo="plazo"):
    abonos = abonos_extraordinarios or {}
    delta = DELTA_PERIODICIDAD[periodicidad]
    filas = []
    saldo = capital

    # Periodo 0: desembolso
    filas.append({
        "n": 0,
        "Fecha": fecha_desembolso,
        "Saldo inicial": 0.0,
        "Cuota": 0.0,
        "Interes": 0.0,
        "Abono capital": 0.0,
        "Abono extraordinario": 0.0,
        "Cuota pactada": 0.0,
        "Saldo final": round(capital, 2),
        "Tasa periodica": tasa_periodica,
    })

    cuota_fija = cuota_francesa(capital, tasa_periodica, periodos)
    periodos_pactada = generar_periodos_pactada(cuota_pactada_inicio, cuota_pactada_frecuencia) if cuota_pactada else set()
    fecha = fecha_desembolso + delta

    for periodo in range(1, periodos + 1):
        interes = round(saldo * tasa_periodica, 2)
        es_ultimo = (periodo == periodos)

        if es_ultimo:
            abono_capital = round(saldo, 2)
            cuota_periodo = round(abono_capital + interes, 2)
            abono_extraordinario = 0.0
            abono_pactado = 0.0
            saldo_final = 0.0
        else:
            cuota_periodo = round(cuota_fija, 2)
            abono_capital = round(cuota_periodo - interes, 2)
            if abono_capital < 0:
                abono_capital = 0.0
                cuota_periodo = interes

            saldo_tras_cuota = round(saldo - abono_capital, 2)

            abono_extraordinario = round(min(abonos.get(periodo, 0), saldo_tras_cuota), 2)
            saldo_tras_extra = round(saldo_tras_cuota - abono_extraordinario, 2)

            abono_pactado = round(min(cuota_pactada or 0, saldo_tras_extra) if periodo in periodos_pactada else 0, 2)
            saldo_final = round(saldo_tras_extra - abono_pactado, 2)

            if recalculo == "cuota" and (abono_extraordinario + abono_pactado) > 0:
                periodos_restantes = periodos - periodo
                if periodos_restantes > 0 and saldo_final > 0:
                    cuota_fija = cuota_francesa(saldo_final, tasa_periodica, periodos_restantes)

        filas.append({
            "n": periodo,
            "Fecha": fecha,
            "Saldo inicial": round(saldo, 2),
            "Cuota": cuota_periodo,
            "Interes": interes,
            "Abono capital": abono_capital,
            "Abono extraordinario": abono_extraordinario,
            "Cuota pactada": abono_pactado,
            "Saldo final": saldo_final,
            "Tasa periodica": tasa_periodica,
        })

        saldo = saldo_final
        fecha = fecha + delta

    df = pd.DataFrame(filas)
    df = df.set_index("n")
    df.index.name = "n"
    return df


def tabla_abono_constante(capital, tasa_periodica, periodos, fecha_desembolso, periodicidad,
                          abonos_extraordinarios=None, cuota_pactada=None,
                          cuota_pactada_inicio=1, cuota_pactada_frecuencia=1):
    abonos = abonos_extraordinarios or {}
    delta = DELTA_PERIODICIDAD[periodicidad]
    abono_capital_fijo = round(capital / periodos, 2)
    filas = []
    saldo = capital

    filas.append({
        "n": 0,
        "Fecha": fecha_desembolso,
        "Saldo inicial": 0.0,
        "Cuota": 0.0,
        "Interes": 0.0,
        "Abono capital": 0.0,
        "Abono extraordinario": 0.0,
        "Cuota pactada": 0.0,
        "Saldo final": round(capital, 2),
        "Tasa periodica": tasa_periodica,
    })

    periodos_pactada = generar_periodos_pactada(cuota_pactada_inicio, cuota_pactada_frecuencia) if cuota_pactada else set()
    fecha = fecha_desembolso + delta

    for periodo in range(1, periodos + 1):
        interes = round(saldo * tasa_periodica, 2)
        es_ultimo = (periodo == periodos)

        if es_ultimo:
            abono_capital = round(saldo, 2)
            cuota = round(abono_capital + interes, 2)
            abono_extraordinario = 0.0
            abono_pactado = 0.0
            saldo_final = 0.0
        else:
            abono_capital = round(min(abono_capital_fijo, saldo), 2)
            cuota = round(abono_capital + interes, 2)

            saldo_tras_cuota = round(saldo - abono_capital, 2)

            abono_extraordinario = round(min(abonos.get(periodo, 0), saldo_tras_cuota), 2)
            saldo_tras_extra = round(saldo_tras_cuota - abono_extraordinario, 2)

            abono_pactado = round(min(cuota_pactada or 0, saldo_tras_extra) if periodo in periodos_pactada else 0, 2)
            saldo_final = round(saldo_tras_extra - abono_pactado, 2)

        filas.append({
            "n": periodo,
            "Fecha": fecha,
            "Saldo inicial": round(saldo, 2),
            "Cuota": cuota,
            "Interes": interes,
            "Abono capital": abono_capital,
            "Abono extraordinario": abono_extraordinario,
            "Cuota pactada": abono_pactado,
            "Saldo final": saldo_final,
            "Tasa periodica": tasa_periodica,
        })

        saldo = saldo_final
        fecha = fecha + delta

    df = pd.DataFrame(filas)
    df = df.set_index("n")
    df.index.name = "n"
    return df

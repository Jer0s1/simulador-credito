import pandas as pd
from dateutil.relativedelta import relativedelta
import math

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


def plazo_implicito_frances(capital, tasa, cuota):
    """
    Retorna (plazo_real, plazo_ceiled) en número de periodos.
    Si la cuota no amortiza (cuota <= interés del primer periodo), retorna (None, None).
    """
    if cuota <= 0 or capital <= 0:
        return None, None
    if tasa == 0:
        n = capital / cuota
        return n, int(math.ceil(n))

    interes_1 = capital * tasa
    if cuota <= interes_1:
        return None, None

    # n = -ln(1 - (PV*r)/P) / ln(1+r)
    n = -math.log(1 - (capital * tasa) / cuota) / math.log(1 + tasa)
    return n, int(math.ceil(n))


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
                   recalculo="plazo", max_periodos=1000):
    abonos = abonos_extraordinarios or {}
    delta = DELTA_PERIODICIDAD[periodicidad]
    filas = []
    saldo = capital

    # Periodo 0: desembolso
    filas.append({
        "n": 0,
        "Fecha": fecha_desembolso,
        "Cuota": 0.0,
        "Interes": 0.0,
        "Abono capital": 0.0,
        "Abono extraordinario": 0.0,
        "Cuota pactada": 0.0,
        "Saldo final": round(capital, 2),
        "Tasa periodica": tasa_periodica,
    })

    cuota_fija = cuota_francesa(capital, tasa_periodica, periodos)
    periodos_pactada = generar_periodos_pactada(
        cuota_pactada_inicio, cuota_pactada_frecuencia, limite=max_periodos
    ) if cuota_pactada else set()
    fecha = fecha_desembolso + delta

    # Si el usuario define una cuota pactada para todos los periodos y pide recalcular plazo,
    # podemos extender/reducir el número de periodos hasta cancelar el saldo.
    usar_plazo_variable = (
        recalculo == "plazo"
        and cuota_pactada is not None
        and cuota_pactada_inicio == 1
        and cuota_pactada_frecuencia == 1
        and len(abonos) == 0
    )

    periodo = 1
    while True:
        if not usar_plazo_variable and periodo > periodos:
            break
        if usar_plazo_variable and periodo > max_periodos:
            break

        interes = round(saldo * tasa_periodica, 4)
        cuota_sugerida = round(cuota_pactada, 2) if (cuota_pactada is not None and periodo in periodos_pactada) else round(cuota_fija, 2)

        # Determinar si este periodo liquida el saldo.
        pago_total = cuota_sugerida
        cubre_interes = pago_total >= interes
        if not cubre_interes:
            # El simulador no hace capitalización de intereses; solo advierte y limita el pago a interés.
            pago_total = interes

        abono_capital = round(min(max(pago_total - interes, 0.0), saldo), 2)
        saldo_tras_cuota = round(saldo - abono_capital, 2)

        abono_extraordinario = 0.0
        if saldo_tras_cuota > 0:
            abono_extraordinario = round(
                min(abonos.get(periodo, 0), saldo_tras_cuota), 2
            )
        saldo_tras_extra = round(saldo_tras_cuota - abono_extraordinario, 2)

        saldo_final = saldo_tras_extra
        es_ultimo = saldo_final <= 0

        # Si es el último, ajustamos la cuota para liquidar exactamente (cuota = interés + saldo),
        # sin exceder por redondeos.
        if es_ultimo:
            abono_capital = round(saldo, 2)
            pago_total = round(abono_capital + interes, 2)
            abono_extraordinario = 0.0
            saldo_final = 0.0

        # Si hay abonos y se quiere recalcular la cuota, recomputamos con el saldo remanente.
        if (
            not es_ultimo
            and recalculo == "cuota"
            and abono_extraordinario > 0
        ):
            periodos_restantes = max(periodos - periodo, 0)
            if periodos_restantes > 0 and saldo_final > 0:
                cuota_fija = cuota_francesa(saldo_final, tasa_periodica, periodos_restantes)

        filas.append({
            "n": periodo,
            "Fecha": fecha,
            "Cuota": pago_total,
            "Interes": interes,
            "Abono capital": abono_capital,
            "Abono extraordinario": abono_extraordinario,
            "Cuota pactada": round(cuota_pactada, 2) if (cuota_pactada is not None and periodo in periodos_pactada) else 0.0,
            "Cubre intereses": bool(cubre_interes),
            "Saldo final": saldo_final,
            "Tasa periodica": tasa_periodica,
        })

        saldo = saldo_final
        fecha = fecha + delta

        if es_ultimo:
            break
        periodo += 1

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
        "Cuota": 0.0,
        "Interes": 0.0,
        "Abono capital": 0.0,
        "Abono extraordinario": 0.0,
        "Cuota pactada": 0.0,
        "Saldo final": round(capital, 2),
        "Tasa periodica": tasa_periodica,
    })

    periodos_pactada = generar_periodos_pactada(
        cuota_pactada_inicio, cuota_pactada_frecuencia) if cuota_pactada else set()
    fecha = fecha_desembolso + delta

    for periodo in range(1, periodos + 1):
        interes = round(saldo * tasa_periodica, 4)
        es_ultimo = (periodo == periodos)

        if es_ultimo:
            abono_capital = round(saldo, 2)
            cuota = round(abono_capital + interes, 2)
            abono_extraordinario = 0.0
            cuota_pactada_valor = 0.0
            saldo_final = 0.0
        else:
            abono_capital = round(min(abono_capital_fijo, saldo), 2)
            cuota = round(abono_capital + interes, 2)

            saldo_tras_cuota = round(saldo - abono_capital, 2)

            abono_extraordinario = round(
                min(abonos.get(periodo, 0), saldo_tras_cuota), 2)
            saldo_tras_extra = round(
                saldo_tras_cuota - abono_extraordinario, 2)

            # La "cuota pactada" se trata como cuota (pago total) en los periodos seleccionados.
            cuota_pactada_valor = round(cuota_pactada, 2) if (cuota_pactada is not None and periodo in periodos_pactada) else 0.0
            if cuota_pactada_valor > 0:
                cuota = cuota_pactada_valor
                cubre_interes = cuota >= interes
                if not cubre_interes:
                    cuota = interes
                abono_capital = round(min(max(cuota - interes, 0.0), saldo_tras_extra), 2)
                saldo_final = round(saldo_tras_extra - abono_capital, 2)
            else:
                cubre_interes = True
                saldo_final = round(saldo_tras_extra, 2)

        filas.append({
            "n": periodo,
            "Fecha": fecha,
            "Cuota": cuota,
            "Interes": interes,
            "Abono capital": abono_capital,
            "Abono extraordinario": abono_extraordinario,
            "Cuota pactada": cuota_pactada_valor if not es_ultimo else 0.0,
            "Cubre intereses": bool(cubre_interes) if not es_ultimo else True,
            "Saldo final": saldo_final,
            "Tasa periodica": tasa_periodica,
        })

        saldo = saldo_final
        fecha = fecha + delta

    df = pd.DataFrame(filas)
    df = df.set_index("n")
    df.index.name = "n"
    return df

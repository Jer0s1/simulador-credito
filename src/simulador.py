from src.tasas import convertir_tasa, descripcion_conversion
from src.amortizacion import (
    tabla_francesa,
    tabla_abono_constante,
    cuota_francesa,
    plazo_implicito_frances,
)


def resumen_financiero(df):
    df_pagos = df[df.index > 0]
    return {
        # "Cuota" ya representa el pago total del periodo (sea teórica o pactada).
        "Total pagado": df_pagos["Cuota"].sum() + df_pagos["Abono extraordinario"].sum(),
        "Total intereses": df_pagos["Interes"].sum(),
        "Total abono capital": df_pagos["Abono capital"].sum() + df_pagos["Abono extraordinario"].sum(),
        "Cuota inicial": df_pagos["Cuota"].iloc[0],
        "Cuota final": df_pagos["Cuota"].iloc[-1],
        "Numero de periodos": len(df_pagos),
    }


def formato_moneda(valor, decimales=0):
    texto = f"{valor:,.{decimales}f}"
    texto = texto.replace(".", "_").replace(",", ".").replace("_", ",")
    return f"${texto}"


def ejecutar_simulacion(capital, plazo, periodicidad, tipo_tasa, valor_tasa,
                        sistema, fecha_desembolso, abonos_extraordinarios=None,
                        cuota_pactada=None, cuota_pactada_inicio=1,
                        cuota_pactada_frecuencia=1, recalculo="plazo"):
    advertencias = []
    tasa_periodica = convertir_tasa(valor_tasa, tipo_tasa, periodicidad)
    desc_tasa = descripcion_conversion(
        valor_tasa, tipo_tasa, periodicidad, tasa_periodica)

    # Validación de cuota pactada (si se interpreta como cuota/pago del periodo).
    if cuota_pactada is not None:
        cuota_teorica = cuota_francesa(
            capital, tasa_periodica, plazo) if sistema == "frances" else None

        if sistema == "frances":
            n_real, n_ceiled = plazo_implicito_frances(
                capital, tasa_periodica, cuota_pactada)
            if n_ceiled is None:
                advertencias.append(
                    "La cuota pactada no es financieramente viable: no cubre los intereses del primer periodo "
                    "(la deuda no amortiza con esa cuota)."
                )
            else:
                if cuota_teorica is not None and abs(cuota_pactada - cuota_teorica) > 0.01:
                    advertencias.append(
                        f"La cuota pactada ({formato_moneda(cuota_pactada)}) no coincide con la cuota teórica "
                        f"({formato_moneda(cuota_teorica)}) para plazo={plazo}. Plazo implícito aproximado: {n_ceiled} periodos."
                    )

    if sistema == "frances":
        tabla = tabla_francesa(
            capital, tasa_periodica, plazo, fecha_desembolso,
            periodicidad, abonos_extraordinarios,
            cuota_pactada, cuota_pactada_inicio, cuota_pactada_frecuencia,
            recalculo
        )
    elif sistema == "abono_constante":
        tabla = tabla_abono_constante(
            capital, tasa_periodica, plazo, fecha_desembolso,
            periodicidad, abonos_extraordinarios,
            cuota_pactada, cuota_pactada_inicio, cuota_pactada_frecuencia
        )
    else:
        raise ValueError(f"Sistema de amortizacion no soportado: {sistema}")

    if "Tasa periodica" in tabla.columns:
        tabla = tabla.drop(columns=["Tasa periodica"])

    if "Cubre intereses" in tabla.columns and not bool(tabla.loc[tabla.index > 0, "Cubre intereses"].all()):
        advertencias.append(
            "Hay periodos donde la cuota no cubre los intereses generados. Revisa la columna 'Cubre intereses'."
        )

    resumen = resumen_financiero(tabla)
    return tabla, resumen, tasa_periodica, desc_tasa, advertencias

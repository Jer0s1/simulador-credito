from src.tasas import convertir_tasa, descripcion_conversion
from src.amortizacion import tabla_francesa, tabla_abono_constante, cuota_francesa


def resumen_financiero(df):
    df_pagos = df[df.index > 0]
    return {
        "Total pagado": df_pagos["Cuota"].sum() + df_pagos["Abono extraordinario"].sum() + df_pagos["Cuota pactada"].sum(),
        "Total intereses": df_pagos["Interes"].sum(),
        "Total abono capital": df_pagos["Abono capital"].sum() + df_pagos["Abono extraordinario"].sum() + df_pagos["Cuota pactada"].sum(),
        "Cuota inicial": df_pagos["Cuota"].iloc[0],
        "Cuota final": df_pagos["Cuota"].iloc[-1],
        "Numero de periodos": len(df_pagos),
    }


def ejecutar_simulacion(capital, plazo, periodicidad, tipo_tasa, valor_tasa,
                        sistema, fecha_desembolso, abonos_extraordinarios=None,
                        cuota_pactada=None, cuota_pactada_inicio=1,
                        cuota_pactada_frecuencia=1, recalculo="plazo"):
    advertencias = []
    tasa_periodica = convertir_tasa(valor_tasa, tipo_tasa, periodicidad)
    desc_tasa = descripcion_conversion(valor_tasa, tipo_tasa, periodicidad, tasa_periodica)

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

    resumen = resumen_financiero(tabla)
    return tabla, resumen, tasa_periodica, desc_tasa, advertencias
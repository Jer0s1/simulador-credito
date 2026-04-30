NOMBRES_TASA = {
    "EA":   "Tasa efectiva anual",
    "NAMV": "Tasa nominal anual MV",
    "NATV": "Tasa nominal anual TV",
    "NASV": "Tasa nominal anual SV",
    "PM":   "Tasa efectiva mensual",
    "PT":   "Tasa efectiva trimestral",
}

ABREVIATURA_PERIODICA = {
    "mensual":    "EM",
    "bimestral":  "EB",
    "trimestral": "ET",
    "semestral":  "ES",
    "anual":      "EA",
}


def nominal_a_efectiva_anual(tasa_nominal, periodos_por_anio):
    tasa_periodica = tasa_nominal / periodos_por_anio
    return (1 + tasa_periodica) ** periodos_por_anio - 1


def efectiva_anual_a_periodica(tasa_ea, periodos_por_anio):
    return (1 + tasa_ea) ** (1 / periodos_por_anio) - 1


def convertir_tasa(valor, tipo, periodicidad):
    periodos_anio = {
        "mensual": 12,
        "bimestral": 6,
        "trimestral": 4,
        "semestral": 2,
        "anual": 1,
    }
    n = periodos_anio[periodicidad]

    if tipo == "EA":
        ea = valor
    elif tipo == "NAMV":
        ea = nominal_a_efectiva_anual(valor, 12)
    elif tipo == "NATV":
        ea = nominal_a_efectiva_anual(valor, 4)
    elif tipo == "NASV":
        ea = nominal_a_efectiva_anual(valor, 2)
    elif tipo == "PM":
        ea = (1 + valor) ** 12 - 1
    elif tipo == "PT":
        ea = (1 + valor) ** 4 - 1
    else:
        raise ValueError(f"Tipo de tasa no soportado: {tipo}")

    return efectiva_anual_a_periodica(ea, n)


def descripcion_conversion(valor, tipo, periodicidad, tasa_periodica):
    nombre_entrada = NOMBRES_TASA.get(tipo, tipo)
    abrev_salida = ABREVIATURA_PERIODICA.get(periodicidad, periodicidad)
    nombre_salida = f"Tasa efectiva {periodicidad}"
    return (
        f"{nombre_entrada}: {valor * 100:.4f}% {tipo} "
        f"-> {nombre_salida} ({abrev_salida}): {tasa_periodica * 100:.6f}%"
    )
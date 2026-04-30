import streamlit as st
from datetime import date
from src.simulador import ejecutar_simulacion

st.set_page_config(page_title="Simulador de Credito", layout="wide")
st.title("Simulador de Credito - Tabla de Amortizacion")

with st.sidebar:
    st.header("Parametros del credito")

    capital = st.number_input("Valor del credito", min_value=1000.0, value=10000000.0, step=100000.0)
    plazo = st.number_input("Plazo (numero de cuotas)", min_value=1, value=24, step=1)
    periodicidad = st.selectbox("Periodicidad de pago", ["mensual", "bimestral", "trimestral", "semestral", "anual"])
    tipo_tasa = st.selectbox("Tipo de tasa", ["EA", "NAMV", "NATV", "NASV", "PM", "PT"])
    valor_tasa = st.number_input("Valor de la tasa (%)", min_value=0.01, value=12.0, step=0.1) / 100
    sistema = st.selectbox("Sistema de amortizacion", ["frances", "abono_constante"])
    fecha_desembolso = st.date_input("Fecha de desembolso", value=date.today())
    recalculo = st.radio("Si hay abonos, recalcular:", ["plazo", "cuota"])

    st.subheader("Cuota pactada (opcional)")
    usar_cuota_pactada = st.checkbox("Agregar cuota pactada periodica")
    cuota_pactada = None
    cuota_pactada_inicio = 1
    cuota_pactada_frecuencia = 1
    if usar_cuota_pactada:
        cuota_pactada = st.number_input("Monto cuota pactada", min_value=1.0, value=500000.0)
        cuota_pactada_inicio = st.number_input("Periodo de inicio", min_value=1, value=1, step=1)
        cuota_pactada_frecuencia = st.number_input("Frecuencia (cada cuantos periodos)", min_value=1, value=1, step=1)
        st.caption(f"Se aplicara en los periodos: {int(cuota_pactada_inicio)}, {int(cuota_pactada_inicio + cuota_pactada_frecuencia)}, {int(cuota_pactada_inicio + 2*cuota_pactada_frecuencia)}...")

    st.subheader("Abonos extraordinarios")
    abonos_texto = st.text_area("Periodo:monto (uno por linea)\nEjemplo:\n6:500000\n12:1000000")

abonos = {}
if abonos_texto:
    for linea in abonos_texto.strip().split("\n"):
        try:
            p, m = linea.split(":")
            abonos[int(p.strip())] = float(m.strip())
        except ValueError:
            st.warning(f"Linea ignorada (formato invalido): {linea}")

if st.button("Calcular"):
    try:
        tabla, resumen, tasa_periodica, desc_tasa, advertencias = ejecutar_simulacion(
            capital=capital,
            plazo=int(plazo),
            periodicidad=periodicidad,
            tipo_tasa=tipo_tasa,
            valor_tasa=valor_tasa,
            sistema=sistema,
            fecha_desembolso=fecha_desembolso,
            abonos_extraordinarios=abonos,
            cuota_pactada=cuota_pactada,
            cuota_pactada_inicio=int(cuota_pactada_inicio),
            cuota_pactada_frecuencia=int(cuota_pactada_frecuencia),
            recalculo=recalculo,
        )

        for adv in advertencias:
            st.warning(adv)

        st.subheader("Tasa periodica utilizada")
        st.info(desc_tasa)

        st.subheader("Resumen financiero")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total pagado", f"${resumen['Total pagado']:,.0f}")
        col2.metric("Total intereses", f"${resumen['Total intereses']:,.0f}")
        col3.metric("Total abono capital", f"${resumen['Total abono capital']:,.0f}")
        col1.metric("Cuota inicial", f"${resumen['Cuota inicial']:,.0f}")
        col2.metric("Cuota final", f"${resumen['Cuota final']:,.0f}")
        col3.metric("Periodos efectivos", resumen["Numero de periodos"])

        st.subheader("Tabla de amortizacion")
        st.dataframe(tabla, use_container_width=True)

    except Exception as e:
        st.error(f"Error en el calculo: {e}")
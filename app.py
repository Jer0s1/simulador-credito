import streamlit as st
from datetime import date
from src.simulador import ejecutar_simulacion
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Crédito", layout="wide")


def formato_moneda(valor, decimales=2):
    texto = f"{valor:,.{decimales}f}"
    texto = texto.replace(".", "_").replace(",", ".").replace("_", ",")
    return f"${texto}"


def formatear_tabla_moneda(tabla):
    columnas_moneda = [
        "Cuota",
        "Interes",
        "Abono capital",
        "Abono extraordinario",
        "Cuota pactada",
        "Saldo final",
    ]
    formato = {col: lambda v: formato_moneda(
        v) for col in columnas_moneda if col in tabla.columns}
    return tabla.style.format(formato)


st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #0b6e4f;
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 16px;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #0f8b61;
    }
    .card {
        background-color: white;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        padding: 24px;
        margin: 16px 0;
    }
    .stTextInput, .stNumberInput, .stSelectbox, .stTextArea, .stDateInput {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def preparar_tabla_graficas(tabla):
    if hasattr(tabla, 'reset_index'):
        df = tabla.reset_index()
        if 'n' in df.columns and 'Periodo' not in df.columns:
            df = df.rename(columns={'n': 'Periodo'})
        return df
    return tabla


if 'vista' not in st.session_state:
    st.session_state.vista = 'datos'

if 'capital' not in st.session_state:
    st.session_state.capital = 10000000.0
    st.session_state.plazo = 24
    st.session_state.fecha_desembolso = date.today()
    st.session_state.periodicidad = 'mensual'
    st.session_state.tipo_tasa = 'EA'
    st.session_state.valor_tasa_raw = 12.0
    st.session_state.sistema = 'frances'
    st.session_state.recalculo = 'Mantener plazo'
    st.session_state.abonos_texto = ''
    st.session_state.usar_cuota_pactada = False
    st.session_state.cuota_pactada = 500000.0
    st.session_state.cuota_pactada_inicio = 1
    st.session_state.cuota_pactada_frecuencia = 1

if st.session_state.vista == 'datos':
    st.title("Simulador de Crédito - Información del Crédito")

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            capital = st.number_input(
                "Valor del crédito", min_value=1000.0, value=st.session_state.capital, step=100000.0)
            st.session_state.capital = capital
            st.caption(
                f"Valor del crédito formateado: {formato_moneda(capital, 0)}")
            plazo = st.number_input(
                "Plazo (número de cuotas)", min_value=1, value=st.session_state.plazo, step=1)
            st.session_state.plazo = plazo
            fecha_desembolso = st.date_input(
                "Fecha inicial", value=st.session_state.fecha_desembolso)
            st.session_state.fecha_desembolso = fecha_desembolso
            periodicidad = st.selectbox("Periodicidad de pago", [
                                        "mensual", "bimestral", "trimestral", "semestral", "anual"], index=["mensual", "bimestral", "trimestral", "semestral", "anual"].index(st.session_state.periodicidad))
            st.session_state.periodicidad = periodicidad
        with col2:
            tipo_tasa = st.selectbox(
                "Tipo de tasa", ["EA", "NAMV", "NATV", "NASV", "PM", "PT"], index=["EA", "NAMV", "NATV", "NASV", "PM", "PT"].index(st.session_state.tipo_tasa))
            st.session_state.tipo_tasa = tipo_tasa
            valor_tasa = st.number_input(
                "Valor de la tasa (%)", min_value=0.01, value=st.session_state.valor_tasa_raw, step=0.1) / 100
            st.session_state.valor_tasa_raw = valor_tasa * 100
            sistema = st.selectbox("Sistema de amortización", [
                                   "frances", "abono_constante"], index=["frances", "abono_constante"].index(st.session_state.sistema))
            st.session_state.sistema = sistema
            recalculo = st.radio("Opciones de recálculo", [
                                 "Mantener plazo", "Mantener cuota"], index=["Mantener plazo", "Mantener cuota"].index(st.session_state.recalculo))
            st.session_state.recalculo = recalculo

        st.subheader("Abonos extraordinarios")
        abonos_texto = st.text_area(
            "Periodo:monto (uno por línea)\nEjemplo:\n6:500000\n12:1000000", value=st.session_state.abonos_texto)
        st.session_state.abonos_texto = abonos_texto

        st.subheader("Cuota pactada")
        usar_cuota_pactada = st.checkbox("Agregar cuota pactada periódica", value=st.session_state.usar_cuota_pactada)
        st.session_state.usar_cuota_pactada = usar_cuota_pactada
        cuota_pactada = None
        cuota_pactada_inicio = 1
        cuota_pactada_frecuencia = 1
        if usar_cuota_pactada:
            cuota_pactada = st.number_input(
                "Monto cuota pactada", min_value=1.0, value=st.session_state.cuota_pactada)
            st.session_state.cuota_pactada = cuota_pactada
            st.caption(
                f"Monto pactado formateado: {formato_moneda(cuota_pactada, 0)}")
            cuota_pactada_inicio = st.number_input(
                "Periodo de inicio", min_value=1, value=st.session_state.cuota_pactada_inicio, step=1)
            st.session_state.cuota_pactada_inicio = cuota_pactada_inicio
            cuota_pactada_frecuencia = st.number_input(
                "Frecuencia (cada cuantos periodos)", min_value=1, value=st.session_state.cuota_pactada_frecuencia, step=1)
            st.session_state.cuota_pactada_frecuencia = cuota_pactada_frecuencia

        st.markdown('</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 3])
    with col_left:
        if st.button("Ver Resultados", key="ver_resultados"):
            abonos = {}
            if abonos_texto:
                for linea in abonos_texto.strip().split("\n"):
                    try:
                        p, m = linea.split(":")
                        abonos[int(p.strip())] = float(m.strip())
                    except ValueError:
                        st.warning(
                            f"Línea ignorada (formato inválido): {linea}")

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
                    recalculo=recalculo.lower().replace("mantener ", ""),
                )
                st.session_state.tabla = tabla
                st.session_state.resumen = resumen
                st.session_state.desc_tasa = desc_tasa
                st.session_state.advertencias = advertencias
                st.session_state.vista = 'resultados'
                st.rerun()
            except Exception as e:
                st.error(f"Error en el cálculo: {e}")

elif st.session_state.vista == 'resultados':
    st.title("Simulador de Crédito - Resultados y Análisis")

    for adv in st.session_state.advertencias:
        st.warning(adv)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Tasa periódica utilizada")
    st.info(st.session_state.desc_tasa)

    st.subheader("Resumen financiero")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total pagado", formato_moneda(
        st.session_state.resumen['Total pagado'], 0))
    col2.metric("Total intereses", formato_moneda(
        st.session_state.resumen['Total intereses'], 0))
    col3.metric("Total abono capital", formato_moneda(
        st.session_state.resumen['Total abono capital'], 0))
    col1.metric("Cuota inicial", formato_moneda(
        st.session_state.resumen['Cuota inicial'], 0))
    col2.metric("Cuota final", formato_moneda(
        st.session_state.resumen['Cuota final'], 0))
    col3.metric("Periodos efectivos",
                st.session_state.resumen["Numero de periodos"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Tabla de amortización")
    st.dataframe(formatear_tabla_moneda(st.session_state.tabla),
                 use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Ver Gráficas", key="ver_graficas"):
        st.session_state.vista = 'graficas'
        st.rerun()

    if st.button("Regresar", key="modificar_datos"):
        st.session_state.vista = 'datos'
        st.rerun()

elif st.session_state.vista == 'graficas':
    st.title("Simulador de Crédito - Gráficas Financieras")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Análisis Visual")

    tabla = preparar_tabla_graficas(st.session_state.tabla)

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.line(tabla, x='Fecha', y='Saldo final',
                       title='Evolución del Saldo')
        fig1.update_traces(line=dict(width=2.5), marker=dict(size=4))
        fig1.update_layout(plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(255,255,255,0)',
                           xaxis=dict(showgrid=True, gridwidth=0.3,
                                      gridcolor='rgba(0,0,0,0.08)'),
                           yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(tabla, x='Fecha', y=[
                      'Interes', 'Abono capital', 'Abono extraordinario'], title='Intereses, Abono Capital y Abonos Extraordinarios')
        fig2.update_traces(marker_line_width=0.5)
        fig2.update_layout(barmode='stack', plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(255,255,255,0)',
                           xaxis=dict(showgrid=True, gridwidth=0.3,
                                      gridcolor='rgba(0,0,0,0.08)'),
                           yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Regresar", key="regresar_resultados"):
        st.session_state.vista = 'resultados'
        st.rerun()

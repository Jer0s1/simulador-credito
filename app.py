import streamlit as st
from datetime import date
from src.simulador import ejecutar_simulacion
import plotly.express as px
<<<<<<< HEAD
=======
import plotly.graph_objects as go
>>>>>>> d28740cba87c92615a9bbd3586218b27139e8d12

st.set_page_config(page_title="Simulador de Crédito", layout="wide")

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

<<<<<<< HEAD

def preparar_tabla_graficas(tabla):
    if hasattr(tabla, 'reset_index'):
        df = tabla.reset_index()
        if 'n' in df.columns and 'Periodo' not in df.columns:
            df = df.rename(columns={'n': 'Periodo'})
        return df
    return tabla


if 'vista' not in st.session_state:
    st.session_state.vista = 'datos'
=======
    capital = st.number_input(
        "Valor del credito",
        min_value=1000.0,
        value=10000000.0,
        step=100000.0,
        format="%0.0f"
    )
    st.caption(f"$ {capital:,.0f}".replace(",", "."))
    plazo = st.number_input("Plazo (numero de cuotas)",
                            min_value=1, value=24, step=1)
    periodicidad = st.selectbox("Periodicidad de pago", [
                                "mensual", "bimestral", "trimestral", "semestral", "anual"])
    opciones_tasa = {
        "Efectiva anual (EA)": "EA",
        "Nominal anual mes vencido (NAMV)": "NAMV",
        "Nominal anual trimestre vencido (NATV)": "NATV",
        "Nominal anual semestre vencido (NASV)": "NASV",
        "Efectiva mensual (PM)": "PM",
        "Efectiva trimestral (PT)": "PT",
    }
    tipo_tasa_seleccionada = st.selectbox("Tipo de tasa", list(opciones_tasa.keys()))
    tipo_tasa = opciones_tasa[tipo_tasa_seleccionada]
    valor_tasa = st.number_input(
        "Valor de la tasa (%)", min_value=0.01, value=12.0, step=0.1) / 100
    sistema = st.selectbox("Sistema de amortizacion", [
                           "frances", "abono_constante"])
    fecha_desembolso = st.date_input("Fecha de desembolso", value=date.today())
    recalculo = st.radio("Si hay abonos, recalcular:", ["plazo", "cuota"])

    st.subheader("Cuota pactada (opcional)")
    usar_cuota_pactada = st.checkbox("Agregar cuota pactada periodica")
    cuota_pactada = None
    cuota_pactada_inicio = 1
    cuota_pactada_frecuencia = 1
    if usar_cuota_pactada:
        cuota_pactada = st.number_input(
            "Monto cuota pactada", min_value=1.0, value=500000.0)
        cuota_pactada_inicio = st.number_input(
            "Periodo de inicio", min_value=1, value=1, step=1)
        cuota_pactada_frecuencia = st.number_input(
            "Frecuencia (cada cuantos periodos)", min_value=1, value=1, step=1)
        st.caption(
            f"Se aplicara en los periodos: {int(cuota_pactada_inicio)}, {int(cuota_pactada_inicio + cuota_pactada_frecuencia)}, {int(cuota_pactada_inicio + 2*cuota_pactada_frecuencia)}...")

    st.subheader("Abonos extraordinarios")

    if "abonos_extra" not in st.session_state:
        st.session_state.abonos_extra = {}

    col_p, col_m = st.columns(2)
    with col_p:
        abono_periodo = st.number_input(
            "Periodo", min_value=1, value=1, step=1, key="abono_periodo_input")
    with col_m:
        abono_monto = st.number_input(
            "Monto", min_value=1.0, value=500000.0, step=100000.0,
            format="%0.0f", key="abono_monto_input")

    if st.button("Agregar abono", use_container_width=True):
        if int(abono_periodo) in st.session_state.abonos_extra:
            st.error(f"Ya existe un abono extraordinario en el periodo {int(abono_periodo)}. Elimínalo primero si deseas cambiarlo.")
        else:
            st.session_state.abonos_extra[int(abono_periodo)] = float(abono_monto)
            st.rerun()

    if st.session_state.abonos_extra:
        st.caption("Abonos agregados:")
        for per in sorted(st.session_state.abonos_extra.keys()):
            monto_val = st.session_state.abonos_extra[per]
            col_info, col_del = st.columns([3, 1])
            with col_info:
                st.write(f"Periodo {per}: ${monto_val:,.0f}")
            with col_del:
                if st.button("✕", key=f"del_abono_{per}"):
                    del st.session_state.abonos_extra[per]
                    st.rerun()

abonos = dict(st.session_state.get("abonos_extra", {}))
>>>>>>> d28740cba87c92615a9bbd3586218b27139e8d12

if st.session_state.vista == 'datos':
    st.title("Simulador de Crédito - Información del Crédito")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            capital = st.number_input("Valor del crédito", min_value=1000.0, value=10000000.0, step=100000.0)
            plazo = st.number_input("Plazo (número de cuotas)", min_value=1, value=24, step=1)
            fecha_desembolso = st.date_input("Fecha inicial", value=date.today())
            periodicidad = st.selectbox("Periodicidad de pago", ["mensual", "bimestral", "trimestral", "semestral", "anual"])
        with col2:
            tipo_tasa = st.selectbox("Tipo de tasa", ["EA", "NAMV", "NATV", "NASV", "PM", "PT"])
            valor_tasa = st.number_input("Valor de la tasa (%)", min_value=0.01, value=12.0, step=0.1) / 100
            sistema = st.selectbox("Sistema de amortización", ["frances", "abono_constante"])
            recalculo = st.radio("Opciones de recálculo", ["Mantener plazo", "Mantener cuota"])
        
        st.subheader("Abonos extraordinarios")
        abonos_texto = st.text_area("Periodo:monto (uno por línea)\nEjemplo:\n6:500000\n12:1000000")
        
        st.subheader("Cuota pactada")
        usar_cuota_pactada = st.checkbox("Agregar cuota pactada periódica")
        cuota_pactada = None
        cuota_pactada_inicio = 1
        cuota_pactada_frecuencia = 1
        if usar_cuota_pactada:
            cuota_pactada = st.number_input("Monto cuota pactada", min_value=1.0, value=500000.0)
            cuota_pactada_inicio = st.number_input("Periodo de inicio", min_value=1, value=1, step=1)
            cuota_pactada_frecuencia = st.number_input("Frecuencia (cada cuantos periodos)", min_value=1, value=1, step=1)
        
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
                        st.warning(f"Línea ignorada (formato inválido): {linea}")
            
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
    col1.metric("Total pagado", f"${st.session_state.resumen['Total pagado']:,.0f}")
    col2.metric("Total intereses", f"${st.session_state.resumen['Total intereses']:,.0f}")
    col3.metric("Total abono capital", f"${st.session_state.resumen['Total abono capital']:,.0f}")
    col1.metric("Cuota inicial", f"${st.session_state.resumen['Cuota inicial']:,.0f}")
    col2.metric("Cuota final", f"${st.session_state.resumen['Cuota final']:,.0f}")
    col3.metric("Periodos efectivos", st.session_state.resumen["Numero de periodos"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Tabla de amortización")
    st.dataframe(st.session_state.tabla, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Ver Gráficas", key="ver_graficas"):
        st.session_state.vista = 'graficas'
        st.rerun()
    
    if st.button("Regresar", key="modificar_datos"):
        st.session_state.vista = 'datos'
        st.rerun()

<<<<<<< HEAD
elif st.session_state.vista == 'graficas':
    st.title("Simulador de Crédito - Gráficas Financieras")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Análisis Visual")
    
    tabla = preparar_tabla_graficas(st.session_state.tabla)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.line(tabla, x='Periodo', y='Saldo final', title='Evolución del Saldo')
        fig1.update_traces(line=dict(width=2.5), marker=dict(size=4))
        fig1.update_layout(plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(255,255,255,0)',
                           xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'),
                           yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'))
        st.plotly_chart(fig1, use_container_width=True)
        
        fig3 = px.line(tabla, x='Periodo', y='Cuota', title='Comportamiento de Cuotas')
        fig3.update_traces(line=dict(width=2.5), marker=dict(size=4))
        fig3.update_layout(plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(255,255,255,0)',
                           xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'),
                           yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'))
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig2 = px.bar(tabla, x='Periodo', y=['Interes', 'Abono capital'], title='Intereses vs Capital')
        fig2.update_traces(marker_line_width=0.5)
        fig2.update_layout(barmode='group', plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(255,255,255,0)',
                           xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'),
                           yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='rgba(0,0,0,0.08)'))
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Regresar", key="regresar_resultados"):
        st.session_state.vista = 'resultados'
        st.rerun()
=======
        st.subheader("Tasa periodica utilizada")
        st.info(desc_tasa)

        st.subheader("Resumen financiero")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total pagado", f"${resumen['Total pagado']:,.0f}")
        col2.metric("Total intereses", f"${resumen['Total intereses']:,.0f}")
        col3.metric("Total abono capital",
                    f"${resumen['Total abono capital']:,.0f}")
        col1.metric("Cuota inicial", f"${resumen['Cuota inicial']:,.0f}")
        col2.metric("Cuota final", f"${resumen['Cuota final']:,.0f}")
        col3.metric("Periodos efectivos", resumen["Numero de periodos"])

        st.subheader("Tabla de amortizacion")
        tabla_formateada = tabla.style.format({
            "Cuota": "${:,.0f}",
            "Interes": "${:,.4f}",
            "Abono capital": "${:,.0f}",
            "Abono extraordinario": "${:,.0f}",
            "Cuota pactada": "${:,.0f}",
            "Saldo final": "${:,.0f}"
        })
        st.dataframe(tabla_formateada, use_container_width=True)

        st.subheader("Evolucion del saldo en el tiempo")

        # Crear gráfica del saldo
        fig_saldo = go.Figure()

        # Separar períodos con y sin abonos extraordinarios
        periodos_sin_abonos = []
        saldo_sin_abonos = []
        periodos_con_abonos = []
        saldo_con_abonos = []

        for idx in tabla.index:
            if tabla.loc[idx, 'Abono extraordinario'] > 0:
                periodos_con_abonos.append(idx)
                saldo_con_abonos.append(tabla.loc[idx, 'Saldo final'])
            else:
                periodos_sin_abonos.append(idx)
                saldo_sin_abonos.append(tabla.loc[idx, 'Saldo final'])

        # Línea normal del saldo
        fig_saldo.add_trace(go.Scatter(
            x=tabla.index,
            y=tabla['Saldo final'],
            mode='lines',
            name='Saldo final',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>Periodo %{x}</b><br>Saldo: $%{y:,.0f}<extra></extra>'
        ))

        # Markers normales (sin abonos extraordinarios)
        fig_saldo.add_trace(go.Scatter(
            x=periodos_sin_abonos,
            y=saldo_sin_abonos,
            mode='markers',
            name='Período normal',
            marker=dict(size=8, color='#1f77b4', symbol='circle'),
            hovertemplate='<b>Periodo %{x}</b><br>Saldo: $%{y:,.0f}<extra></extra>'
        ))

        # Markers para períodos con abonos extraordinarios
        fig_saldo.add_trace(go.Scatter(
            x=periodos_con_abonos,
            y=saldo_con_abonos,
            mode='markers',
            name='Período con abono extraordinario',
            marker=dict(size=12, color='#d62728', symbol='star',
                        line=dict(color='#8B0000', width=2)),
            hovertemplate='<b>Periodo %{x}</b><br>Saldo: $%{y:,.0f}<br><b>⭐ Abono Extraordinario</b><extra></extra>'
        ))

        fig_saldo.update_layout(
            title="Reducción del Saldo a lo largo del tiempo",
            xaxis_title="Periodo",
            yaxis_title="Saldo ($)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            yaxis=dict(tickformat='$,.0f')
        )

        st.plotly_chart(fig_saldo, use_container_width=True)

        # Crear gráfica de composición de cuota (Interés vs Capital)
        st.subheader("Composicion de la cuota: Interes vs Abono a Capital")

        fig_composicion = go.Figure()

        fig_composicion.add_trace(go.Bar(
            x=tabla.index,
            y=tabla['Abono capital'],
            name='Abono a capital',
            marker_color='#007FFF',
            hovertemplate='<b>Periodo %{x}</b><br>Abono capital: $%{y:,.0f}<extra></extra>'
        ))

        fig_composicion.add_trace(go.Bar(
            x=tabla.index,
            y=tabla['Interes'],
            name='Interés',
            marker_color='#50A5FA',
            hovertemplate='<b>Periodo %{x}</b><br>Interés: $%{y:,.4f}<extra></extra>'
        ))

        fig_composicion.add_trace(go.Bar(
            x=tabla.index,
            y=tabla['Abono extraordinario'],
            name='Abono extraordinario',
            marker_color='#28FA28',
            hovertemplate='<b>Periodo %{x}</b><br>Abono extraordinario: $%{y:,.0f}<extra></extra>'
        ))

        fig_composicion.update_layout(
            barmode='stack',
            title="Desglose de la cuota: Interés vs Abono a Capital vs Abono Extraordinario",
            xaxis_title="Periodo",
            yaxis_title="Monto ($)",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            yaxis=dict(tickformat='$,.0f')
        )

        st.plotly_chart(fig_composicion, use_container_width=True)

    except Exception as e:
        st.error(f"Error en el calculo: {e}")
>>>>>>> d28740cba87c92615a9bbd3586218b27139e8d12

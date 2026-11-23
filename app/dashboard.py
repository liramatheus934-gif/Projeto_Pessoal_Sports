import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Sports Analytics - Fadiga no Brasileirão", layout="wide")

st.title("⚽ Monitor de Fadiga e Risco Logístico — Brasileirão 2024")
st.markdown("Análise do impacto de viagens e densidade de calendário no desempenho dos clubes.")


@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/processed/partidas_fadiga_gold.csv")
    df["data_jogo"] = pd.to_datetime(df["data_jogo"])
    return df


@st.cache_resource
def treinar_modelo(df):
    df_mod = df.dropna(subset=["media_pontos_5_jogos"]).copy()
    df_mod["eh_mandante"] = (df_mod["mando"] == "Casa").astype(int)
    features = [
        "eh_mandante", "dias_descanso", "km_viagem_partida",
        "jogos_ultimos_7d", "jogos_ultimos_14d", "km_acumulado_14d",
        "media_pontos_5_jogos", "sequencia_fora_casa", "alerta_fadiga_alta"
    ]
    modelo = RandomForestClassifier(
        n_estimators=200, max_depth=5, min_samples_leaf=10,
        class_weight="balanced", random_state=42
    )
    modelo.fit(df_mod[features], df_mod["flag_derrota"])
    return modelo, features


df = carregar_dados()
modelo, features = treinar_modelo(df)

# --- ABAS DO DASHBOARD ---
aba1, aba2 = st.tabs(["📊 Raio-X por Clube", "🤖 Simulador de Risco de Fadiga"])

with aba1:
    clube_selecionado = st.selectbox("Selecione o Clube:", sorted(df["clube"].unique()))
    df_clube = df[df["clube"] == clube_selecionado].sort_values("data_jogo")

    col1, col2, col3 = st.columns(3)
    col1.metric("Km Totais Viajados", f"{df_clube['km_viagem_partida'].sum():,.0f} km")
    col2.metric("Jogos em Sobrecarga", int(df_clube["alerta_fadiga_alta"].sum()))
    col3.metric("Média de Pontos/Jogo", f"{df_clube['pontos'].mean():.2f}")

    fig = px.line(
        df_clube, x="data_jogo", y="km_acumulado_14d",
        markers=True, title=f"Carga Acumulada de Viagens (14 dias) — {clube_selecionado}",
        labels={"data_jogo": "Data", "km_acumulado_14d": "Km Acumulados (14d)"}
    )
    st.plotly_chart(fig, use_container_width=True)

with aba2:
    st.subheader("Simule o cenário pré-jogo de um elenco")
    c1, c2, c3 = st.columns(3)
    mando = c1.radio("Mando de Campo:", ["Casa", "Fora"])
    descanso = c2.slider("Dias de descanso:", 2, 14, 3)
    km_14d = c3.number_input("Km acumulados nos últimos 14 dias:", 0, 10000, 3200, step=200)

    c4, c5, c6 = st.columns(3)
    jogos_7d = c4.selectbox("Jogos nos últimos 7 dias:", [0, 1, 2, 3], index=2)
    jogos_14d = c5.selectbox("Jogos nos últimos 14 dias:", [0, 1, 2, 3, 4, 5], index=4)
    media_5j = c6.slider("Média de pontos nos últimos 5 jogos:", 0.0, 3.0, 1.4, 0.2)

    alerta = 1 if (jogos_14d >= 3 and km_14d >= 2500) else 0
    entrada = pd.DataFrame([{
        "eh_mandante": 1 if mando == "Casa" else 0,
        "dias_descanso": descanso,
        "km_viagem_partida": km_14d / 2,
        "jogos_ultimos_7d": jogos_7d,
        "jogos_ultimos_14d": jogos_14d,
        "km_acumulado_14d": km_14d,
        "media_pontos_5_jogos": media_5j,
        "sequencia_fora_casa": 1 if mando == "Fora" else 0,
        "alerta_fadiga_alta": alerta
    }])

    risco_derrota = modelo.predict_proba(entrada[features])[0][1] * 100
    st.divider()
    st.metric("Probabilidade Estimada de Derrota (Risco de Fadiga):", f"{risco_derrota:.1f}%")
    if alerta == 1:
        st.warning("⚠️ Alerta de Sobrecarga Logística ativo: considere rotação de elenco.")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


def treinar_e_avaliar_modelo(caminho_gold: str):
    # 1. Carregar a tabela final (Camada Gold)
    df = pd.read_csv(caminho_gold)
    df["data_jogo"] = pd.to_datetime(df["data_jogo"])

    # Ordenar cronologicamente para respeitar a linha do tempo do campeonato
    df = df.sort_values("data_jogo").reset_index(drop=True)

    # Remover as primeiras rodadas onde ainda não há histórico de 5 jogos anteriores
    df_modelo = df.dropna(subset=["media_pontos_5_jogos"]).copy()

    # Transformar coluna categórica 'mando' em número (1 = Casa, 0 = Fora)
    df_modelo["eh_mandante"] = (df_modelo["mando"] == "Casa").astype(int)

    # 2. Definir as variáveis explicativas (Features) e o alvo (Target)
    features = [
        "eh_mandante",
        "dias_descanso",
        "km_viagem_partida",
        "jogos_ultimos_7d",
        "jogos_ultimos_14d",
        "km_acumulado_14d",
        "media_pontos_5_jogos",
        "sequencia_fora_casa",
        "alerta_fadiga_alta",
    ]
    target = "flag_derrota"

    # 3. Divisão Temporal: 70% iniciais para Treino (1º Turno) e 30% finais para Teste (2º Turno)
    ponto_corte = int(len(df_modelo) * 0.70)
    treino = df_modelo.iloc[:ponto_corte]
    teste = df_modelo.iloc[ponto_corte:]

    X_train, y_train = treino[features], treino[target]
    X_test, y_test = teste[features], teste[target]

    print(f"Jogos no Treino: {len(X_train)} | Jogos no Teste: {len(X_test)}")

    # 4. Treinar o modelo Random Forest (equilibrando as classes)
    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42
    )
    modelo.fit(X_train, y_train)

    # 5. Avaliar no conjunto de Teste (2º Turno)
    previsoes = modelo.predict(X_test)
    probabilidades = modelo.predict_proba(X_test)[:, 1]

    print("\n--- Relatório de Classificação (Previsão de Derrota no 2º Turno) ---")
    print(classification_report(y_test, previsoes))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, probabilidades):.3f}")

    # 6. Gerar gráfico de Importância das Variáveis (Feature Importance)
    importancias = pd.DataFrame({
        "variavel": features,
        "importancia": modelo.feature_importances_
    }).sort_values("importancia", ascending=False)

    plt.figure(figsize=(9, 5))
    sns.barplot(data=importancias, x="importancia", y="variavel", color="#2b5c8f")
    plt.title("Quais Fatores Mais Pesam no Risco de Derrota? (Random Forest)", fontsize=12, fontweight="bold")
    plt.xlabel("Importância Relativa no Modelo")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("notebooks/grafico_importancia_variaveis.png", dpi=300)
    print("\nGráfico salvo em: notebooks/grafico_importancia_variaveis.png")


if __name__ == "__main__":
    treinar_e_avaliar_modelo("data/processed/partidas_fadiga_gold.csv")
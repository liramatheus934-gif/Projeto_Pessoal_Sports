# Projeto_Pessoal_Sports
# ⚽ Sports Analytics: Previsão de Fadiga e Risco Logístico no Brasileirão

Projeto de Ciência de Dados *end-to-end* desenvolvido para quantificar o impacto da densidade do calendário e das distâncias percorridas no desempenho dos 20 clubes da Série A do Campeonato Brasileiro (2024), apoiando decisões de rotação de elenco e prevenção de queda de rendimento.

---

## 🎯 Problema de Negócio
O calendário do futebol brasileiro impõe sequências intensas de partidas (intervalos de 72h) somadas a deslocamentos continentais. O objetivo deste projeto é transformar registros brutos de partidas em **indicadores fisiológicos e logísticos** capazes de responder:
1. Quantos pontos um time perde em média quando joga com pouco descanso ou após longas viagens?
2. É possível antecipar o risco de derrota antes da partida usando apenas variáveis pré-jogo de carga e calendário?

---

## 🏗️ Arquitetura do Projeto (Pipeline Medalhão)

```text
[Kaggle CSV (Bronze)] 
       │  (Python: Pandas + Cálculo Geoespacial Haversine)
       ▼
[Dados Limpos & Desdobrados (Silver)] ──► [MySQL 8.0 Workbench]
                                                  │  (SQL Window Functions: RANGE BETWEEN, LAG)
                                                  ▼
                                        [Camada Gold (View Analítica)]
                                           ├──► Análise Exploratória (Seaborn/Matplotlib)
                                           ├──► Modelo Preditivo (Random Forest)
                                           └──► Simulador Interativo (Streamlit)
import numpy as np
import pandas as pd

# 1. Coordenadas das sedes dos 20 clubes (para calcular retorno à base)
SEDES_CLUBES = {
    'Ath Paranaense': (-25.4483, -49.2769),     # Curitiba - PR
    'Atl Goianiense': (-16.6786, -49.2608),     # Goiânia - GO
    'Atlético Mineiro': (-19.9300, -44.0139),   # Belo Horizonte - MG
    'Bahia': (-12.9788, -38.5044),              # Salvador - BA
    'Botafogo (RJ)': (-22.8932, -43.2923),      # Rio de Janeiro - RJ
    'Corinthians': (-23.5453, -46.4742),        # São Paulo - SP
    'Criciúma': (-28.6844, -49.3676),           # Criciúma - SC
    'Cruzeiro': (-19.8658, -43.9711),           # Belo Horizonte - MG
    'Cuiabá': (-15.6031, -56.1206),             # Cuiabá - MT
    'Flamengo': (-22.9121, -43.2302),           # Rio de Janeiro - RJ
    'Fluminense': (-22.9121, -43.2302),         # Rio de Janeiro - RJ
    'Fortaleza': (-3.8073, -38.5225),           # Fortaleza - CE
    'Grêmio': (-29.9740, -51.1949),             # Porto Alegre - RS
    'Internacional': (-30.0655, -51.2361),      # Porto Alegre - RS
    'Juventude': (-29.1628, -51.1794),          # Caxias do Sul - RS
    'Palmeiras': (-23.5275, -46.6785),          # São Paulo - SP
    'RB Bragantino': (-22.9669, -46.5364),      # Bragança Paulista - SP
    'São Paulo': (-23.6001, -46.7201),          # São Paulo - SP
    'Vasco da Gama': (-22.8908, -43.2281),      # Rio de Janeiro - RJ
    'Vitória': (-12.9192, -38.4272),            # Salvador - BA
}

# 2. Coordenadas exatas dos 31 estádios que apareceram no dataset
COORDENADAS_ESTADIOS = {
    'Allianz Parque': (-23.5275, -46.6785),
    'Arena Barueri': (-23.5131, -46.8997),
    'Arena Condá': (-27.0994, -52.6067),
    'Arena MRV': (-19.9300, -44.0139),
    'Arena Pantanal': (-15.6031, -56.1206),
    'Arena do Grêmio': (-29.9740, -51.1949),
    'Estadio Jornalista Mário Filho': (-22.9121, -43.2302),         # Maracanã
    'Estádio Alfredo Jaconi': (-29.1628, -51.1794),
    'Estádio Antônio Accioly': (-16.6786, -49.2608),
    'Estádio Brinco de Ouro da Princesa': (-22.9097, -47.0436),
    'Estádio Castelão': (-3.8073, -38.5225),
    'Estádio Club de Regatas Vasco da Gama': (-22.8908, -43.2281),  # São Januário
    'Estádio Francisco Stédile': (-29.1667, -51.1969),              # Centenário (Caxias)
    'Estádio Governador Magalhães Pinto': (-19.8658, -43.9711),     # Mineirão
    'Estádio Heriberto Hülse': (-28.6844, -49.3676),
    'Estádio José Pinheiro Borba': (-30.0655, -51.2361),            # Beira-Rio
    'Estádio Kleber José de Andrade': (-20.3344, -40.3861),         # Cariacica - ES
    'Estádio Major Antônio Couto Pereira': (-25.4211, -49.2594),
    'Estádio Manoel Barradas': (-12.9192, -38.4272),                # Barradão
    'Estádio Municipal Nílton Santos': (-22.8932, -43.2923),
    'Estádio Nilton Santos': (-22.8932, -43.2923),
    'Estádio Municipal Presidente Getúlio Var...': (-22.7556, -43.4603), # Nova Iguaçu - RJ
    'Estádio Nabi Abi Chedid': (-22.9669, -46.5364),
    'Estádio Nacional de Brasília': (-15.7836, -47.8992),           # Mané Garrincha
    'Estádio Orlando Scarpelli': (-27.5856, -48.5867),
    'Estádio Raimundo Sampaio': (-19.9083, -43.9178),               # Independência
    'Estádio do Governo do Estado de Goiás': (-16.6989, -49.2336),  # Serra Dourada
    'Estádio do Morumbi': (-23.6001, -46.7201),
    'Itaipava Arena Fonte Nova': (-12.9788, -38.5044),
    'Ligga Arena': (-25.4483, -49.2769),
    'Neo Química Arena': (-23.5453, -46.4742),
}


def calcular_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em km entre dois pontos geográficos."""
    raio_terra = 6371.0
    lat1_r, lon1_r, lat2_r, lon2_r = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
    return round(raio_terra * 2 * np.arcsin(np.sqrt(a)), 2)


def executar_pipeline(caminho_csv_bruto: str, caminho_csv_saida: str) -> pd.DataFrame:
    colunas = ['data', 'horario', 'mandante', 'resultado', 'visitante', 'publico', 'estadio']
    df = pd.read_csv(caminho_csv_bruto, header=None, names=colunas)

    # 1. Limpeza de strings e tipos
    df['data'] = pd.to_datetime(df['data'])
    df['estadio'] = df['estadio'].str.strip()

    # Separar placar '1–1' (tenta travessão '–' e hífen comum '-' por segurança)
    placar = df['resultado'].str.replace('–', '-', regex=False).str.split('-', expand=True)
    df['gols_mandante'] = pd.to_numeric(placar[0].str.strip())
    df['gols_visitante'] = pd.to_numeric(placar[1].str.strip())

    # Limpar público ('12,804' -> 12804)
    df['publico'] = (
        df['publico'].astype(str).str.replace(',', '', regex=False).replace('nan', np.nan)
    )
    df['publico'] = pd.to_numeric(df['publico'], errors='coerce')

    # Criar ID único para cada partida
    df = df.sort_values(['data', 'horario']).reset_index(drop=True)
    df['id_partida'] = df.index + 1

    # 2. Desdobrar a tabela: 1 linha para o Mandante + 1 linha para o Visitante
    mandantes = pd.DataFrame({
        'id_partida': df['id_partida'],
        'data': df['data'],
        'clube': df['mandante'],
        'adversario': df['visitante'],
        'mando': 'Casa',
        'estadio': df['estadio'],
        'gols_pro': df['gols_mandante'],
        'gols_contra': df['gols_visitante'],
    })

    visitantes = pd.DataFrame({
        'id_partida': df['id_partida'],
        'data': df['data'],
        'clube': df['visitante'],
        'adversario': df['mandante'],
        'mando': 'Fora',
        'estadio': df['estadio'],
        'gols_pro': df['gols_visitante'],
        'gols_contra': df['gols_mandante'],
    })

    df_clubes = pd.concat([mandantes, visitantes], ignore_index=True)
    df_clubes = df_clubes.sort_values(['clube', 'data']).reset_index(drop=True)

    # 3. Calcular pontos conquistados e saldo de gols
    df_clubes['saldo_gols'] = df_clubes['gols_pro'] - df_clubes['gols_contra']
    df_clubes['pontos'] = np.select(
        [df_clubes['saldo_gols'] > 0, df_clubes['saldo_gols'] == 0],
        [3, 1],
        default=0
    )

    # 4. Adicionar coordenadas da sede e do estádio do jogo
    df_clubes['lat_sede'] = df_clubes['clube'].map(lambda c: SEDES_CLUBES[c][0])
    df_clubes['lon_sede'] = df_clubes['clube'].map(lambda c: SEDES_CLUBES[c][1])
    df_clubes['lat_estadio'] = df_clubes['estadio'].map(lambda e: COORDENADAS_ESTADIOS.get(e, (np.nan, np.nan))[0])
    df_clubes['lon_estadio'] = df_clubes['estadio'].map(lambda e: COORDENADAS_ESTADIOS.get(e, (np.nan, np.nan))[1])

    # 5. Calcular dias de descanso e km viajados entre partidas consecutivas
    df_clubes['data_anterior'] = df_clubes.groupby('clube')['data'].shift(1)
    df_clubes['lat_estadio_ant'] = df_clubes.groupby('clube')['lat_estadio'].shift(1)
    df_clubes['lon_estadio_ant'] = df_clubes.groupby('clube')['lon_estadio'].shift(1)
    df_clubes['dias_descanso'] = (df_clubes['data'] - df_clubes['data_anterior']).dt.days

    distancias = []
    for row in df_clubes.itertuples():
        if pd.isna(row.lat_estadio):
            dist = np.nan
        elif pd.isna(row.dias_descanso):
            dist = calcular_haversine(row.lat_sede, row.lon_sede, row.lat_estadio, row.lon_estadio)
        elif row.dias_descanso <= 3:
            dist = calcular_haversine(row.lat_estadio_ant, row.lon_estadio_ant, row.lat_estadio, row.lon_estadio)
        else:
            volta = calcular_haversine(row.lat_estadio_ant, row.lon_estadio_ant, row.lat_sede, row.lon_sede)
            ida = calcular_haversine(row.lat_sede, row.lon_sede, row.lat_estadio, row.lon_estadio)
            dist = volta + ida
        distancias.append(dist)

    df_clubes['km_viagem_partida'] = distancias

    # Salvar na camada Silver (data/processed)
    df_clubes.to_csv(caminho_csv_saida, index=False)
    print(f"Pipeline concluído! {len(df_clubes)} registros salvos em {caminho_csv_saida}")
    return df_clubes


if __name__ == "__main__":
    
    executar_pipeline(
        caminho_csv_bruto="data/raw/Brasileiro 2024 (Srie A) - Dataset - Final.csv",
        caminho_csv_saida="data/processed/partidas_clubes_silver.csv"
    )
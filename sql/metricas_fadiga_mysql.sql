USE Analise_Fadiga_Sports;

CREATE OR REPLACE VIEW vw_partidas_fadiga_gold AS
WITH base_calculos AS (
    SELECT 
        id_partida,
        STR_TO_DATE(data, '%Y-%m-%d') AS data_jogo,
        clube,
        adversario,
        mando,
        estadio,
        gols_pro,
        gols_contra,
        saldo_gols,
        pontos,
        COALESCE(dias_descanso, 7) AS dias_descanso,
        COALESCE(km_viagem_partida, 0) AS km_viagem_partida,

        -- 1. Quantos jogos o time fez nos últimos 7 e 14 dias (antes da partida atual)
        COUNT(id_partida) OVER (
            PARTITION BY clube 
            ORDER BY STR_TO_DATE(data, '%Y-%m-%d') 
            RANGE BETWEEN INTERVAL 7 DAY PRECEDING AND INTERVAL 1 DAY PRECEDING
        ) AS jogos_ultimos_7d,

        COUNT(id_partida) OVER (
            PARTITION BY clube 
            ORDER BY STR_TO_DATE(data, '%Y-%m-%d') 
            RANGE BETWEEN INTERVAL 14 DAY PRECEDING AND INTERVAL 1 DAY PRECEDING
        ) AS jogos_ultimos_14d,

        -- 2. Quilômetros viajados acumulados nos últimos 14 dias
        COALESCE(SUM(km_viagem_partida) OVER (
            PARTITION BY clube 
            ORDER BY STR_TO_DATE(data, '%Y-%m-%d') 
            RANGE BETWEEN INTERVAL 14 DAY PRECEDING AND INTERVAL 1 DAY PRECEDING
        ), 0) AS km_acumulado_14d,

        -- 3. Desempenho recente: média de pontos nos últimos 5 jogos
        AVG(pontos) OVER (
            PARTITION BY clube 
            ORDER BY STR_TO_DATE(data, '%Y-%m-%d') 
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS media_pontos_5_jogos,

        -- 4. Mando do jogo anterior
        LAG(mando, 1) OVER (
            PARTITION BY clube 
            ORDER BY STR_TO_DATE(data, '%Y-%m-%d')
        ) AS mando_jogo_anterior
    FROM partidas_clubes_silver -- <-- Confira se este é o nome exato em Tables!
)

SELECT 
    *,
    CASE 
        WHEN mando = 'Fora' AND mando_jogo_anterior = 'Fora' THEN 1 
        ELSE 0 
    END AS sequencia_fora_casa,

    CASE 
        WHEN jogos_ultimos_14d >= 3 AND km_acumulado_14d >= 2500 THEN 1 
        ELSE 0 
    END AS alerta_fadiga_alta,

    CASE 
        WHEN pontos = 0 THEN 1 
        ELSE 0 
    END AS flag_derrota
FROM base_calculos
ORDER BY clube, data_jogo;

-- Conferir o resultado
SELECT * FROM vw_partidas_fadiga_gold LIMIT 20;
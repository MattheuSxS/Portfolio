CREATE OR REPLACE PROCEDURE `mts-default-portofolio.ls_customers.sp_merge_and_delete_delivery_status`()
BEGIN
  -- Cria uma transação para garantir que as operações sejam atômicas.
  BEGIN TRANSACTION;

  -- 1. Cria uma tabela temporária para armazenar os dados do último intervalo.
  --    Esta tabela será visível para o MERGE e o DELETE.
  CREATE TEMP TABLE RecentData AS (
    SELECT
      *
    FROM
      `mts-default-portofolio.staging.tb_delivery_status_stage`
    WHERE
      -- Filtra os dados que chegaram nos últimos 30 minutos.
      updated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE)
  );

  -- 2. Executa o MERGE na tabela principal usando a tabela temporária como fonte.
  MERGE `mts-default-portofolio.ls_customers.tb_delivery_status` AS T
  USING RecentData AS S
  ON T.delivery_id = S.delivery_id
  WHEN MATCHED THEN
    UPDATE SET
      T.remaining_distance_km = COALESCE(S.remaining_distance_km, T.remaining_distance_km),
      T.estimated_time_min = COALESCE(S.estimated_time_min, T.estimated_time_min),
      T.delivery_difficulty = COALESCE(S.delivery_difficulty, T.delivery_difficulty),
      T.status = COALESCE(S.status, T.status),
      T.updated_at = COALESCE(S.updated_at, T.updated_at)
  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
        delivery_id,
        vehicle_id,
        purchase_id,
        remaining_distance_km,
        estimated_time_min,
        delivery_difficulty,
        status,
        created_at,
        updated_at
    )
    VALUES (
        S.delivery_id,
        S.vehicle_id,
        S.purchase_id,
        S.remaining_distance_km,
        S.estimated_time_min,
        S.delivery_difficulty,
        S.status,
        COALESCE(S.created_at, CURRENT_TIMESTAMP()),
        COALESCE(S.updated_at, CURRENT_TIMESTAMP())
    );

  -- 3. Exclui os dados da tabela de staging original, referenciando a tabela temporária.
  DELETE FROM `mts-default-portofolio.staging.tb_delivery_status_stage`
  WHERE delivery_id IN (SELECT delivery_id FROM RecentData);

  -- Confirma as alterações.
  COMMIT TRANSACTION;
END;
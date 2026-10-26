CREATE OR REPLACE PROCEDURE `gcp-mts-pf.ls_customers.sp_merge_and_delete_delivery_status`()
BEGIN
    -- Create a transaction to ensure that the operations are atomic.
    BEGIN TRANSACTION;

    -- 1. Create a temporary table to store the data from the last interval.
    --    This table will be visible to the MERGE and DELETE statements.
    CREATE TEMP TABLE RecentData AS (
        SELECT
        *
        FROM
        `gcp-mts-pf.staging.tb_delivery_status_stage`
        WHERE
        -- Filter the data that arrived in the last 60 minutes.
        updated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 MINUTE)
    );

    -- 2. Execute the MERGE statement to update existing records and insert new ones based on the RecentData temporary table.
    MERGE `gcp-mts-pf.ls_customers.tb_delivery_status` AS T
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

    -- 3. Delete the data from the original staging table, referencing the temporary table.
    DELETE FROM `gcp-mts-pf.staging.tb_delivery_status_stage`
    WHERE delivery_id IN (SELECT delivery_id FROM RecentData);

    -- Commit the changes.
    COMMIT TRANSACTION;
END;
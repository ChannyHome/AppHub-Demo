from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SQL_UPSERT_HUB_DAILY = text("""
INSERT INTO hub_daily_metrics (metric_date, dau, page_open_count, search_count, created_at)
SELECT
  :d AS metric_date,
  COUNT(DISTINCT user_id) AS dau,
  SUM(event_type = 'page_open') AS page_open_count,
  SUM(event_type = 'search') AS search_count,
  NOW() AS created_at
FROM hub_events
WHERE occurred_at >= :d
  AND occurred_at <  DATE_ADD(:d, INTERVAL 1 DAY)
ON DUPLICATE KEY UPDATE
  dau = VALUES(dau),
  page_open_count = VALUES(page_open_count),
  search_count = VALUES(search_count),
  created_at = VALUES(created_at);
""")

SQL_UPSERT_APP_DAILY_BASE = text("""
INSERT INTO app_daily_metrics (metric_date, app_id, unique_users, launch_count, total_runtime_sec, action_count, created_at)
SELECT
  :d AS metric_date,
  rs.app_id,
  COUNT(DISTINCT rs.user_id) AS unique_users,
  COUNT(*) AS launch_count,
  SUM(
    CASE
      WHEN rs.ended_at IS NULL THEN 0
      ELSE TIMESTAMPDIFF(SECOND, rs.started_at, rs.ended_at)
    END
  ) AS total_runtime_sec,
  0 AS action_count,
  NOW() AS created_at
FROM app_run_sessions rs
WHERE rs.started_at >= :d
  AND rs.started_at <  DATE_ADD(:d, INTERVAL 1 DAY)
GROUP BY rs.app_id
ON DUPLICATE KEY UPDATE
  unique_users = VALUES(unique_users),
  launch_count = VALUES(launch_count),
  total_runtime_sec = VALUES(total_runtime_sec),
  created_at = VALUES(created_at);
""")

SQL_UPDATE_APP_DAILY_ACTIONS = text("""
UPDATE app_daily_metrics adm
JOIN (
  SELECT
    rs.app_id,
    COUNT(*) AS action_count
  FROM app_action_events ae
  JOIN app_run_sessions rs ON rs.id = ae.session_id
  WHERE ae.occurred_at >= :d
    AND ae.occurred_at <  DATE_ADD(:d, INTERVAL 1 DAY)
  GROUP BY rs.app_id
) x ON x.app_id = adm.app_id
SET adm.action_count = x.action_count,
    adm.created_at = NOW()
WHERE adm.metric_date = :d;
""")

async def run_daily_batch(db: AsyncSession, metric_date: str) -> None:
    # metric_date: 'YYYY-MM-DD'
    await db.execute(SQL_UPSERT_HUB_DAILY, {"d": metric_date})
    await db.execute(SQL_UPSERT_APP_DAILY_BASE, {"d": metric_date})
    await db.execute(SQL_UPDATE_APP_DAILY_ACTIONS, {"d": metric_date})
    await db.commit()

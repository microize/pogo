-- Post-load data quality checks: <layer> of track <track_id> (spec section 7).
-- Run on a SQL warehouse after a pipeline update. One pass/fail row per rule, no row values.
-- A job task fails when any Critical row is false, for example:
--   SELECT assert_true(bool_and(pass)) FROM (<this query>) WHERE severity = 'Critical'
-- FRS-01 needs a column `_source_file_mtime` written at ingest in bronze as `_metadata.file_modification_time`
-- (file sources only; `_metadata` cannot be read after the write) and carried through to silver.
-- Idempotency (CON-01): run the pipeline update twice with no new source data; this query and
--   SELECT count(*), sum(CAST(xxhash64(*) AS DECIMAL(38,0))) FROM <table>   -- per target
-- must return the same values both times.
DECLARE OR REPLACE VARIABLE catalog_name STRING DEFAULT '<dev catalog>';

SELECT 'UNQ-01' AS rule_id, 'Critical' AS severity, '<table> one row per <grain>' AS rule,
  (SELECT count(*) = count(DISTINCT <grain_cols>) FROM IDENTIFIER(catalog_name || '.<schema>.<table>')) AS pass
UNION ALL SELECT 'UNQ-02', 'Critical', '<scd2 table> one current row per key',
  (SELECT count(*) = 0 FROM (SELECT <key_cols> FROM IDENTIFIER(catalog_name || '.<schema>.<scd2_table>')
     WHERE __END_AT IS NULL GROUP BY ALL HAVING count(*) > 1))
UNION ALL SELECT 'REF-01', 'Critical', 'every fact key exists in the dimension',
  (SELECT count(*) = 0 FROM IDENTIFIER(catalog_name || '.<schema>.<fact>') f
     LEFT ANTI JOIN IDENTIFIER(catalog_name || '.<schema>.<dim>') d ON f.<fk> = d.<sk>)
UNION ALL SELECT 'CMP-01', 'Critical', '<columns> never null',
  (SELECT count_if(<col_a> IS NULL OR <col_b> IS NULL) = 0 FROM IDENTIFIER(catalog_name || '.<schema>.<table>'))
UNION ALL SELECT 'THR-01', 'Critical', 'bronze rows = silver valid + quarantined',
  (SELECT (SELECT count(*) FROM IDENTIFIER(catalog_name || '.<bronze>')) =
          (SELECT count(*) FROM IDENTIFIER(catalog_name || '.<silver_valid_source>')) +
          (SELECT count(*) FROM IDENTIFIER(catalog_name || '.<quarantine>')))
UNION ALL SELECT 'FRS-01', 'Critical', 'nothing left unprocessed (newest source file = newest loaded file)',
  (SELECT (SELECT max(_source_file_mtime) FROM IDENTIFIER(catalog_name || '.<bronze>')) =
          (SELECT max(_source_file_mtime) FROM IDENTIFIER(catalog_name || '.<silver>')))
UNION ALL SELECT 'RNG-01', 'Warning', '<measure> within expected range',
  (SELECT count_if(<measure> < 0 OR <measure> > <max>) = 0 FROM IDENTIFIER(catalog_name || '.<schema>.<table>'));

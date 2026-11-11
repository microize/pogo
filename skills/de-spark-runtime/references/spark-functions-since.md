# Spark SQL built-in functions by first version ("Since")

Generated 2026-11-12 from the `Since:` field of the Spark SQL built-in function pages
(spark.apache.org/docs/latest/api/sql/). Operators and symbols are left out. Caveats: the field shows the version of
the **latest overload** for a few functions (for example `max_by` / `min_by` show 4.2 for the k-argument form; the base
function is older); the PySpark wrapper can arrive later than the SQL function (call it through `F.expr("fn(...)")`
on an older runtime); Databricks can ship a function earlier than the Apache version that carries it (minimum DBR
in `runtime-versions.md`, section 4, wins). Map Spark versions to runtimes with `runtime-versions.md`, section 1.

**1.0** (25): `and`, `avg`, `between`, `case`, `cast`, `coalesce`, `count`, `if`, `in`, `isnotnull`, `isnull`, `lcase`, `like`, `lower`, `max`, `mean`, `min`, `negative`, `not`, `or`, `rlike`, `sum`, `ucase`, `upper`, `when`

**1.1** (2): `array`, `sqrt`

**1.2** (1): `abs`

**1.4** (27): `acos`, `asin`, `atan`, `atan2`, `cbrt`, `cos`, `cosh`, `degrees`, `exp`, `expm1`, `hypot`, `ln`, `log10`, `log1p`, `log2`, `monotonically_increasing_id`, `pow`, `power`, `radians`, `rint`, `sign`, `signum`, `sin`, `sinh`, `spark_partition_id`, `tan`, `tanh`

**1.5** (80): `add_months`, `array_contains`, `ascii`, `base64`, `bin`, `concat`, `concat_ws`, `conv`, `current_date`, `current_timestamp`, `date_add`, `date_format`, `date_sub`, `datediff`, `day`, `dayofmonth`, `dayofyear`, `decode`, `e`, `encode`, `factorial`, `find_in_set`, `format_number`, `format_string`, `from_unixtime`, `from_utc_timestamp`, `get_json_object`, `greatest`, `hex`, `hour`, `initcap`, `input_file_name`, `instr`, `isnan`, `last_day`, `least`, `length`, `levenshtein`, `locate`, `log`, `lpad`, `ltrim`, `minute`, `month`, `months_between`, `nanvl`, `next_day`, `pi`, `pmod`, `positive`, `printf`, `quarter`, `rand`, `randn`, `regexp_extract`, `regexp_replace`, `repeat`, `reverse`, `round`, `rpad`, `rtrim`, `second`, `size`, `sort_array`, `soundex`, `space`, `split`, `substr`, `substring`, `substring_index`, `to_date`, `to_utc_timestamp`, `translate`, `trim`, `trunc`, `unbase64`, `unhex`, `unix_timestamp`, `weekofyear`, `year`

**1.6** (15): `approx_count_distinct`, `corr`, `current_database`, `json_tuple`, `kurtosis`, `now`, `skewness`, `std`, `stddev`, `stddev_pop`, `stddev_samp`, `to_unix_timestamp`, `var_pop`, `var_samp`, `variance`

**2.0** (48): `assert_true`, `bigint`, `binary`, `boolean`, `bround`, `collect_list`, `collect_set`, `covar_pop`, `covar_samp`, `cume_dist`, `date`, `decimal`, `dense_rank`, `double`, `elt`, `first`, `first_value`, `float`, `grouping`, `grouping_id`, `ifnull`, `int`, `java_method`, `lag`, `last`, `last_value`, `lead`, `map`, `map_keys`, `map_values`, `ntile`, `nullif`, `nvl`, `nvl2`, `parse_url`, `percent_rank`, `range`, `rank`, `reflect`, `row_number`, `sentences`, `smallint`, `str_to_map`, `string`, `time`, `timestamp`, `tinyint`, `window`

**2.1** (3): `approx_percentile`, `percentile`, `percentile_approx`

**2.2** (6): `count_min_sketch`, `from_json`, `input_file_block_length`, `input_file_block_start`, `to_json`, `to_timestamp`

**2.3** (15): `bit_length`, `char`, `char_length`, `character_length`, `chr`, `cot`, `date_trunc`, `dayofweek`, `left`, `mod`, `octet_length`, `position`, `replace`, `right`, `uuid`

**2.4** (29): `aggregate`, `array_distinct`, `array_except`, `array_intersect`, `array_join`, `array_max`, `array_min`, `array_position`, `array_remove`, `array_repeat`, `array_sort`, `array_union`, `arrays_overlap`, `arrays_zip`, `cardinality`, `element_at`, `exists`, `filter`, `flatten`, `map_concat`, `map_from_arrays`, `map_from_entries`, `schema_of_json`, `sequence`, `shuffle`, `slice`, `transform`, `weekday`, `zip_with`

**3.0** (28): `acosh`, `any`, `asinh`, `atanh`, `bit_and`, `bit_or`, `bit_xor`, `bool_and`, `bool_or`, `count_if`, `date_part`, `div`, `every`, `extract`, `forall`, `make_date`, `make_interval`, `make_timestamp`, `map_entries`, `map_filter`, `map_zip_with`, `overlay`, `random`, `some`, `transform_keys`, `transform_values`, `typeof`, `version`

**3.1** (16): `current_catalog`, `current_timezone`, `date_from_unix_date`, `json_array_length`, `json_object_keys`, `nth_value`, `raise_error`, `regexp_extract_all`, `timestamp_micros`, `timestamp_millis`, `timestamp_seconds`, `unix_date`, `unix_micros`, `unix_millis`, `unix_seconds`, `width_bucket`

**3.2** (9): `btrim`, `current_user`, `make_dt_interval`, `make_ym_interval`, `regexp`, `regexp_like`, `session_window`, `try_add`, `try_divide`

**3.3** (29): `aes_decrypt`, `aes_encrypt`, `array_agg`, `array_size`, `ceil`, `ceiling`, `contains`, `csc`, `endswith`, `floor`, `histogram_numeric`, `ilike`, `map_contains_key`, `regr_avgx`, `regr_avgy`, `regr_count`, `regr_r2`, `sec`, `split_part`, `startswith`, `to_binary`, `to_number`, `try_avg`, `try_element_at`, `try_multiply`, `try_subtract`, `try_sum`, `try_to_binary`, `try_to_number`

**3.4** (36): `any_value`, `array_append`, `array_compact`, `array_insert`, `convert_timezone`, `curdate`, `current_schema`, `date_diff`, `dateadd`, `datepart`, `equal_null`, `get`, `len`, `localtimestamp`, `make_timestamp_ltz`, `make_timestamp_ntz`, `mask`, `median`, `mode`, `reduce`, `regexp_count`, `regexp_instr`, `regexp_substr`, `regr_intercept`, `regr_slope`, `regr_sxx`, `regr_sxy`, `regr_syy`, `to_char`, `to_timestamp_ltz`, `to_timestamp_ntz`, `try_to_timestamp`, `url_decode`, `url_encode`, `user`, `window_time`

**3.5** (13): `array_prepend`, `bitmap_bit_position`, `bitmap_bucket_number`, `bitmap_construct_agg`, `bitmap_count`, `bitmap_or_agg`, `hll_sketch_agg`, `hll_sketch_estimate`, `hll_union`, `hll_union_agg`, `luhn_check`, `to_varchar`, `try_aes_decrypt`

**4.0** (36): `collate`, `collation`, `dayname`, `is_valid_utf8`, `is_variant_null`, `listagg`, `make_valid_utf8`, `monthname`, `nullifzero`, `parse_json`, `percentile_cont`, `percentile_disc`, `randstr`, `schema_of_variant`, `schema_of_variant_agg`, `session_user`, `string_agg`, `to_variant_object`, `try_make_interval`, `try_make_timestamp`, `try_make_timestamp_ltz`, `try_make_timestamp_ntz`, `try_mod`, `try_parse_json`, `try_parse_url`, `try_reflect`, `try_to_date`, `try_url_decode`, `try_validate_utf8`, `try_variant_get`, `uniform`, `validate_utf8`, `variant_explode`, `variant_explode_outer`, `variant_get`, `zeroifnull`

**4.1** (46): `approx_top_k`, `approx_top_k_accumulate`, `approx_top_k_combine`, `approx_top_k_estimate`, `bitmap_and_agg`, `current_time`, `kll_merge_agg_bigint`, `kll_merge_agg_double`, `kll_merge_agg_float`, `kll_sketch_agg_bigint`, `kll_sketch_agg_double`, `kll_sketch_agg_float`, `kll_sketch_get_n_bigint`, `kll_sketch_get_n_double`, `kll_sketch_get_n_float`, `kll_sketch_get_quantile_bigint`, `kll_sketch_get_quantile_double`, `kll_sketch_get_quantile_float`, `kll_sketch_get_rank_bigint`, `kll_sketch_get_rank_double`, `kll_sketch_get_rank_float`, `kll_sketch_merge_bigint`, `kll_sketch_merge_double`, `kll_sketch_merge_float`, `kll_sketch_to_string_bigint`, `kll_sketch_to_string_double`, `kll_sketch_to_string_float`, `make_time`, `python_worker_logs`, `quote`, `st_asbinary`, `st_geogfromwkb`, `st_geomfromwkb`, `st_setsrid`, `st_srid`, `theta_difference`, `theta_intersection`, `theta_intersection_agg`, `theta_sketch_agg`, `theta_sketch_estimate`, `theta_union`, `theta_union_agg`, `time_diff`, `time_trunc`, `to_time`, `try_to_time`

**4.2** (43): `current_path`, `is_valid_variant`, `max_by`, `measure`, `min_by`, `time_bucket`, `time_from_micros`, `time_from_millis`, `time_from_seconds`, `time_to_micros`, `time_to_millis`, `time_to_seconds`, `tuple_difference_double`, `tuple_difference_integer`, `tuple_difference_theta_double`, `tuple_difference_theta_integer`, `tuple_intersection_agg_double`, `tuple_intersection_agg_integer`, `tuple_intersection_double`, `tuple_intersection_integer`, `tuple_intersection_theta_double`, `tuple_intersection_theta_integer`, `tuple_sketch_agg_double`, `tuple_sketch_agg_integer`, `tuple_sketch_estimate_double`, `tuple_sketch_estimate_integer`, `tuple_sketch_summary_double`, `tuple_sketch_summary_integer`, `tuple_sketch_theta_double`, `tuple_sketch_theta_integer`, `tuple_union_agg_double`, `tuple_union_agg_integer`, `tuple_union_double`, `tuple_union_integer`, `tuple_union_theta_double`, `tuple_union_theta_integer`, `vector_avg`, `vector_cosine_similarity`, `vector_inner_product`, `vector_l2_distance`, `vector_norm`, `vector_normalize`, `vector_sum`

**4.3** (17): `collect_union`, `counter_diff`, `from_base32`, `hmac`, `jaro_winkler_similarity`, `localtime`, `timestamp_nanos`, `to_base32`, `try_variant_array_append`, `try_variant_insert`, `try_variant_set`, `unix_nanos`, `variant_array_append`, `variant_delete`, `variant_insert`, `variant_set`, `variant_strip_nulls`

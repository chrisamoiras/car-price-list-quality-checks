-- Variants approved for MY2027 but missing from the export, and export rows that are not in the approved list
SELECT 'MISSING_IN_EXPORT' AS issue, a.variant_code AS code
FROM approved_price_list a
LEFT JOIN configurator_export e ON e.code = a.variant_code AND e.item_type = 'VARIANT'
WHERE e.code IS NULL
UNION ALL
SELECT 'NOT_IN_APPROVED_LIST' AS issue, e.code
FROM configurator_export e
LEFT JOIN approved_price_list a ON a.variant_code = e.code
WHERE e.item_type = 'VARIANT' AND a.variant_code IS NULL
UNION ALL
SELECT 'DUPLICATE_CODE' AS issue, code
FROM configurator_export
GROUP BY item_type, code
HAVING COUNT(*) > 1;

-- Package price vs the sum of its options bought separately (a package should be cheaper)
WITH RECURSIVE split(package_code, item, rest) AS (
    SELECT package_code, '', contents || ';' FROM packages
    UNION ALL
    SELECT package_code,
           substr(rest, 1, instr(rest, ';') - 1),
           substr(rest, instr(rest, ';') + 1)
    FROM split WHERE rest <> ''
)
SELECT p.package_code,
       p.package_name,
       e.net_price                         AS package_net_in_export,
       SUM(o.net_price)                    AS options_net_total,
       SUM(o.net_price) - e.net_price      AS customer_saving
FROM split s
JOIN packages p             ON p.package_code = s.package_code
JOIN approved_options o     ON o.option_code  = s.item
JOIN configurator_export e  ON e.code = p.package_code AND e.item_type = 'PACKAGE'
WHERE s.item <> ''
GROUP BY p.package_code, p.package_name, e.net_price
ORDER BY customer_saving;

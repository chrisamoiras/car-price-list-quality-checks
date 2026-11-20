-- Variants whose price in the configurator export differs from the approved MY2027 price list
SELECT e.code,
       e.net_price            AS export_net,
       a.net_price_my2027     AS approved_net,
       e.net_price - a.net_price_my2027 AS diff_net,
       e.retail_price         AS export_retail,
       a.retail_price_my2027  AS approved_retail
FROM configurator_export e
JOIN approved_price_list a ON a.variant_code = e.code
WHERE e.item_type = 'VARIANT'
  AND (e.net_price <> a.net_price_my2027 OR e.retail_price <> a.retail_price_my2027)
ORDER BY e.code;

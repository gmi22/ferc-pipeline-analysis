
GET_OPERATING_REVENUE = """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("Total Current Year to Date Balance for Quarter/Year") AS operating_revenue
FROM IS_data
WHERE "Title of Account (Class)" = ?
  AND Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_Miles = """
SELECT
    Asset,
    Year,
    Qtr,
    SUM(Value) AS miles
FROM TotalMiles_data
WHERE  Year = ?
AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_OPEX= """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("Total Current Year to Date Balance for Quarter/Year") AS operating_revenue
FROM IS_data
WHERE "Title of Account (Class)" = ?
  AND Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_Depreciation= """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("Total Current Year to Date Balance for Quarter/Year") AS operating_revenue
FROM IS_data
WHERE "Title of Account (Class)" = ?
  AND Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_Volume= """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("Dekatherm of Natural Gas Amount for Current Year") AS Volume
FROM Rev_data
WHERE "Title of Account" = ?
  AND Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_Negotiated_Revenue= """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("RevenuesFromNegotiatedRateServices") AS Negotiated_Revenue
FROM NegDisc_data
  WHERE Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""



GET_NetPlant = """
SELECT
    Asset,
    Year,
    Qtr,
    SUM("Current Year End of Quarter/Year Balance") AS Net_Plant
FROM BS_data
WHERE "Title of Account sub-value" = ?
  AND Year = ?
  AND Qtr = "Q4"
GROUP BY Asset, Year, Qtr
"""


GET_KPIs = """
SELECT
    Asset,
    Year,
    Qtr,
    Metric,
    Value
FROM KPIs
WHERE Year = ?
  AND Qtr = "Q4"
"""



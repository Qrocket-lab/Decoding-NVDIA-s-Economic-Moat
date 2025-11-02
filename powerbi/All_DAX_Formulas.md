# Key DAX Formulas - NVIDIA Moat Analysis

## Calendar Table

```dax
Calendar = 
CALENDAR(
    MIN('nvda_stock_data'[Report Date]), 
    MAX('price_forecast'[Report Date])
)
```

**Purpose**: Creates a comprehensive date table spanning from the earliest stock data to the latest forecast date, enabling time intelligence calculations across all data sources.

---

## NOPAT (Net Operating Profit After Tax)

```dax
NOPAT = 
VAR OperatingIncome = SUM('nvidia_financial_data'[operatingIncome])
VAR PretaxIncome = SUM('nvidia_financial_data'[incomeBeforeTax])
VAR TaxExpense = SUM('nvidia_financial_data'[incomeTaxExpense])

VAR EffectiveTaxRate = DIVIDE(TaxExpense, PretaxIncome, 0.21)

RETURN
OperatingIncome * (1 - EffectiveTaxRate)
```

**Purpose**: Calculates the core operating profitability of NVIDIA by adjusting operating income for taxes. Uses actual effective tax rate when available, defaults to 21% corporate tax rate otherwise.

**Components**:
- `OperatingIncome`: Core business earnings before interest and taxes
- `EffectiveTaxRate`: Actual tax burden based on historical data
- **Output**: True operating profit available to all capital providers

---

## ROIC (%) - Return on Invested Capital

```dax
ROIC (%) = 
DIVIDE([NOPAT], [Invested Capital])
```

**Purpose**: Measures how efficiently NVIDIA generates returns from its invested capital. This is the **primary moat metric** indicating competitive advantage.

**Interpretation**:
- **>15%**: Strong competitive advantage
- **10-15%**: Good performance
- **<10%**: Weak competitive position

**Formula Logic**: 
```
ROIC = Net Operating Profit After Tax / Invested Capital
```

---

## Gross Margin %

```dax
Gross Margin % = 
DIVIDE(
    SUM('nvidia_financial_data'[grossProfit]), 
    SUM('nvidia_financial_data'[totalRevenue])
)
```

**Purpose**: Measures core profitability after direct production costs. High and stable gross margins indicate pricing power and cost advantages.

**Interpretation**:
- **High & Stable**: Strong brand/pricing power, efficient operations
- **Declining**: Price pressure, rising costs, competitive threats
- **Volatile**: Unstable business model

**Formula Logic**:
```
Gross Margin = (Revenue - Cost of Goods Sold) / Revenue
```

---

## R&D as % of Revenue

```dax
R&D as % of Revenue = 
DIVIDE(
    SUM('nvidia_financial_data'[researchAndDevelopment]), 
    SUM('nvidia_financial_data'[totalRevenue])
)
```

**Purpose**: Measures NVIDIA's investment in innovation and future growth relative to its current scale.

**Interpretation**:
- **High %**: Heavy investment in future technologies (typical for tech)
- **Increasing**: Accelerating innovation efforts
- **Declining**: May indicate maturity or efficiency improvements

**Strategic Importance**: For technology companies, sustained R&D investment is crucial for maintaining competitive advantages.

---

## Supporting Measures

### Invested Capital Calculation
*(Implied in ROIC formula)*
```dax
Invested Capital = 
SUM('nvidia_financial_data'[totalDebt]) + 
SUM('nvidia_financial_data'[totalShareholderEquity]) -
SUM('nvidia_financial_data'[cashAndCashEquivalentsAtCarryingValue])
```

**Purpose**: Represents total capital invested in the business (debt + equity - excess cash)

---

## Key Performance Indicators Derived

| Metric | Formula | Moat Significance |
|--------|---------|-------------------|
| **ROIC** | NOPAT / Invested Capital | Primary efficiency and competitive advantage indicator |
| **Gross Margin** | Gross Profit / Revenue | Pricing power and cost structure health |
| **R&D Intensity** | R&D / Revenue | Innovation commitment and future growth potential |
| **NOPAT** | Operating Income × (1 - Tax Rate) | Core operating profitability |

---

## Relationships in Power BI Data Model

These DAX formulas work across the following tables:
- `nvidia_financial_data` - Quarterly financial statements
- `nvda_stock_data` - Daily stock performance  
- `price_forecast` - ML-predicted future prices
- `Calendar` - Unified date dimension

All time-based calculations use the `Calendar` table for consistent period-over-period comparisons and trend analysis.

---

## Strategic Insights from These Formulas

1. **ROIC Trend** → Sustainable competitive advantage
2. **Gross Margin Stability** → Pricing power and cost control
3. **R&D Consistency** → Long-term innovation pipeline
4. **NOPAT Growth** → Core business expansion

These four key metrics provide a comprehensive view of NVIDIA's economic moat and financial health.
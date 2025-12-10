## 1. Aggregation & Grouping

**Question:**  
What is the total sales and average benefit per order by order_region?

**Expected Behavior:**  
- Generates groupby on `order_region`
- Computes `sum(Sales)` and `mean(Benefit per order)`
- Returns table with one row per region
- Narrative highlights top/bottom regions and key patterns

---

## 2. Delivery Performance

**Question:**  
What is the on_time_delivery rate by order_region?

**Expected Behavior:**  
- Correctly interprets `Late_delivery_risk` and `Delivery Status`
- Calculates % of on-time deliveries per region
- Narrative explains which regions underperform and possible reasons

---

## 3. Customer Segment Profitability

**Question:**  
Compare average profit and total sales by customer_segment.

**Expected Behavior:**  
- Groups by `Customer Segment`
- Calculates metrics: avg profit, total sales
- Narrative mentions which segments are most and least profitable

---

## 4. Risk vs Profit Trade-off

**Question:**  
For each order_region, how does late_delivery_risk relate to order profit per order?

**Expected Behavior:**  
- Joins/aggregates late_delivery_risk with `Order Profit Per Order`
- Shows relationship (e.g. scatter or grouped summary)
- Narrative discusses trade-offs between risk and profit

---

## 5. Product-Level Analysis

**Question:**  
Which product category has the highest total sales and which has the highest average profit per order?

**Expected Behavior:**  
- Groups by `Product Category Id` or `Category Name`
- Computes total sales and average profit
- Narrative distinguishes volume vs profitability leaders

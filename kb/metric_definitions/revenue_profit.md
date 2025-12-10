# Revenue and Profit Metrics

**Revenue (Sales)**  
At the line level:
- `sales`: revenue attributed to this order line.
- `order_item_total`: total line revenue after discounts.

**Profit**  
- `benefit_per_order`: profit contribution per order line.
- `order_profit_per_order`: total profit for the order (repeated on each line of the same order).

**Common metrics:**

1. **Total Revenue**
   `total_revenue = sum(sales)`

2. **Total Profit**
   `total_profit = sum(benefit_per_order)` or `sum(order_profit_per_order)`, depending on level.

3. **Average Order Value (AOV)**
   `AOV = total_revenue / number_of_unique_orders`

4. **Profit Margin**
   `profit_margin = total_profit / total_revenue`

These metrics can be broken down by:
- `order_region`
- `order_country`
- `customer_segment`
- `category_name`
- `shipping_mode`

# Supply Chain Orders Schema (DataCo)

Main analytical table: **orders** (one row per order line / item).

Key fields:

- `order_id`: unique identifier of the order (multiple line items share this).
- `order_item_id`: unique identifier of the order line item.
- `order_date`: date when the order was placed.
- `shipping_date`: date when the order was shipped.
- `order_region`: geographic region of the order (e.g., Southeast Asia, Oceania).
- `order_country`: country where the order was placed.
- `order_city`: city where the order was placed.
- `order_state`: state / province / region.

Customer fields:
- `order_customer_id`: internal customer identifier used in orders.
- `customer_id`: customer identifier in the customer master table.
- `customer_fname`, `customer_lname`: customer name.
- `customer_segment`: e.g., Consumer, Corporate, Home Office.
- `customer_country`, `customer_state`, `customer_city`, `customer_zipcode`: customer location.
- `payment_type`: payment method used (e.g., DEBIT, TRANSFER, CASH).

Product fields:
- `product_card_id`, `product_category_id`: product identifiers.
- `category_name`: high-level product category (e.g., Sporting Goods).
- `department_name`: department (e.g., Fitness).
- `product_name`: product name (e.g., Smart watch).
- `product_price`: list price of the product.
- `product_status`: status code for the product (e.g., active/inactive).

Order line metrics:
- `order_item_quantity`: quantity ordered in this line.
- `order_item_product_price`: price per unit at the time of order.
- `order_item_discount`: discount amount applied to this line.
- `order_item_discount_rate`: discount as a fraction of product price.
- `order_item_total`: total revenue for the line (after discount).
- `sales`: sales attribution at the line level (often same as order_item_total).
- `benefit_per_order`: profit contribution attributed to the order line.
- `order_profit_per_order`: total profit for the order (repeated per line).
- `order_item_profit_ratio`: profit ratio for the line (profit / sales).

Logistics fields:
- `delivery_status`: textual status (e.g., Shipping on time, Late delivery, Advance shipping).
- `late_delivery_risk`: indicator (0/1) whether this order is at risk of late delivery.
- `days_for_shipment_scheduled`: promised shipping duration in days.
- `days_for_shipping_real`: actual shipping duration in days.
- `shipping_delay_days`: derived: real - scheduled.
- `on_time_delivery`: boolean; True if `shipping_delay_days <= 0`.

Other:
- `market`: market zone (e.g., Pacific Asia, South Asia).
- `shipping_mode`: shipping service level (e.g., Standard Class).
- `latitude`, `longitude`: geographic coordinates.

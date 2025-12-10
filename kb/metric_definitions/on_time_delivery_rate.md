# On-Time Delivery Rate

**Definition**  
The percentage of order lines delivered on or before the promised shipping duration.

**Formula**  
On a dataset with `on_time_delivery` as a boolean flag:

`on_time_delivery_rate = (number of rows where on_time_delivery == True) / (total number of rows)`

This metric can be computed overall, or broken down by:
- `order_region`
- `order_country`
- `customer_segment`
- `shipping_mode`
- `category_name`

**Interpretation**  
Higher values indicate better logistics performance and customer experience.

**Usage**  
Used to compare performance across regions, shipping modes, and product categories, and to detect operational bottlenecks.

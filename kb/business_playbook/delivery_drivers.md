# Typical Drivers of Delivery Performance

Common factors influencing delivery performance:

- **Region and Country**
  Some regions (e.g., remote or less connected) tend to have longer shipping times and higher risk of late delivery.

- **Shipping Mode**
  Faster shipping modes usually have lower shipping_delay_days but higher cost.
  Standard or economy service can show higher delay and variability.

- **Product Category**
  Bulky, fragile, or regulated items may require longer handling time and special carriers.

- **Order Volume and Seasonality**
  High demand periods (e.g., holidays) can increase delays if logistics capacity is constrained.

- **Operational Constraints**
  Warehouse location, carrier reliability, and cut-off times directly affect on-time delivery.

When analyzing delivery performance, it's helpful to:
- Compare `on_time_delivery_rate` by `order_region`, `order_country`, and `shipping_mode`.
- Look at the distribution of `shipping_delay_days` for the worst-performing segments.

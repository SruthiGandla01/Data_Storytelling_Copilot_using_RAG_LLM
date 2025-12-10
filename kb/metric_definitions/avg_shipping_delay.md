# Average Shipping Delay

**Definition**  
The average number of days difference between real and scheduled shipping durations.

**Fields**  
- `days_for_shipment_scheduled`
- `days_for_shipping_real`
- `shipping_delay_days = days_for_shipping_real - days_for_shipment_scheduled`

**Formula**  

`avg_shipping_delay = mean(shipping_delay_days)`

Segmented versions:
- `avg_shipping_delay_by_region = mean(shipping_delay_days) grouped by order_region`
- `avg_shipping_delay_by_shipping_mode = mean(shipping_delay_days) grouped by shipping_mode`

**Interpretation**  
- Values > 0: shipments are, on average, delayed.
- Values < 0: shipments are, on average, earlier than promised.

**Usage**  
Identify lanes, regions, or shipping modes with consistently late deliveries and prioritize operational improvements.

# Fulfillment & Delivery Risk Factors

Fulfillment risk represents the likelihood that an order will be delayed, mis-handled, or delivered outside expected SLA.  
In the DataCo dataset, risk can be approximated using fields like:

- `late_delivery_risk` (0/1 indicator)  
- `shipping_delay_days`  
- `delivery_status`  
- `shipping_mode`  
- `order_region`  

---

# 1. Core Drivers of Delivery Risk

## A. Logistics & Operational Delays
**Caused by:**
- Insufficient carrier capacity  
- Warehouse processing delays  
- High seasonal order volume  
- Routing inefficiencies  

**Indicators in data:**  
- High positive values in `shipping_delay_days`  
- Frequent “Late delivery” statuses  

---

## B. Geographic and Regional Factors
Some regions inherently show:
- Longer transit times  
- Lower carrier density  
- Customs and border delays (international markets)

**Key columns:**
- `order_region`  
- `order_country`  
- `market`  

High-risk regions often correlate with:
- Low on_time_delivery rate  
- Higher variance in shipping_delay_days  

---

## C. Shipping Mode
Different modes imply different reliability levels.

- **Standard Class:** economical but higher delay risk  
- **First Class / Two-Day:** lower average delay  
- **Same Day / Express:** highest reliability but costly  

**Data field:** `shipping_mode`

---

## D. Product-Related Risks
Some products influence fulfillment performance:
- Bulky items → handling delays  
- Fragile goods → special carrier routing  
- High-value items → security screening  

Fields:  
- `product_category_id`  
- `category_name`  
- `department_name`

---

# 2. Analytical Evaluation of Risk

Common breakdowns:
- **On-time delivery rate by region**
- **Average shipping delay by shipping mode**
- **Late_delivery_risk by customer segment**
- **Benefit_per_order impact due to delay**

Useful formulas:
- `on_time_delivery = shipping_delay_days <= 0`
- `late_delivery_rate = mean(late_delivery_risk)`
- `avg_delay = mean(shipping_delay_days)`

---

# 3. Business Consequences of High Risk

- Lower customer satisfaction (especially Consumer segment)  
- Higher refunds / returns  
- Increased logistics cost  
- Contract penalties for B2B customers  
- Reduced repeat purchase likelihood  

---

# 4. Recommendations for Mitigation

## Operational Actions
- Improve warehouse processing efficiency  
- Allocate more reliable carriers for high-risk regions  
- Increase safety stock in regional hubs  
- Use predictive models to anticipate delay spikes  

## Customer Experience Actions
- Provide proactive delay notifications  
- Offer alternative delivery modes at checkout  
- Introduce regional delivery SLA differentiation  
- Prioritize high-value customers (Corporate & Home Office)  

---

# Importance for InsightWeaver
Understanding fulfill

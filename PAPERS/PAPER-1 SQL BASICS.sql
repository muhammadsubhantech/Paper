-- 1.  List every order with the customer's full name, store name, and the full name of the staff member who handled it.
SELECT 
    o.order_id,
    o.order_date,
    c.first_name + ' ' + c.last_name AS customer_name,
    s.store_name,
    st.first_name + ' ' + st.last_name AS staff_name
FROM sales.orders o
JOIN sales.customers c ON o.customer_id = c.customer_id
JOIN sales.stores s ON o.store_id = s.store_id
JOIN sales.staffs st ON o.staff_id = st.staff_id
ORDER BY o.order_id;


-- 2. Show each product with its brand name and category name. Include products even if they have no brand or category assigned.
SELECT 
    p.product_id,
    p.product_name,
    b.brand_name,
    c.category_name
FROM production.products p
LEFT JOIN production.brands b ON p.brand_id = b.brand_id
LEFT JOIN production.categories c ON p.category_id = c.category_id
ORDER BY p.product_name;


-- 3. Find all customers who have never placed an order. Return their name, city, and email.
SELECT 
    c.first_name + ' ' + c.last_name AS customer_name,
    c.city,
    c.email
FROM sales.customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM sales.orders o 
    WHERE o.customer_id = c.customer_id
);


-- 4. Calculate total revenue per store. Revenue = quantity * list_price * (1 - discount). Sort from highest to lowest.
SELECT 
    s.store_name,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_revenue
FROM sales.stores s
JOIN sales.orders o ON s.store_id = o.store_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_name
ORDER BY total_revenue DESC;


-- 5. For each brand, show the number of products, the average list price, and the highest list price. Only include brands with more than 5 products.
SELECT 
    b.brand_name,
    COUNT(*) AS product_count,
    AVG(p.list_price) AS avg_price,
    MAX(p.list_price) AS max_price
FROM production.brands b
JOIN production.products p ON b.brand_id = p.brand_id
GROUP BY b.brand_name
HAVING COUNT(*) > 5
ORDER BY product_count DESC;


-- 6. Show the number of orders and total revenue per month for the year 2017, ordered chronologically.
SELECT 
    MONTH(o.order_date) AS month_num,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS revenue
FROM sales.orders o
JOIN sales.order_items oi ON o.order_id = oi.order_id
WHERE YEAR(o.order_date) = 2017
GROUP BY MONTH(o.order_date)
ORDER BY month_num;


---- 7. Find all products priced above the average list price of their own category.
--Hint: Use a correlated subquery.

SELECT 
    p.product_id,
    p.product_name,
    p.list_price,
    p.category_id
FROM production.products p
WHERE p.list_price > (
    SELECT AVG(p2.list_price)
    FROM production.products p2
    WHERE p2.category_id = p.category_id
)
ORDER BY p.category_id, p.list_price DESC;


-- 8.   List the customers who have placed more orders than the average number of orders per customer.
SELECT 
    c.customer_id,
    c.first_name + ' ' + c.last_name AS customer_name,
    COUNT(o.order_id) AS orders_count
FROM sales.customers c
JOIN sales.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > (
    SELECT AVG(cnt * 1.0)
    FROM (
        SELECT COUNT(*) AS cnt
        FROM sales.orders
        GROUP BY customer_id
    ) t
)
ORDER BY orders_count DESC;


-- 9. Using a CTE, calculate each customer's total spend, then return the top 10 customers with their spend and rank. Add a second CTE that labels each customer as "High" (above the overall average spend) or "Regular".
WITH customer_spend AS (
    SELECT 
        c.customer_id,
        c.first_name + ' ' + c.last_name AS customer_name,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_spend
    FROM sales.customers c
    JOIN sales.orders o ON c.customer_id = o.customer_id
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.first_name, c.last_name
),
ranked AS (
    SELECT *,
           RANK() OVER (ORDER BY total_spend DESC) AS rnk,
           AVG(total_spend) OVER() AS avg_spend
    FROM customer_spend
)
SELECT 
    customer_name,
    total_spend,
    rnk,
    CASE 
        WHEN total_spend > avg_spend THEN 'High'
        ELSE 'Regular'
    END AS segment
FROM ranked
WHERE rnk <= 10
ORDER BY rnk;


-- 10. Using CTEs, find the best-selling product (by quantity) in each category, and show how much of that product's stock is currently available across all stores.
--Hint: Use ROW_NUMBER() or RANK() partitioned by category, then join to production.stocks.

WITH sales_by_product AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category_id,
        cat.category_name,
        SUM(oi.quantity) AS qty_sold
    FROM production.products p
    JOIN production.categories cat ON p.category_id = cat.category_id
    JOIN sales.order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category_id, cat.category_name
),
top_products AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY qty_sold DESC) AS rn
    FROM sales_by_product
)
SELECT 
    tp.category_name,
    tp.product_name,
    tp.qty_sold,
    ISNULL(SUM(st.quantity), 0) AS available_stock
FROM top_products tp
LEFT JOIN production.stocks st ON tp.product_id = st.product_id
WHERE tp.rn = 1
GROUP BY tp.category_name, tp.product_name, tp.qty_sold
ORDER BY tp.category_name;


-- Bonus

---- Bonus
--1:	Rewrite Q8 using a CTE instead of a subquery and compare readability.
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS cnt
    FROM sales.orders
    GROUP BY customer_id
),
avg_orders AS (
    SELECT AVG(cnt * 1.0) AS avg_cnt
    FROM order_counts
)
SELECT 
    c.customer_id,
    c.first_name + ' ' + c.last_name AS customer_name,
    oc.cnt AS orders_count
FROM sales.customers c
JOIN order_counts oc ON c.customer_id = oc.customer_id
CROSS JOIN avg_orders
WHERE oc.cnt > avg_orders.avg_cnt
ORDER BY orders_count DESC;


-- Bonus 2: For Q4, add a column showing each store's percentage share of total company revenue.

WITH store_rev AS (
    SELECT 
        s.store_name,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS revenue
    FROM sales.stores s
    JOIN sales.orders o ON s.store_id = o.store_id
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    GROUP BY s.store_name
)
SELECT 
    store_name,
    revenue,
    CAST(revenue * 100.0 / SUM(revenue) OVER() AS DECIMAL(5,2)) AS percentage_share
FROM store_rev
ORDER BY revenue DESC;
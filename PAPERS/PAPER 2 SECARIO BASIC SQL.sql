--Task 1 — Build the Sales Detail Dataset (6 marks)
--   Management needs a detailed sales dataset for analysis. 
--   Return one row per order item containing:
--   order_id, order_date, customer full name, store name, 
--   staff full name, product name, category name, brand name, 
--   quantity, list_price, discount and net_line_revenue.
--   Include only completed orders (order_status = 4). 
--   Sort from newest to oldest.
SELECT 
    o.order_id,
    o.order_date,
    c.first_name + ' ' + c.last_name AS customer_full_name,
    s.store_name,
    st.first_name + ' ' + st.last_name AS staff_full_name,
    p.product_name,
    cat.category_name,
    b.brand_name,
    oi.quantity,
    oi.list_price,
    oi.discount,
    oi.quantity * oi.list_price * (1 - oi.discount) AS net_line_revenue
FROM sales.orders o
JOIN sales.customers c ON o.customer_id = c.customer_id
JOIN sales.stores s ON o.store_id = s.store_id
JOIN sales.staffs st ON o.staff_id = st.staff_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
JOIN production.products p ON oi.product_id = p.product_id
JOIN production.categories cat ON p.category_id = cat.category_id
JOIN production.brands b ON p.brand_id = b.brand_id
WHERE o.order_status = 4
ORDER BY o.order_date DESC;

--Task 2 — Store Performance Summary (5 marks)
--   Create a store-level performance report for completed orders showing:
--   store name, number of distinct orders, total units sold, 
--   total net revenue and average order value.
--   Order stores from highest to lowest total net revenue.

SELECT 
    s.store_name,
    COUNT(DISTINCT o.order_id) AS number_of_orders,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_net_revenue,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) / COUNT(DISTINCT o.order_id) AS average_order_value
FROM sales.orders o
JOIN sales.stores s ON o.store_id = s.store_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 4
GROUP BY s.store_name
ORDER BY total_net_revenue DESC;

--Task 3 — High-Value Customers (5 marks)
--   Return customers whose total completed-order spending is greater 
--   than the average total spending of customers who have completed orders.
--   Show customer_id, customer name, completed order count and total spending.
--   Order by total spending descending.

WITH customer_total AS (
    SELECT 
        c.customer_id,
        c.first_name + ' ' + c.last_name AS customer_name,
        COUNT(DISTINCT o.order_id) AS completed_order_count,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_spending
    FROM sales.customers c
    JOIN sales.orders o ON c.customer_id = o.customer_id
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 4
    GROUP BY c.customer_id, c.first_name, c.last_name
)
SELECT 
    customer_id,
    customer_name,
    completed_order_count,
    total_spending
FROM customer_total
WHERE total_spending > (SELECT AVG(total_spending) FROM customer_total)
ORDER BY total_spending DESC;


--Task 4 — Inventory Risk Report (5 marks)
--   Return products where the stock quantity is below 5 in at least one store.
--   Show product name, store name, current quantity, category name and brand name.
--   Products with zero stock should appear first.

SELECT 
    p.product_name,
    s.store_name,
    st.quantity AS current_quantity,
    cat.category_name,
    b.brand_name
FROM production.stocks st
JOIN production.products p ON st.product_id = p.product_id
JOIN sales.stores s ON st.store_id = s.store_id
JOIN production.categories cat ON p.category_id = cat.category_id
JOIN production.brands b ON p.brand_id = b.brand_id
WHERE st.quantity < 5
ORDER BY st.quantity ASC;

--Task 5 — Top Products Within Each Category (6 marks)
--   For each product category, identify the top 3 products by total net revenue 
--   from completed orders. Tied products must receive the same position 
--   and the next position should not contain gaps.

WITH product_sales AS (
    SELECT 
        cat.category_name,
        p.product_name,
        SUM(oi.quantity) AS total_units_sold,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_net_revenue
    FROM sales.orders o
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    JOIN production.products p ON oi.product_id = p.product_id
    JOIN production.categories cat ON p.category_id = cat.category_id
    WHERE o.order_status = 4
    GROUP BY cat.category_name, p.product_name
),
ranked AS (
    SELECT 
        category_name,
        product_name,
        total_units_sold,
        total_net_revenue,
        DENSE_RANK() OVER(PARTITION BY category_name ORDER BY total_net_revenue DESC) AS product_position
    FROM product_sales
)
SELECT *
FROM ranked
WHERE product_position <= 3
ORDER BY category_name, product_position;

--Task 6 — Monthly Sales Trend (6 marks)
--   Create a monthly sales trend for completed orders.
--   Show year, month, total net revenue, previous month revenue 
--   and the change from previous month.

WITH monthly AS (
    SELECT 
        YEAR(o.order_date) AS sales_year,
        MONTH(o.order_date) AS sales_month,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_net_revenue
    FROM sales.orders o
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 4
    GROUP BY YEAR(o.order_date), MONTH(o.order_date)
)
SELECT 
    sales_year,
    sales_month,
    total_net_revenue,
    LAG(total_net_revenue) OVER(ORDER BY sales_year, sales_month) AS previous_month_revenue,
    total_net_revenue - LAG(total_net_revenue) OVER(ORDER BY sales_year, sales_month) AS revenue_change
FROM monthly
ORDER BY sales_year, sales_month;

--Task 7 — Reusable Reporting View (4 marks)
--   Create a view named sales.vw_customer_sales_summary 
--   that returns one row per customer with:
--   customer_id, full name, total completed orders, 
--   total units purchased, total net revenue and 
--   most recent completed order date.
--   Customers with no completed orders should also appear.

CREATE OR ALTER VIEW sales.vw_customer_sales_summary
AS
SELECT 
    c.customer_id,
    c.first_name + ' ' + c.last_name AS customer_full_name,
    COUNT(DISTINCT CASE WHEN o.order_status = 4 THEN o.order_id END) AS total_completed_orders,
    ISNULL(SUM(CASE WHEN o.order_status = 4 THEN oi.quantity END), 0) AS total_units_purchased,
    ISNULL(SUM(CASE WHEN o.order_status = 4 THEN oi.quantity * oi.list_price * (1 - oi.discount) END), 0) AS total_net_revenue,
    MAX(CASE WHEN o.order_status = 4 THEN o.order_date END) AS most_recent_completed_order_date
FROM sales.customers c
LEFT JOIN sales.orders o ON c.customer_id = o.customer_id
LEFT JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.first_name, c.last_name;
GO
---------- view dekhna ka lia
SELECT * 
FROM sales.vw_customer_sales_summary
ORDER BY total_net_revenue DESC;


--Task 8 — Safe Data Modification (4 marks)
--   A customer with customer_id = 1 has requested that their 
--   phone number be changed to '(999) 555-0101'.
--   Write the update inside a transaction, validate it, 
--   and show how to roll it back.

BEGIN TRANSACTION;

UPDATE sales.customers
SET phone = '(999) 555-0101'
WHERE customer_id = 1;

-- Check the change
SELECT customer_id, first_name, last_name, phone
FROM sales.customers
WHERE customer_id = 1;

-- Roll back so the database is not permanently changed
ROLLBACK TRANSACTION;


--Task 9 — Store Sales Procedure (6 marks)
--   Create a stored procedure sales.usp_store_sales_report 
--   with parameters @store_id, @start_date, @end_date.
--   Return product name, total units sold and total net revenue 
--   for completed orders of that store in the given date range.
--   Add error handling if start_date is later than end_date.

CREATE OR ALTER PROCEDURE sales.usp_store_sales_report
    @store_id   INT,
    @start_date DATE,
    @end_date   DATE
AS
BEGIN
    IF @start_date > @end_date
    BEGIN
        PRINT 'Error: Start date cannot be later than end date.';
        RETURN;
    END;

    SELECT 
        p.product_name,
        SUM(oi.quantity) AS total_units_sold,
        SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_net_revenue
    FROM sales.orders o
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    JOIN production.products p ON oi.product_id = p.product_id
    WHERE o.store_id = @store_id
      AND o.order_status = 4
      AND o.order_date BETWEEN @start_date AND @end_date
    GROUP BY p.product_name
    ORDER BY total_net_revenue DESC;
END;
GO


--Task 10 — Management Insight Query (3 marks)
--   Write one additional useful query using at least three tables.

SELECT 
    s.store_name,
    cat.category_name,
    SUM(oi.quantity * oi.list_price * (1 - oi.discount)) AS total_net_revenue
FROM sales.orders o
JOIN sales.stores s ON o.store_id = s.store_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
JOIN production.products p ON oi.product_id = p.product_id
JOIN production.categories cat ON p.category_id = cat.category_id
WHERE o.order_status = 4
GROUP BY s.store_name, cat.category_name
ORDER BY s.store_name, total_net_revenue DESC;

/*
1. Business question : Which category sells best in each store?
2. What it measures  : Net revenue by store and category.
3. Why management should care : Helps decide which products to stock more in each store.
*/
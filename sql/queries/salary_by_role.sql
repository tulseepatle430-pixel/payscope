-- Median and average salary by job title, roles with at least 5 postings
SELECT job_title,
       COUNT(*) AS n_jobs,
       ROUND(AVG(salary_midpoint), 0) AS avg_salary,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_midpoint), 0) AS median_salary
FROM jobs
GROUP BY job_title
HAVING COUNT(*) >= 5
ORDER BY median_salary DESC;

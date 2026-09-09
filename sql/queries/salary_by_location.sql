-- Median salary and job count by location
SELECT location,
       COUNT(*) AS n_jobs,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_midpoint), 0) AS median_salary
FROM jobs
GROUP BY location
ORDER BY median_salary DESC;

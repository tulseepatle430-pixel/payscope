-- Average salary for jobs requiring a given skill vs. overall average (salary premium)
WITH overall AS (
    SELECT AVG(salary_midpoint) AS overall_avg FROM jobs
)
SELECT s.skill_name,
       COUNT(*) AS n_jobs,
       ROUND(AVG(j.salary_midpoint), 0) AS avg_salary_with_skill,
       ROUND(AVG(j.salary_midpoint) - overall.overall_avg, 0) AS salary_premium
FROM job_skills js
JOIN skills s ON s.skill_id = js.skill_id
JOIN jobs j ON j.job_id = js.job_id
CROSS JOIN overall
GROUP BY s.skill_name, overall.overall_avg
HAVING COUNT(*) >= 5
ORDER BY salary_premium DESC;

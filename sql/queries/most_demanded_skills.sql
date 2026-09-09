-- Most in-demand skills by number of job postings
SELECT s.skill_name,
       COUNT(*) AS job_count
FROM job_skills js
JOIN skills s ON s.skill_id = js.skill_id
GROUP BY s.skill_name
ORDER BY job_count DESC;

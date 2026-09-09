CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(20) PRIMARY KEY,
    job_title VARCHAR(120) NOT NULL,
    company VARCHAR(120),
    location VARCHAR(80),
    experience_years NUMERIC(4, 1),
    education VARCHAR(60),
    employment_type VARCHAR(40),
    industry VARCHAR(80),
    salary_min NUMERIC(14, 2),
    salary_max NUMERIC(14, 2),
    salary_midpoint NUMERIC(14, 2),
    currency VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(80) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id VARCHAR(20) REFERENCES jobs (job_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills (skill_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs (job_title);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs (location);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills (skill_id);

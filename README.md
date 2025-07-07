# CourseBase: AI-Powered Course Management & Recommendation System

> *Independently developed by [Your Name]*  
> **Deployed Full-Stack | AI-Powered Recommendations | Real-Time Analytics**

 [View Tableau Dashboard](https://public.tableau.com/app/profile/varsha.hemakumar7273/viz/AnalyticsDashboard17457002522590/Dashboard1?publish=yes)

---

##  Overview

**CourseBase** is a production-grade, full-stack course management platform built with a powerful combination of relational databases, AI-driven recommendation systems, and advanced analytics.

- Dual Login System: Separate access for **students** and **admins**.
- Smart Recommendations: AI-based course suggestions using **hybrid filtering**.
- Visual Insights: Integrated **Tableau dashboard** with enrollment trends and performance stats.
- Robust Backend: BCNF-compliant PostgreSQL schema with stored procedures, triggers, and failure handling.
- Live Deployment: Hosted on **Render** using **Flask**, **PostgreSQL**, and **Tableau Public**.

---

##  Features

###  Student Portal
- View & edit personal profiles  
- Browse and self-enroll into courses  
- Track attendance & view personalized recommendations  

###  Admin Portal
- Add/edit/delete students and courses  
- Enroll students manually  
- Monitor attendance and performance trends  
- View dynamic recommendations for each student  
- Secure login and access-controlled dashboard  

---

##  Recommendation Engine

Combines two powerful techniques:
- **Collaborative Filtering** – Using cosine similarity on student-course ratings  
- **Content-Based Filtering** – Course attributes (credits, difficulty, etc.)

Hybrid scoring dynamically excludes already-enrolled courses and generates personalized paths for students.

---

##  Database Design

-  10,000+ Students  
-  50+ Courses  
-  15,000+ Attendance Records  
-  Normalized to **BCNF**  
-  Referential integrity via cascading updates/deletes  
-  Stored procedures and functions for insertion, updates, analytics  

---

##  Advanced SQL Capabilities

- Aggregated performance & rating queries  
- Stored procedures for safe insertions  
- Trigger-based **failure handling** and **logging** (e.g., protected student deletion)  
- Indexing for query optimization (e.g., `student name`, `course department`, `session time`)  

---

##  Analytics Dashboard (Tableau)

Includes:
- Top 10 Most Enrolled Courses  
- Average Ratings by Difficulty  
- Hybrid vs Fallback Recommendation Sources  
- Bubble chart comparing difficulty vs satisfaction  

🔗 [Live Dashboard Access](https://public.tableau.com/app/profile/varsha.hemakumar7273/viz/AnalyticsDashboard17457002522590/Dashboard1?publish=yes)

---

##  Tech Stack

| Layer      | Technology                  |
|------------|------------------------------|
| Frontend   | Flask, HTML/CSS, JS          |
| Backend    | Flask (Python), REST APIs    |
| Database   | PostgreSQL, SQL, PL/pgSQL    |
| AI / Recs  | Python (cosine similarity, filters) |
| Analytics  | Tableau Public               |
| Deployment | Render.com                   |

---

##  Why It Stands Out

- Fully normalized schema and scalable relational model  
- Real-world recommendation engine with hybrid architecture  
- Intuitive dashboards for real-time insights  
- End-to-end production-grade implementation — **everything built and deployed independently by me**

---

##  Auth & Security

- Role-based access: students vs admins  
- Email-verified safe insertions  
- Trigger-based error handling to prevent unauthorized actions  
- Deletion logs for traceability

---

# CourseBase: AI-Powered Course Management & Recommendation System

> *Independently developed by [Your Name]*  
> **Deployed Full-Stack | AI-Powered Recommendations | Real-Time Analytics**

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

 [**View Tableau Dashboard**](https://public.tableau.com/app/profile/varsha.hemakumar7273/viz/AnalyticsDashboard_17457002522590/Dashboard1)

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
##  Data Architecture

### ER Diagram for Course Management System

<img width="469" alt="Screenshot 2025-07-07 at 12 43 26 PM" src="https://github.com/user-attachments/assets/c517bf1d-bbb8-428b-8862-1e4007c8559b" />

> This Entity-Relationship (ER) diagram outlines the high-level structure of the Course Management System, highlighting key relationships between students, courses, instructors, and enrollment records.

---

###  Final Schema After Decomposition (BCNF)

<img width="338" alt="Screenshot 2025-07-07 at 12 43 58 PM" src="https://github.com/user-attachments/assets/80cc1817-8800-421a-b9e6-3d0096fa889f" />

> The schema was normalized to **Boyce-Codd Normal Form (BCNF)** to eliminate redundancy and maintain referential integrity. This decomposition forms the foundation for reliable querying and constraint enforcement in PostgreSQL.

---

##  Tableau Analytics Dashboard

You can explore the real-time visual analytics used in this project — including course trends, top-rated modules, and hybrid recommendation sources — via the interactive dashboard below:

 [**View Tableau Dashboard**](https://public.tableau.com/app/profile/varsha.hemakumar7273/viz/AnalyticsDashboard_17457002522590/Dashboard1)

---

##  Application Preview

<img width="1460" alt="Screenshot 2025-07-07 at 12 49 22 PM" src="https://github.com/user-attachments/assets/07a5a9cf-dc1e-4ee3-9e06-555ee84f9d81" />

> The web interface provides access to enrollment, attendance, and AI-powered recommendations through separate admin and student logins. Built using Flask and PostgreSQL, this interface demonstrates the full-stack functionality of CourseBase.

---




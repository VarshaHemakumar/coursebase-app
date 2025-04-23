import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# from db_config import get_connection

from db_config import get_engine



def get_recommendations_for(student_id):
    engine = get_engine()
    ratings_df = pd.read_sql("SELECT * FROM ratings", engine)

    course_df = pd.read_sql("SELECT course_id, credits, difficulty_level FROM courses", conn)

    enrollment_query = "SELECT course_id FROM enrollment_details WHERE student_id = %s"
    enrolled_df = pd.read_sql(enrollment_query, conn, params=(student_id,))
    enrolled_courses = set(enrolled_df['course_id'].tolist())

    conn.close()

    if ratings_df.empty or course_df.empty:
        return []

    rating_matrix = ratings_df.pivot_table(index='student_id', columns='course_id', values='rating_score').fillna(0)
    if student_id not in rating_matrix.index:
        return []

    similarity = cosine_similarity(rating_matrix)
    sim_df = pd.DataFrame(similarity, index=rating_matrix.index, columns=rating_matrix.index)

    similar_students = sim_df[student_id].sort_values(ascending=False)[1:6]
    weighted_scores = rating_matrix.loc[similar_students.index].T.dot(similar_students)
    cf_recommendations = weighted_scores.sort_values(ascending=False)

    student_courses = rating_matrix.loc[student_id]
    rated_courses = student_courses[student_courses > 0].index.tolist()
    course_features = pd.get_dummies(course_df.set_index('course_id'), columns=['difficulty_level'])

    if rated_courses:
        student_profile = course_features.loc[rated_courses].mean()
        similarities = cosine_similarity([student_profile], course_features)[0]
        cb_scores = pd.Series(similarities, index=course_features.index)
        cb_scores = cb_scores.drop(index=enrolled_courses, errors='ignore')
    else:
        cb_scores = pd.Series(0, index=course_features.index)

    hybrid_scores = (cf_recommendations.add(cb_scores, fill_value=0)).sort_values(ascending=False)
    hybrid_scores = hybrid_scores[~hybrid_scores.index.isin(enrolled_courses)]

    top_courses = hybrid_scores.head(5).index.tolist()
    if not top_courses:
        return []

    conn = get_connection()
    cursor = conn.cursor()
    format_ids = ','.join(map(str, top_courses))
    cursor.execute(f"SELECT course_id, course_name FROM courses WHERE course_id IN ({format_ids})")
    course_info = cursor.fetchall()
    conn.close()

    return [(cid, name, float(hybrid_scores[cid])) for cid, name in course_info if cid in hybrid_scores]

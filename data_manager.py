import database_common


@database_common.connection_handler
def get_question(cursor, question_id):
    query = """
        SELECT q.id, q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image
        FROM question q
        WHERE q.id = %s
        ORDER BY id DESC;"""
    cursor.execute(query, (question_id,))
    return cursor.fetchall()


@database_common.connection_handler
def insert_question(cursor, title, message):
    query = """
        INSERT INTO question (title,message) values(%s,%s);"""
    cursor.execute(query, (title, message,))


@database_common.connection_handler
def insert_answer(cursor, message, question_id):
    query = """
        INSERT INTO answer (message, question_id) values(%s, %s);"""
    cursor.execute(query, (message, question_id,))


@database_common.connection_handler
def get_questions(cursor):
    query = """
        SELECT q.id, q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image
        FROM question q;"""

    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers(cursor, question_id):
    query = """
        SELECT *
        FROM answer
        WHERE question_id = %s;"""

    cursor.execute(query, (question_id,))
    return cursor.fetchall()


@database_common.connection_handler
def search_in_questions(cursor, search_phrase):
    search_phrase = f'%{search_phrase}%'
    query = """SELECT * FROM question
     WHERE title ILIKE %s OR message LIKE %s;"""
    cursor.execute(query, (search_phrase, search_phrase,))
    return cursor.fetchall()


@database_common.connection_handler
def search_in_answers(cursor, search_phrase):
    search_phrase = f'%{search_phrase}%'
    query = """SELECT * FROM answer
      WHERE message ILIKE %s;"""
    cursor.execute(query, (search_phrase,))
    return cursor.fetchall()


@database_common.connection_handler
def sort_questions_by_submission_time_desc(cursor):
    cursor.execute("""SELECT title, id, submission_time, view_number, vote_number FROM question
                      ORDER BY submission_time DESC;""")
    sorted_questions = cursor.fetchall()
    return sorted_questions


@database_common.connection_handler
def sort_questions_by_submission_time_asc(cursor):
    cursor.execute("""SELECT title, id,  submission_time, view_number, vote_number FROM question
                      ORDER BY submission_time;""")
    sorted_questions = cursor.fetchall()
    return sorted_questions


@database_common.connection_handler
def sort_questions_by_name(cursor):
    cursor.execute("""SELECT title, id,  submission_time, view_number, vote_number FROM question
                      ORDER BY title;""")
    sorted_questions = cursor.fetchall()
    return sorted_questions


@database_common.connection_handler
def sort_questions_by_votes(cursor):
    cursor.execute("""SELECT title, id,  submission_time, view_number, vote_number FROM question
                      ORDER BY vote_number DESC;""")
    sorted_questions = cursor.fetchall()
    return sorted_questions


@database_common.connection_handler
def sort_questions_by_views(cursor):
    cursor.execute("""SELECT title, id,  submission_time, view_number, vote_number FROM question
                      ORDER BY view_number DESC;""")
    sorted_questions = cursor.fetchall()
    return sorted_questions


@database_common.connection_handler
def get_tags(cursor):
    query = """
        SELECT t.id, t.name
        FROM tag t;
      """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def insert_tag(cursor, tag_name):
    query = """
        INSERT INTO tag (name) values(%s) RETURNING id;"""
    cursor.execute(query, (tag_name,))
    return cursor.fetchone()['id']


@database_common.connection_handler
def insert_question_tag(cursor, tag_id, question_id):
    query = """
    INSERT INTO question_tag (tag_id, question_id) values(%s,%s);"""
    cursor.execute(query, (tag_id, question_id))


@database_common.connection_handler
def get_tag_by_question_id(cursor, question_id):
    query = """
    SELECT tag.* FROM tag LEFT JOIN question_tag qt ON qt.tag_id=tag.id WHERE question_id=%s;"""
    cursor.execute(query, (question_id,))
    return cursor.fetchall()


@database_common.connection_handler
def delete_tag(cursor, tag_id):
    query = """
    DELETE FROM tag WHERE id=%s;"""
    cursor.execute(query, (tag_id,))


@database_common.connection_handler
def get_answer(cursor, answer_id):
    query = """
        SELECT *
        FROM answer
        WHERE answer.id = %s
        ORDER BY id DESC;"""
    cursor.execute(query, (answer_id,))
    return cursor.fetchall()


@database_common.connection_handler
def insert_comment_answer(cursor, message, answer_id, question_id):
    query = """
        INSERT INTO comment (message, answer_id, question_id) values(%s, %s, %s);"""
    cursor.execute(query, (message, answer_id, question_id))


@database_common.connection_handler
def insert_comment_question(cursor, message, question_id):
    query = """
        INSERT INTO comment (message, question_id) values(%s, %s);"""
    cursor.execute(query, (message, question_id,))


@database_common.connection_handler
def get_comment(cursor, comment_id):
    query = """
            SELECT *
            FROM comment
            WHERE comment.id = %s
            ORDER BY id DESC;"""
    cursor.execute(query, (comment_id,))
    return cursor.fetchall()


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = """
        DELETE 
        FROM question 
        WHERE id = %s;"""

    cursor.execute(query, (question_id,))


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = """
        DELETE 
        FROM answer
        WHERE answer.id = %s;"""

    cursor.execute(query, (answer_id,))


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    query = """
        DELETE 
        FROM comment
        WHERE comment.id = %s;"""

    cursor.execute(query, (comment_id,))


@database_common.connection_handler
def edit_question(cursor, title, message, question_id):
    query = """
        UPDATE question 
        set title = %s, message = %s
        WHERE id =%s;"""

    cursor.execute(query, (title, message, question_id))


@database_common.connection_handler
def edit_answer(cursor, message, answer_id):
    query = """
        UPDATE answer
        set message = %s
        WHERE id = %s;"""

    cursor.execute(query, (message, answer_id))


@database_common.connection_handler
def edit_comment(cursor, message, comment_id):
    query = """
        UPDATE comment
        set message = %s
        WHERE id = %s;"""

    cursor.execute(query, (message, comment_id))


@database_common.connection_handler
def get_comments_for_question(cursor, question_id):
    query = """
        SELECT *
        FROM comment
        WHERE question_id = %s;"""

    cursor.execute(query, (question_id,))
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_for_answer(cursor, answer_id):
    query = """
        SELECT *
        FROM comment
        WHERE answer_id = %s;"""

    cursor.execute(query, (answer_id,))
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_question_id(cursor, question_id):
    query = """
        SELECT *
        FROM answer
        WHERE question_id = %s;"""

    cursor.execute(query, (question_id,))
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_id(cursor, answer_id):
    query = """
        SELECT *
        FROM answer
        WHERE id = %s;"""

    cursor.execute(query, (answer_id,))
    return cursor.fetchall()


@database_common.connection_handler
def update_answer(cursor, answer):
    query = """
    UPDATE answer SET
    vote_number = %s,
    message = %s,
    image = %s
    WHERE id = %s;
    """
    cursor.execute(query, (
        answer['vote_number'],
        answer['message'],
        answer['image'],
        answer['id'],
    ))


@database_common.connection_handler
def update_question(cursor, question):
    query = """
    UPDATE question set
    view_number = %s,
    vote_number = %s,
    title = %s,
    message = %s
    WHERE id = %s;
    """
    cursor.execute(query, (
        question['view_number'],
        question['vote_number'],
        question['title'],
        question['message'],
        question['id'],
    ))

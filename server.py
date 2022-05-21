import re
import bcrypt
from flask import Flask, redirect, render_template, request, abort, url_for, flash, session

import data_manager
from bonus_questions import SAMPLE_QUESTIONS


app = Flask(__name__)
app.config['SECRET_KEY'] = "dfsdfefewreew"

@app.route('/')
def index():
    q = data_manager.get_questions()[-5:]
    return render_template('index.html', questions=q)


@app.route('/list', methods= ['GET', 'POST'])
def show_questions():
    q = data_manager.get_questions()
    show_users_link = logged_in()
    return render_template('questions.html', questions=q, show_users_link=show_users_link)


@app.route("/question/<int:question_id>")
def show_question(question_id):
    author = data_manager.get_author(question_id)['author']
    question = data_manager.get_question(question_id)[0]
    answers = data_manager.get_answers_by_question_id(question_id)
    question['view_number'] += 1
    data_manager.update_question(question)
    t = data_manager.get_tag_by_question_id(question_id)

    for answer in answers:
        answer['comments'] = data_manager.get_comments_for_answer(answer['id'])

    comments = data_manager.get_comments_for_question(question_id)
    return render_template("question.html", question=question, answers=answers, tags=t, comments=comments, author=author)


@app.route('/add-question', methods=['GET', 'POST'])
def ask_question():
    author = session['user_name']
    if request.method == 'GET':
        return render_template('add-question.html')
    if request.method == "POST":
        data_manager.insert_question(request.form['title'], request.form['message'], author)
        return redirect('/list')
    return render_template("add-question.html")


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def put_answer(question_id):
    author = session['user_name']
    question = data_manager.get_question(question_id)

    if not question:
        abort(404)

    if request.method == 'POST':
        data_manager.insert_answer(request.form['message'], question_id, author)
        return redirect(f'/question/{question_id}')
    return render_template("new_answer.html", question=question[0])


@app.route('/search', methods=['POST'])
def search():
    search_phrase = request.form.get('search_phrase')

    answers = data_manager.search_in_answers(search_phrase)
    questions = [data_manager.get_question(answer['question_id'])[0] for answer in answers]
    questions2 = data_manager.search_in_questions(search_phrase)
    add_without_duplicates(questions, questions2)
    return render_template('search.html',
                           search_phrase=search_phrase,
                           questions=questions,
                           answers=answers)


def add_without_duplicates(list1, list2):
    ids = [item['id'] for item in list1]
    list1 += [item for item in list2 if item['id'] not in ids]


def split_ignore_case(pattern, string):
    return re.split(pattern, string, flags=re.IGNORECASE)


app.jinja_env.globals.update(split_ignore_case=split_ignore_case)


@app.route("/filters", methods=["GET", "POST"])
def filters():
    questions = None
    sort = request.form.get("sort")
    if sort == "latest":
        questions = data_manager.sort_questions_by_submission_time_desc()
    if sort == "oldest":
        questions = data_manager.sort_questions_by_submission_time_asc()
    if sort == "name":
        questions = data_manager.sort_questions_by_name()
    if sort == "votes":
        questions = data_manager.sort_questions_by_votes()
    if sort == "views":
        questions = data_manager.sort_questions_by_votes()
    return render_template("questions.html", questions=questions)


@app.route("/question/<int:question_id>/create_new_tag", methods=['GET', 'POST'])
def create_new_tag(question_id):
    if request.method == 'GET':
        return render_template("create_new_tag.html", question_id=question_id)
    if request.method == 'POST':
        tag_id = data_manager.insert_tag(request.form['new_tag_name'])
        data_manager.insert_question_tag(tag_id, question_id)
        return redirect(f'/question/{question_id}')


@app.route("/question/<question_id>/tag/<tag_id>/delete")
def delete_tag(tag_id, question_id):
    data_manager.delete_tag(tag_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<int:question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    question = data_manager.get_question(question_id)
    author = session['user_name']
    if request.method == "GET":
        return render_template("add-comment-to-question.html")

    if request.method == "POST":
        data_manager.insert_comment_question(request.form['message'], question_id, author)
        return redirect(f'/question/{question_id}')
    return render_template('question.html', question=question[0], )


@app.route('/answer/<int:answer_id>')
def show_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    return render_template("answer.html", answer=answer[0])


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    answer = data_manager.get_answer(answer_id)[0]
    question_id = answer["question_id"]

    if request.method == "GET":
        return render_template("add-comment-to-question.html")

    if request.method == "POST":
        data_manager.insert_comment_answer(request.form['message'], answer_id, question_id)
        return redirect(f'/question/{question_id}')
    return render_template("new_comment.html", answers=answer[0])


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect('/list')


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    answer = data_manager.get_answer(answer_id)[0]
    data_manager.delete_answer(answer_id)
    return redirect(f'/question/{answer["question_id"]}')


@app.route('/comment/<comment_id>/delete')
def delete_comment_form_answer(comment_id):
    comment = data_manager.get_comment(comment_id)[0]
    data_manager.delete_comment(comment_id)
    return redirect(f'/question/{comment["question_id"]}')


@app.route('/question/<int:question_id>/edit-page', methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "POST":
        data_manager.edit_question(request.form['title'], request.form['message'], question_id)
        return redirect(f'/question/{question_id}')

    question = data_manager.get_question(question_id)
    return render_template("edit_question.html", question=question[0])


@app.route('/answer/<answer_id>/edit-page', methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = data_manager.get_answer(answer_id)[0]
    if request.method == "POST":
        data_manager.edit_answer(request.form['message'], answer_id)
        question_id = answer["question_id"]
        return redirect(f'/question/{question_id}')

    return render_template("edit_answer.html", answer=answer)


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = data_manager.get_comment(comment_id)[0]
    if request.method == "POST":
        data_manager.edit_comment(request.form['message'], comment_id)
        question_id = comment["question_id"]
        return redirect(f'/question/{question_id}')
    return render_template("edit_comment.html", comment=comment)


@app.route('/question/<question_id>/upvote')
def upvote_question(question_id):
    q = data_manager.get_question(question_id)[0]
    q['vote_number'] += 1
    data_manager.update_question(q)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/down-vote')
def down_vote_question(question_id):
    q = data_manager.get_question(question_id)[0]
    q['vote_number'] -= 1
    data_manager.update_question(q)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<answer_id>/upvote')
def upvote_answer(answer_id):
    answer = data_manager.get_answers_by_id(answer_id)[0]
    answer['vote_number'] += 1
    data_manager.update_answer(answer)
    return redirect(url_for('show_question', question_id=answer['question_id']))


@app.route('/answer/<answer_id>/down-vote')
def down_vote_answer(answer_id):
    answer = data_manager.get_answers_by_id(answer_id)[0]
    answer['vote_number'] -= 1
    data_manager.update_answer(answer)
    return redirect(url_for('show_question', question_id=answer['question_id']))


@app.route("/bonus-questions")
def main():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == "POST":
        user_name = request.form['user_name']
        password = request.form['_hashed_password']
        full_name = request.form['full_name']
        email = request.form['email']
        repeated_password = request.form['repeated_password']
        session['email'] = request.form['email']
        session['user_name'] = request.form['user_name']
        user = data_manager.get_user(user_name)
        if user is None:

            if password == repeated_password:

                data_manager.register(full_name, user_name, email, hash_password(password))
                flash(
                    'You are now registered!')
                return redirect(url_for('show_questions'))
            else:
                flash('Passwords are not the same, try again!')
                return render_template('register.html')
        else:
            flash('You are already registered! Log in!')
            return redirect('/login')

def hash_password(password):
    password = request.form['_hashed_password']
    hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_name = request.form['user_name']
        password = request.form['_hashed_password']
        user = data_manager.get_user(user_name)
        if user is None:
            return render_template('register.html')
        else:
            hashed = user['_hashed_password']
            if bcrypt.checkpw(password.encode('utf8'), hashed.encode('utf-8')):
                session['user_name'] = user_name
                return redirect('/list')
            else:
                flash('Your password is wrong, try again!')
                return render_template('login.html')




@app.route('/logout', methods=["GET", "POST"])
def logout():
    if 'user_name' in session:
        session.pop('user_name', None)
        flash('You are logged out')
    return render_template('logout.html')



@app.route("/users", methods=["GET", "POST"])
def users_list():
    if not logged_in():

        return redirect('/login')
    users = data_manager.get_all_user_details('id', 'user_name', 'email')
    # author = data_manager.get_all_user_details('id')
    # questions = data_manager.get_question_by_author(author)
    # number_of_questions = len(questions)

    # for user in users:
    #     author = data_manager.get_author('user_name')
    #     questions = data_manager.get_question_by_author('author')
    #     number_of_questions = len(questions)
    return render_template('users.html', users=users)

def logged_in():
    return 'user_name' in session

@app.route("/users/<user_name>", methods= ['GET', 'POST'])
def show_user_details(user_name):
    if not logged_in():
        return redirect('/login')
    user_name = session['user_name']
    author = session['user_name']
    questions = data_manager.get_question_by_author(author)
    number_of_questions = len(questions)
    answers = data_manager.get_answer_by_author(author)
    number_of_answers = len(answers)
    comments = data_manager.get_comment_by_author(author)
    number_of_comments = len(comments)
    user = data_manager.get_user_details(user_name)
    return render_template("user.html",
                           user=user,
                           questions=questions,
                           answers=answers,
                           number_of_questions=number_of_questions,
                           number_of_answers=number_of_answers,
                           number_of_comments=number_of_comments,
                           comments=comments)

@app.route("/navigation", methods= ['GET', 'POST'])
def navigation():
    return render_template("navigation.html")

@app.route("/demo")
def demo():
    return render_template("demo.html")

if __name__ == '__main__':
    app.run(debug=True)

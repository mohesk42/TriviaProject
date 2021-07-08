import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_question = questions[start:end]
  return current_question

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={r'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  #Get categories
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()

    category_dict = {} 
    for cat in categories:
      category_dict[cat.id] = cat.type

    if len(categories) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'categories': category_dict
    })

  #Get all questions
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    totalQuestions = len(questions)
    current_questions = paginate_questions(request,questions)

    categories = Category.query.all()
    category_dict = {} 
    for cat in categories:
      category_dict[cat.id] = cat.type

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': totalQuestions,
      'categories': category_dict,
      'currentCategory': 'all'  #all means no category is selected
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()
      return jsonify({
        'success': True
      })
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    difficulty = body.get('difficulty', None)
    category = body.get('category', None)

    try:
      questionModel = Question(question=question, answer=answer, difficulty=difficulty,category=category)
      questionModel.insert()
      return jsonify({
        'success': True
      })
    except:
      abort(422)

  @app.route('/search_questions', methods=['POST'])
  def search_questions():
    searchTerm = request.get_json().get('searchTerm', None)
    questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
    current_questions = paginate_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(questions),
    })

  @app.route('/categories/<int:category_id>/questions')
  def questions_category(category_id):
    category = Category.query.filter_by(id=category_id).one_or_none()
    if category is None:
      abort(404)
    
    questions = Question.query.filter_by(category=category.id).all()

    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'totalQuestions': len(questions),
      'currentCategory': category.type
    })

  @app.route('/quizzes', methods=['POST'])
  def quiz():
    body = request.get_json()
    prev_questions = body.get('previous_questions') 
    quiz_category = body.get('quiz_category')

    #Check category of the quiz
    if quiz_category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).all()
    
    numOfQuestions = len(questions)

    indexToPick = [] #Used to stored index of questions to be selected
    for i in range(numOfQuestions):
      if questions[i].id not in prev_questions:
        indexToPick.append(i)

    if len(indexToPick)==0:
      return jsonify({
        'success': True
      })
    else:
      question = questions[random.choice(indexToPick)] #Get random question
      return jsonify({
        'success': True,
        'question': question.format()
      })

  #Handle 404 errors
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404
  
  #Handle 422 errors
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422
  
  return app

    
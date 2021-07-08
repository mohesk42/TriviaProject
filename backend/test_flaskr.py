import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:2442@localhost:5432/'+self.database_name
        
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    def test_get_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
    
    def test_get_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))
    
    def test_get_questions_with_invalid_page_404(self):
        result = self.client().get('/questions?page=777')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)

    
    def test_delete_question(self):
        result = self.client().delete('/questions/5')
        data = json.loads(result.data)
        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_create_question(self):
        new_question = {
            'question': 'Where does Messi play?',
            'answer': 'Barchelona',
            'difficulty': 3,
            'category': 6
        }
        result = self.client().post('/questions', json=new_question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_question_with_invalid_format_422(self):
        new_question = {
            'question': 'Where does Messi play?',
            'answer': 'Barchelona',
            'difficulty': 3,
            'category': 771
        }
        result = self.client().post('/questions', json=new_question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_search_questions(self):
        result = self.client().post('/search_questions', json={'searchTerm':'what'})
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))

    def test_search_questions_not_found(self):
        result = self.client().post('/search_questions', json={'searchTerm':'kxjoikjfer44'})
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),0)

    def test_questions_by_category(self):
        result = self.client().get('/categories/3/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['currentCategory'], 'Geography')
        self.assertTrue(len(data['questions']))

    def test_questions_by_category_with_invalid_category(self):
        result = self.client().get('/categories/55/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_quiz(self):
        result = self.client().post('/quizzes', json={
            'previous_questions':[30,31,33],
            'quiz_category':{'type': 'Art', 'id': '2'}
        })
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 30)
        self.assertNotEqual(data['question']['id'], 31)
        self.assertNotEqual(data['question']['id'], 33)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
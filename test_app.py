import unittest
from handyman import app, db, BlogPost, Category

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_search(self):
        with app.test_client() as client:
            # Create some test blog posts
            post1 = BlogPost(title="Test Post 1", content="Testing search function")
            post2 = BlogPost(title="Another Post", content="This is a different post")
            db.session.add(post1)
            db.session.add(post2)
            db.session.commit()

            # Search for "Test"
            response = client.get('/search?query=Test')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Test Post 1", response.data)
            self.assertNotIn(b"Another Post", response.data)

            # Search for "post"
            response = client.get('/search?query=post')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Test Post 1", response.data)
            self.assertIn(b"Another Post", response.data)

            # Search for "Random Text"
            response = client.get('/search?query=Random+Text')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b"Test Post 1", response.data)
            self.assertNotIn(b"Another Post", response.data)

    def test_new_post(self):
        with app.test_client() as client:
            # Ensure that the new_post route returns status code 200
            response = client.get('/posts/new')
            self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        with app.test_client() as client:
            # Create a test blog post
            post = BlogPost(title="Test Post", content="This is a test post")
            db.session.add(post)
            db.session.commit()

            # Ensure that the post is deleted
            response = client.get(f'/posts/delete/{post.id}')
            self.assertEqual(response.status_code, 302)

            # Ensure that the post is no longer in the database
            deleted_post = BlogPost.query.get(post.id)
            self.assertIsNone(deleted_post)

    def test_edit_post(self):
        with app.test_client() as client:
            # Create a test blog post
            post = BlogPost(title="Test Post", content="This is a test post")
            db.session.add(post)
            db.session.commit()

            # Ensure that the edit route returns status code 200
            response = client.get(f'/posts/edit/{post.id}')
            self.assertEqual(response.status_code, 200)

            # Edit the post
            updated_title = "Updated Post"
            updated_content = "This post has been updated"
            response = client.post(f'/posts/edit/{post.id}', data={
                'title': updated_title,
                'content': updated_content,
                'email': post.email,
                'category': post.category_id
            })
            self.assertEqual(response.status_code, 302)

            # Ensure that the post has been updated in the database
            updated_post = BlogPost.query.get(post.id)
            self.assertEqual(updated_post.title, updated_title)
            self.assertEqual(updated_post.content, updated_content)

    # Add more tests for other routes and functionalities as needed

if __name__ == '__main__':
    unittest.main()

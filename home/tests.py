"""
tests.py 
**********
Houses all unit tests that can be automatically run
"""
from django.test import TestCase
from django.contrib.auth.models import User
from . import views, models


# Create your tests here.
### VIEW TESTS
class TEST_VIEWS(TestCase):
    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        link = models.EmbedLink.objects.create(type='U',
                                               universeName='index',
                                               description='something',
                                               mapSlug='abc',
                                               viewSlug='def',
                                               embedURL='www.google.com',
                                               bare=False,
                                               simple=False,
                                               scroll=False)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_map(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/insightMap/')
        self.assertEqual(response.status_code, 200)

    def test_blueprint(self):
        response = self.client.get('/insightMap/blueprint.json')
        self.assertEqual(response.status_code, 200)

    def test_mapindex(self):
        element = models.Element(label="name",
                                 description="something here",
                                 type="S")
        element.save()
        element.tags.add(models.EmbedLink.objects.get(universeName="index"))
        element.save()
        user2 = User.objects.create(id=0, username="temporaryStaff", email='temporary@temp.com', password="temp")
        user2.is_superuser = True
        user2.save()
        self.client.login(username="temporaryStaff", password="temp")
        response = self.client.get('/insightMap/index')
        self.assertEqual(response.status_code, 302)

    def test_profile(self):
        self.client.login(username="temporary", password="temporary")
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_report(self):
        self.client.login(username="temporary", password="temporary")
        response = self.client.get('/userReport/')
        # expect redirect home
        self.assertEqual(response.status_code, 302)

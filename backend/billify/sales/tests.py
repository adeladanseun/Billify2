from django.test import TestCase
from django.contrib.auth.models import User
# Create your tests here.
class RandomClass():
    a = 'hello'
    
class UserValidation(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        user = User.objects.create_user(username=self.username, 
                                             password=self.password)
    def test_user_instance_object(self):
        user = User.objects.get(username=self.username)
        self.assertIsInstance(user, User)
    def test_false_user_instance_object(self):
        user = User.objects.get(username=self.username)
        self.assertNotIsInstance(user, RandomClass)
    def return_user(self):
        return User.objects.get(username=self.username)
from django.test import TestCase
from users_app.models import User

class UserTestCase(TestCase):
    
    def setUp(self):
        # Create 3 users
        self.user1 = User.objects.create(first_name='Alice', last_name='Smith')
        self.user2 = User.objects.create(first_name='Bob', last_name='Jones')
        self.user3 = User.objects.create(first_name='Charlie', last_name='Brown')

    
    def test_users_creation(self):
        """Test the creation of three users."""
        
        # Retrieve the users
        user1 = User.objects.get(first_name='Alice')
        user2 = User.objects.get(first_name='Bob')
        user3 = User.objects.get(first_name='Charlie')
        
        # Assert that the users exist and their details are correct
        self.assertEqual(user1.last_name, 'Smith')
        self.assertEqual(user2.last_name, 'Jones')
        self.assertEqual(user3.last_name, 'Brown')
        
        # Assert that there are exactly 3 users in the database
        self.assertEqual(User.objects.count(), 3)

        print("All users created successfully!")

# Run the test using Django's test runner
# python manage.py test users_app.tests.test_users

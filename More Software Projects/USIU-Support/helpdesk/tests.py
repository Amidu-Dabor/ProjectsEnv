from django.test import TestCase
from django.contrib.auth import get_user_model


# Create your tests here.

class UserAccountTests(TestCase):
    
    def test_new_superuser(self):
        db = get_user_model()
        super_user = db.objects.create_superuser(
            'testuser@super.com', 'firstname', 'middlename', 'lastname', 'username', 'password'
        )
        
        self.assertEqual(super_user.email, 'testuser@super.com')
        self.assertEqual(super_user.first_name, 'firstname')
        self.assertEqual(super_user.middle_name, 'middlename')
        self.assertEqual(super_user.last_name, 'lastname')
        self.assertTrue(super_user.staff)
        self.assertTrue(super_user.superuser)
        self.assertTrue(super_user.active)
        self.assertEqual(str(super_user), 'username')


        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email='testuser@super.com', first_name='firstname', middle_name='middlename', last_name='lastname', user_name='username', password='password', staff=False
            )

        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email='testuser@super.com', first_name='firstname', middle_name='middlename', last_name='lastname', user_name='username', password='password', superuser=False
            )
            
        # with self.assertRaises(ValueError):
        #     db.objects.create_superuser(
        #         email='testuser@super.com', first_name='firstname', middle_name='middlename', last_name='lastname', user_name='username', password='password', is_active=False
        #     )
            
        with self.assertRaises(ValueError):
            db.objects.create_superuser(
                email='testuser@super.com', first_name='firstname', middle_name='middlename', last_name='lastname', user_name='username', password='password', superuser=True
            )
            
            
    def test_new_user(self):
        db = get_user_model()
        user = db.objects.create_user(
            'testuser@super.com', 'firstname', 'middlename', 'lastname', 'username', 'password'
        )
        
        self.assertEqual(user.email, 'testuser@super.com')
        self.assertEqual(user.first_name, 'firstname')
        self.assertEqual(user.middle_name, 'middlename')
        self.assertEqual(user.last_name, 'lastname')
        self.assertFalse(user.staff)
        self.assertFalse(user.superuser)
        self.assertFalse(user.active)
        
        with self.assertRaises(ValueError):
            db.objects.create_user(
                email='testuser@super.com', first_name='firstname', middle_name='middlename', last_name='lastname', user_name='username', password='password'
            )

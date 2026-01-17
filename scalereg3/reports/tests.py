from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone


class IndexTest(TestCase):

    def test_not_logged_in(self):
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin/login/?next=/reports/')

    def test_normal_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=False)
        self.client.force_login(user)
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin/login/?next=/reports/')

    def test_staff_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=True)
        self.client.force_login(user)
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            '<a href="sales_dashboard/">Sales Dashboard</a>')
        self.assertContains(
            response,
            '<a href="payment_code_usage/">Payment Code Usage</a>')


class SalesDashboardTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        today = timezone.now()
        day = timezone.timedelta(days=1)

        order_objects = apps.get_model('reg23', 'Order').objects
        create_order_with_date = cls.create_order_with_date
        create_order_with_date(order_objects,
                               today,
                               order_num='0',
                               valid=True,
                               payment_type='cash',
                               amount=2)
        create_order_with_date(order_objects,
                               today - (8 * day),
                               order_num='1',
                               valid=True,
                               payment_type='payflow',
                               amount=3)
        create_order_with_date(order_objects,
                               today - (31 * day),
                               order_num='2',
                               valid=True,
                               payment_type='cash',
                               amount=7)

    @staticmethod
    def create_order_with_date(order_objects, date, **kwargs):
        order = order_objects.create(**kwargs)
        order.date = date
        order.save()

    def test_not_logged_in(self):
        response = self.client.get('/reports/sales_dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/admin/login/?next=/reports/sales_dashboard/')

    def test_normal_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=False)
        self.client.force_login(user)
        response = self.client.get('/reports/sales_dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/admin/login/?next=/reports/sales_dashboard/')

    def test_staff_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=True)
        self.client.force_login(user)
        response = self.client.get('/reports/sales_dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<tr><td>Revenue</td><td>$2.00</td><td>$5.00</td><td>$12.00</td></tr>',
            html=True)
        self.assertContains(
            response,
            '<tr><td>Payflow</td><td>0</td><td>1</td><td>1</td><td>$3.00</td></tr>',
            html=True)
        self.assertContains(
            response,
            '<tr><td>Cash</td><td>1</td><td>1</td><td>2</td><td>$9.00</td></tr>',
            html=True)


class PaymentCodeUsageTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        ticket_model = apps.get_model('reg23', 'Ticket')
        order_model = apps.get_model('reg23', 'Order')
        payment_code_model = apps.get_model('reg23', 'PaymentCode')
        attendee_model = apps.get_model('reg23', 'Attendee')

        ticket = ticket_model.objects.create(
            name='FULL',
            description='Full',
            ticket_type='full',
            price=100,
            public=True,
            cash=True,
            upgradable=False)

        order_with_attendee = order_model.objects.create(
            order_num='ORDER0001',
            valid=True,
            name='Jane Doe',
            address='1 Main',
            city='Portland',
            state='OR',
            zip_code='97201',
            country='USA',
            email='jane@example.com',
            phone='',
            amount=0,
            payment_type='cash')
        payment_code_model.objects.create(
            code='ORDER0001',
            badge_type=ticket,
            order=order_with_attendee,
            max_attendees=3)
        attendee_model.objects.create(
            badge_type=ticket,
            order=order_with_attendee,
            valid=True,
            checked_in=False,
            salutation='Ms',
            first_name='Sam',
            last_name='Smith',
            title='',
            org='',
            email='sam@example.com',
            zip_code='97201',
            phone='')

        order_without_attendee = order_model.objects.create(
            order_num='ORDER0002',
            valid=True,
            name='No Uses',
            address='2 Main',
            city='Portland',
            state='OR',
            zip_code='97201',
            country='USA',
            email='no@example.com',
            phone='',
            amount=0,
            payment_type='cash')
        payment_code_model.objects.create(
            code='ORDER0002',
            badge_type=ticket,
            order=order_without_attendee,
            max_attendees=5)

    def test_not_logged_in(self):
        response = self.client.get('/reports/payment_code_usage/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/admin/login/?next=/reports/payment_code_usage/')

    def test_normal_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=False)
        self.client.force_login(user)
        response = self.client.get('/reports/payment_code_usage/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/admin/login/?next=/reports/payment_code_usage/')

    def test_staff_user_logged_in(self):
        user = get_user_model().objects.create_user('user', is_staff=True)
        self.client.force_login(user)
        response = self.client.get('/reports/payment_code_usage/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<tr><td>Jane Doe</td><td>ORDER0001</td><td>Full</td><td>1</td><td>3</td>'
            '<td><a href="/admin/reg23/attendee/?q=ORDER0001">View (1)</a></td>'
            '<td><a href="/admin/reg23/paymentcode/ORDER0001/change/">Edit</a></td></tr>',
            html=True)

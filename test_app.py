import unittest
from flask_testing import TestCase
from flask import url_for
from project import app, db, Accounts, Transactions  # Import modul-modul yang diperlukan
from datetime import datetime

# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    def tearDown(self):
        db.session.remove()  # Menghapus sesi database
        db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/')  # Melakukan request GET ke '/'
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk membuat karyawan baru
    def test_create_account(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response = self.client.post('/docs/addaccount', json={
            'customer_name': 'Alexx',
            'balance': 5000000,
            'type': 'Priority'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        account = Accounts.query.first()  # Mengambil karyawan pertama dari database
        self.assertEqual(account.customer_name, 'Alexx')  # Memastikan nama karyawan adalah 'John Doe'

    def test_update_account(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response1 = self.client.post('/docs/addaccount', json={
            'customer_name': 'Alexander',
            'balance': 5000000,
            'type': 'Priority'
        })

        response = self.client.post('/docs/updateaccount', json={
            'customer_name': 'Alexander',
            'balance': 4000000,
            'type': 'Priority'
        })

        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        account = Accounts.query.filter(Accounts.customer_name.like(f"%Alexander%")).first() # Mengambil karyawan pertama dari database
        self.assertEqual(account.customer_name, 'Alexander')  # Memastikan nama karyawan adalah 'John Doe'

    # Test untuk menghapus karyawan
    def test_delete_karyawan(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        account = Accounts(customer_name='Chan', balance=0, type='Standart')
        db.session.add(account)
        db.session.commit()

        # Melakukan request DELETE ke '/karyawan/{id_karyawan}'
        response = self.client.delete(f'/deleteaccount/{account.account_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Accounts.query.get(account.account_id))  # Memastikan karyawan dengan id tersebut sudah dihapus

    # Test untuk mendapatkan semua karyawan
    def test_get_all_karyawan(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        account1 = Accounts(customer_name='Fill', balance=300000, type='Standart')
        account2 = Accounts(customer_name='Fabs', balance=9000000, type='Priority')
        db.session.add(account1)
        db.session.add(account2)
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/accounts')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('accounts.html')  # Memastikan template yang digunakan adalah 'displayall.html'
        self.assertIn(b'Fill', response.data)  # Memastikan 'John Doe' ada dalam response data
        self.assertIn(b'Fabs', response.data)  # Memastikan 'Jane Doe' ada dalam response data

    # Test untuk membuat karyawan baru
    def test_create_trans(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response1 = self.client.post('/docs/addaccount', json={
            'customer_name': 'Travis',
            'balance': 5000000,
            'type': 'Priority'
        })

        response = self.client.post('/docs/addtransaction', json={
            'customer_name': 'Travis',
            'amount': 5000,
            'date': '2023-08-08' ,
            'type': 'income'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created

    # Test untuk mendapatkan semua karyawan
    def test_get_all_trans(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        account1 = Accounts(customer_name='Fill', balance=300000, type='Standart')
        db.session.add(account1)
        db.session.commit()

        trans1 = Transactions(account_id=account1.account_id, amount=100, date=datetime.strptime('2023-08-08','%Y-%m-%d'), type='expense')
        trans2 = Transactions(account_id=account1.account_id, amount=100, date=datetime.strptime('2023-08-08','%Y-%m-%d'), type='income')
        db.session.add(trans1)
        db.session.add(trans2)
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/transactions')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('transactions.html')  # Memastikan template yang digunakan adalah 'displayall.html'

if __name__ == '__main__':
    unittest.main()  # Menjalankan semua test
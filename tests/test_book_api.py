from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestLibraryAPI(HttpCase):
    
    def test_create_book_endpoint(self):
        data = {
            'name': 'API Test Book',
        }
        
        response = self.url_open('/library/book/create', data=data)
        
        self.assertEqual(response.status_code, 200, "Response should be 200 OK")
        
        content = response.content.decode('utf-8')
        self.assertIn("Book Created with ID:", content)
        
        book_id = int(content.split(': ')[1])
        book = self.env['library.books'].browse(book_id)
        self.assertTrue(book.exists(), "Book should exist in database")
        self.assertEqual(book.title, 'API Test Book', "Book title should match")

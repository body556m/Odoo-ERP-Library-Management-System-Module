from odoo import models, fields

class LibraryBookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Book Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    book_ids = fields.One2many('library.books', 'category_id', string='Books')
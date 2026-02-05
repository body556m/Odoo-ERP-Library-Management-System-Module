from odoo import models, fields, api


class LibraryPublisher(models.Model):
    _name = 'library.publisher'
    _description = 'Library Publisher'

    name = fields.Char(string='Publisher Name', required=True)
    book_ids = fields.One2many('library.books', 'publisher_id', string='Books')
    book_count = fields.Integer(string='Book Count', compute='_compute_book_count')

    @api.depends('book_ids')
    def _compute_book_count(self):
        for rec in self:
            rec.book_count = len(rec.book_ids)

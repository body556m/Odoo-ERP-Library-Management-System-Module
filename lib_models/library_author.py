from odoo import models, fields

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Author'

    name = fields.Char(string='Author', required=True)
    date_of_birth = fields.Date(string='Author Birthday')
    book_ids = fields.One2many('library.books', 'author_id', string="Authored Books")
    book_count = fields.Integer(string="Count of Books", compute='_compute_book_count')

    def _compute_book_count(self):
        for rec in self:
            rec.book_count = len(rec.book_ids)

    def action_view_books(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Books',
            'view_mode': 'tree,form',
            'res_model': 'library.books',
            'domain': [('author_id', '=', self.id)],
            'context': {'default_author_id': self.id},
        }


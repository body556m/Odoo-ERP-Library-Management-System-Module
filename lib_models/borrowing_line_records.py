from odoo import models, fields, api


class BorrowingLine(models.Model):
    _name = 'borrowing.line'
    _description = 'Borrowing Line'

    borrowing_id = fields.Many2one('borrowing.records', string='Borrowing Records', required=True, ondelete='cascade')
    book_id = fields.Many2one('library.books', string='Book Title', required=True)
    date_returned_line = fields.Date(string='Date Returned')
    line_state = fields.Selection([
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
    ], string='Book Status', default='borrowed', required=True)
    parent_state = fields.Selection(related='borrowing_id.state', string='Parent State', readonly=True)

    def action_return_book_line(self):
        self.ensure_one()
        if self.line_state == 'borrowed':
            self.date_returned_line = fields.Date.context_today(self)
            self.line_state = 'returned'
        return True

    @api.model
    def create(self, vals):
        line = super(BorrowingLine, self).create(vals)

        if line.book_id and line.line_state == 'borrowed':
            line.book_id.write({'copies': line.book_id.copies - 1})
        return line

    def write(self, vals):
        result = super(BorrowingLine, self).write(vals)
        if vals.get('line_state') == 'returned':
            for line in self:
                if line.book_id:
                    line.book_id.write({'copies': line.book_id.copies + 1})
        elif vals.get('line_state') == 'lost':
            pass
        return result
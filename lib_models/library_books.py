import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class LibraryBooks(models.Model):
    _name = "library.books"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Library Books"
    _rec_name = 'title'

    sequence_name = fields.Char(string="Sequence Name", default="New", index=True, readonly=True)
    title = fields.Char(required=True, string="Book Title")
    isbn = fields.Char(string="ISBN", required=True, help="International Standard Book Number", index=True)
    publisher_id = fields.Many2one('library.publisher', string="Publisher")
    author_id = fields.Many2one('library.author', string="Authors", tracking=1)
    author_name = fields.Char(related='author_id.name')
    author_dob = fields.Date(related='author_id.date_of_birth', readonly=False)
    pages = fields.Integer(string="Pages", default=100, help="The number of book pages")
    price = fields.Float(string="Price")
    copies = fields.Integer(string="Copies", default=1)
    available = fields.Boolean(string="Available", compute="_compute_available", store=True, tracking=1)
    published_date = fields.Date(string="Published Date", default=fields.Date.context_today)
    created_by_user = fields.Char(string="Creator Name", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('lost', 'Lost'),
        ('archived', 'Archived')
    ], default="draft")
    category_id = fields.Many2one('library.book.category', string='Category')
    borrowing_line_ids = fields.One2many('borrowing.line', 'book_id', string='History of Borrowing')
    description = fields.Text(string="Description")
    description_summary = fields.Text(string="Description Summary", readonly=True)
    active = fields.Boolean(default=True)
    
    edition = fields.Char(string="Edition")
    language_id = fields.Many2one('res.lang', string="Language")
    rating = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
        ('4', 'Excellent'),
        ('5', 'Masterpiece')
    ], string="Rating", default='0')
    shelf_location = fields.Char(string="Shelf Location")
    
    total_borrowed_count = fields.Integer(string="Total Borrowed Times", compute="_compute_borrowing_stats")
    currently_borrowed_count = fields.Integer(string="Currently Borrowed", compute="_compute_borrowing_stats")
    
    def _compute_borrowing_stats(self):
        for book in self:
            book.total_borrowed_count = self.env['borrowing.line'].search_count([('book_id', '=', book.id)])
            book.currently_borrowed_count = self.env['borrowing.line'].search_count([('book_id', '=', book.id), ('line_state', '=', 'borrowed')])

    @api.onchange('description')
    def _onchange_description(self):
        for rec in self:
            if rec.description:
                rec.description_summary = rec.description[:50]
            else:
                rec.description_summary = False

    _sql_constraints = [
        ('unique_isbn', 'unique(isbn)', 'This ISBN already exists!'),
        ('positive_price', 'CHECK(price > 0)', 'The price must be positive.'),
    ]

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_available(self):
        for rec in self:
            rec.state = 'available'

    def action_rented(self):
        for rec in self:
            rec.state = 'rented'
            
    def action_archive(self):
        for rec in self:
            rec.state = 'archived'

    @api.depends('copies')
    def _compute_available(self):
        for rec in self:
            rec.available = rec.copies > 0

    @api.constrains('pages')
    def _check_pages(self):
        for rec in self:
            if rec.pages < 10:
                raise ValidationError("The number of pages is not valid to be a book.")

    @api.model
    def create(self, vals):    
        res = super(LibraryBooks, self).create(vals)
        if res.sequence_name == 'New':
            res.sequence_name = self.env['ir.sequence'].next_by_code('library_books_seq')
        return res

    def get_latest_book_creator(self):
        latest_book = self.search([], order='create_date desc', limit=1)
        if latest_book:
            creator_user = self.env['res.users'].browse(latest_book.create_uid.id)
            _logger.info(f"The creator of the latest book is: {creator_user.name} (ID: {creator_user.id})")

    def excel_books_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/library/excel/books/{self.env.context.get("active_ids")}',
            'target': 'new'
        }

    def check_availability(self):
        for rec in self:
            if rec.available:
                _logger.info(f"Book '{rec.title}' is available.")
            else:
                _logger.info(f"Book '{rec.title}' is NOT available.")
        
        return True

    def action_library_statistics(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'library.library_statistics',
            'name': 'Library Statistics',
        }
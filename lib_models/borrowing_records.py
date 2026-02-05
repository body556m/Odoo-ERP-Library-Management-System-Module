from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class BorrowingRecords(models.Model):
    _name = 'borrowing.records'
    _description = 'Book Borrowing Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_borrowed desc'

    name = fields.Char(string='Record Number', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('borrowing.records'))
    member_id = fields.Many2one('library.member', string='Member', required=True)
    date_borrowed = fields.Date(string='Date Borrowed', default=fields.Date.context_today, required=True)
    date_expected_return = fields.Date(string='Date Expected Return', required=True)
    date_returned = fields.Date(string='Date Returned')
    
    fine_per_day = fields.Float(string="Fine Per Day", default=10.0)
    total_fine = fields.Float(string="Total Fine", compute="_compute_total_fine", store=True)
    fine_paid = fields.Boolean(string="Fine Paid", default=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('fully_returned', 'Returned'),
        ('partially_returned', 'Partially Returned'),
        ('lost', 'Lost'),
        ('expired', 'Expired')
    ], string='Status', default='draft', compute='_compute_borrowing_state', store=True, tracking=True)
    
    borrowing_line_ids = fields.One2many('borrowing.line', 'borrowing_id', string='Borrowed Books')
    
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_overdue_status', store=True)
    total_books_count = fields.Integer(string='Total Books Count', compute='_compute_books_count', store=True)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('state', 'date_returned', 'date_expected_return', 'fine_per_day')
    def _compute_total_fine(self):
        today = fields.Date.context_today(self)
        for rec in self:
            fine = 0.0
            if rec.date_expected_return:
                overdue_days = 0
                if rec.state in ['borrowed', 'partially_returned']:
                    if today > rec.date_expected_return:
                        overdue_days = (today - rec.date_expected_return).days
                elif rec.state == 'fully_returned' and rec.date_returned:
                    if rec.date_returned > rec.date_expected_return:
                        overdue_days = (rec.date_returned - rec.date_expected_return).days
                
                if overdue_days > 0:
                    fine = overdue_days * rec.fine_per_day
            
            rec.total_fine = fine

    def archive_old_returned_loans(self):
        one_year_ago = fields.Date.today() - relativedelta(years=1)
        records_to_archive = self.search([
            ('state', '=', 'fully_returned'),
            ('date_returned', '<', one_year_ago),
            ('active', '=', True)
        ])
        records_to_archive.write({'active': False})


    @api.depends('borrowing_line_ids.line_state')
    def _compute_borrowing_state(self):
        for record in self:
            if not record.borrowing_line_ids:
                record.state = 'draft'
                continue

            borrowed_count = len(record.borrowing_line_ids.filtered(lambda l: l.line_state == 'borrowed'))
            returned_count = len(record.borrowing_line_ids.filtered(lambda l: l.line_state == 'returned'))
            total_count = len(record.borrowing_line_ids)
            if borrowed_count == total_count:
                record.state = 'borrowed'
            elif returned_count == total_count:
                record.state = 'fully_returned'
            elif returned_count > 0 and borrowed_count > 0:
                record.state = 'partially_returned'
            else:
                record.state = 'draft'


    @api.depends('borrowing_line_ids.line_state')
    def _compute_books_count(self):
        for record in self:
            record.total_books_count = len(record.borrowing_line_ids)

    @api.depends('date_expected_return', 'date_returned', 'state')
    def _compute_overdue_status(self):
        today = fields.Date.context_today(self)
        for record in self:
            is_overdue = False
            if record.state in ['borrowed', 'partially_returned'] and record.date_expected_return and record.date_expected_return < today:
                is_overdue = True

            record.is_overdue = is_overdue

    def action_confirm_borrowing(self):
        self.ensure_one()
        self.state = 'borrowed'
        template = self.env.ref('library.mail_template_borrowing_confirmation')
        if template:
            template.send_mail(self.id, force_send=True)

    def action_return_book(self):
        self.ensure_one()
        if not self.date_returned:
            self.date_returned = fields.Date.context_today(self)
        self.state = 'fully_returned'
        for line in self.borrowing_line_ids:
             if line.line_state == 'borrowed':
                 line.action_return_book_line()

    def excel_borrowing_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/library/excel/borrowing/{self.id}',
            'target': 'new'
        }

    @api.constrains('date_borrowed', 'date_expected_return')
    def _check_dates_consistency(self):
        for record in self:
            if record.date_expected_return and record.date_borrowed > record.date_expected_return:
                raise ValidationError("Date Expected Return Can Not Be Before Date Borrowed")

    @api.model
    def _cron_check_overdue_books(self):
        today = fields.Date.context_today(self)
        overdue_records = self.search([
            ('state', 'in', ['borrowed', 'partially_returned']),
            ('date_expected_return', '<', today),
            ('active', '=', True)
        ])
        template = self.env.ref('library.mail_template_overdue_notification')
        for record in overdue_records:
            if template:
                template.send_mail(record.id, force_send=False)

    @api.model
    def _cron_send_return_reminders(self):
        today = fields.Date.context_today(self)
        deadline = today + relativedelta(days=2)
        records_to_remind = self.search([
             ('state', 'in', ['borrowed', 'partially_returned']),
             ('date_expected_return', '=', deadline),
             ('active', '=', True)
        ])
        template = self.env.ref('library.mail_template_return_reminder')
        for record in records_to_remind:
             if template:
                 template.send_mail(record.id, force_send=False)

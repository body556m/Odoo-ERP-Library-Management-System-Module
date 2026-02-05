from odoo import models, fields, api, _

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    card_number = fields.Char(string="Card Number", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Contact Name", required=True, delegate=True, ondelete='cascade')
    member_image = fields.Binary(related='partner_id.image_1920', readonly=False, string="Member Image")
    
    membership_date = fields.Date(string="Membership Date", default=fields.Date.context_today)
    membership_expiry_date = fields.Date(string="Expiry Date")
    membership_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('public', 'Public'),
        ('staff', 'Staff')
    ], string="Membership Type", default='public', required=True)
    
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='active', group_expand='_expand_states', tracking=True)

    max_books_allowed = fields.Integer(string="Max Books Allowed", default=3)
    borrowing_ids = fields.One2many('borrowing.records', 'member_id', string="Borrowing History")
    
    active_borrowings_count = fields.Integer(string="Active Borrowings", compute="_compute_active_borrowings_count")
    total_fines = fields.Float(string="Total Fines", compute="_compute_total_fines")
    
    @api.model
    def create(self, vals):
        if vals.get('card_number', _('New')) == _('New'):
            vals['card_number'] = self.env['ir.sequence'].next_by_code('library.member') or _('New')
        return super(LibraryMember, self).create(vals)

    @api.depends('borrowing_ids.borrowing_line_ids.line_state')
    def _compute_active_borrowings_count(self):
        for member in self:
            member.active_borrowings_count = self.env['borrowing.line'].search_count([
                ('borrowing_id.member_id', '=', member.id),
                ('line_state', '=', 'borrowed')
            ])

    def _compute_total_fines(self):
        for member in self:
            member.total_fines = 0.0

    def action_renew_membership(self):
        for member in self:
            member.state = 'active'

    def action_suspend_membership(self):
        for member in self:
            member.state = 'suspended'

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

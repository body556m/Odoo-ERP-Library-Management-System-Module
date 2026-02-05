from odoo import models, fields, api, _


class LibraryBookReservation(models.Model):
    _name = 'library.book.reservation'
    _description = 'Library Book Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reservation_date desc'

    name = fields.Char(string='Reservation Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    member_id = fields.Many2one('library.member', string='Member', required=True)
    book_id = fields.Many2one('library.books', string='Book', required=True)
    reservation_date = fields.Date(string='Reservation Date', default=fields.Date.context_today, required=True)
    expiry_date = fields.Date(string='Expiry Date', required=True)
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('fulfilled', 'Fulfilled')
    ], string='Status', default='pending', tracking=True)
    
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('library.reservation.sequence') or _('New')
        return super(LibraryBookReservation, self).create(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            
    def action_fulfill(self):
        for rec in self:
            rec.state = 'fulfilled'

    @api.model
    def _cron_expire_old_reservations(self):
        today = fields.Date.context_today(self)
        expired_reservations = self.search([
            ('state', 'in', ['pending', 'confirmed']),
            ('expiry_date', '<', today)
        ])
        expired_reservations.write({'state': 'expired'})

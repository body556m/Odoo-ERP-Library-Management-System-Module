from odoo import models, fields, api

class LibraryChangeStatusWizard(models.TransientModel):
    _name = "library.change.status.wizard"
    _description = "Change Status Wizard"

    new_status = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('lost', 'Lost'),
        ('archived', 'Archived')
    ], string="New Status", required=True)
    
    reason = fields.Char(string="Reason")

    def action_update_status(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        books = self.env['library.books'].browse(active_ids)
        
        # We perform the state update
        books.write({'state': self.new_status})
        
        # Optional: Log the reason in the chatter if 'reason' is provided
        if self.reason:
            for book in books:
                book.message_post(body=f"Status changed to {dict(self._fields['new_status'].selection).get(self.new_status)} by Wizard. Reason: {self.reason}")
        
        return {'type': 'ir.actions.act_window_close'}

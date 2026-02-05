from odoo import http
from odoo.http import request
import json
from odoo import fields

class BorrowingApi(http.Controller):

    @http.route("/library/borrow/create", type="json", auth="none", methods=["POST"], csrf=False)
    def create_borrowing(self):
        try:
            data = json.loads(request.httprequest.data.decode())
            member_id = data.get('member_id')
            book_ids = data.get('book_ids', [])
            
            if not member_id or not book_ids:
                return {"error": "Member ID and Book IDs are required"}
            
            borrowing_vals = {
                'member_id': member_id,
                'date_expected_return': data.get('date_expected_return')
            }
            borrowing = request.env['borrowing.records'].sudo().create(borrowing_vals)
            
            for book_id in book_ids:
                request.env['borrowing.line'].sudo().create({
                    'borrowing_id': borrowing.id,
                    'book_id': book_id,
                    'date_expected_return': data.get('date_expected_return')
                })
            
            borrowing.action_confirm_borrowing()
            
            return {
                "message": "Borrowing created successfully",
                "id": borrowing.id,
                "name": borrowing.name
            }
        except Exception as e:
            return {"error": str(e)}

    @http.route("/library/borrow/return/<int:borrowing_id>", type="json", auth="none", methods=["POST"], csrf=False)
    def return_borrowing(self, borrowing_id):
        try:
            borrowing = request.env['borrowing.records'].sudo().browse(borrowing_id)
            if not borrowing.exists():
                return {"error": "Record not found"}
                
            borrowing.action_return_book()
            return {"message": "Books returned successfully"}
        except Exception as e:
            return {"error": str(e)}

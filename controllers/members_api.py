from odoo import http
from odoo.http import request
import json

class MembersApi(http.Controller):

    @http.route("/library/members/create", type="json", auth="none", methods=["POST"], csrf=False)
    def create_member(self):
        try:
            data = json.loads(request.httprequest.data.decode())
            if not data.get('name'):
                return {"error": "Name is required"}
            
            vals = {
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'street': data.get('address'),
            }
            if data.get('image'):
                vals['member_image'] = data.get('image')
                
            member = request.env['library.member'].sudo().create(vals)
            return {
                "message": "Member created successfully",
                "id": member.id,
                "card_number": member.card_number
            }
        except Exception as e:
            return {"error": str(e)}

    @http.route("/library/members/<int:member_id>", type="http", auth="none", methods=["GET"], csrf=False)
    def get_member(self, member_id):
        try:
            member = request.env['library.member'].sudo().browse(member_id)
            if not member.exists():
                return request.make_json_response({"error": "Member not found"}, status=404)
            
            return request.make_json_response({
                "id": member.id,
                "name": member.name,
                "card_number": member.card_number,
                "email": member.email,
                "membership_state": member.state,
                "active_borrowings": member.active_borrowings_count
            }, status=200)
        except Exception as e:
            return request.make_json_response({"error": str(e)}, status=400)

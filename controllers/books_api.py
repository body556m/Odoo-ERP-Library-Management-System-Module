from odoo import http
from odoo.http import request
import json


class BooksApi(http.Controller):

    @http.route("/books/api", type="http", auth="none", methods=["POST"], csrf=False)
    def create_book(self):
        rq = request.httprequest.data.decode()
        data = json.loads(rq)
        if not data.get('title'):
            return request.make_json_response({
                "create record": "what's the title of the book?"
            }, status=400)
        try:
            res = request.env['library.books'].sudo().create(data)
            if res:
                return request.make_json_response({
                    "create record": "done"
                }, status=201)
        except Exception as error:
            return request.make_json_response({
                "create record": error
            }, status=400)

    @http.route("/books/api/json", type="json", auth="none", methods=["POST"], csrf=False)
    def create_book_json(self):
        req = request.httprequest.data.decode()
        data = json.loads(req)
        res = request.env['library.books'].sudo().create(data)
        if res:
            return {
                "id": res.id,
                "title": res.title,
                "isbn": res.isbn,
                "price": res.price
            }

    @http.route("/books/api/http/<int:book_id>", type="http", auth="none", methods=["PUT"], csrf=False)
    def update_book_json(self, book_id):
        try:
            book_id = request.env['library.books'].sudo().search([('id', '=', book_id)])
            req = request.httprequest.data.decode()
            data = json.loads(req)
            book_id.write(data)
            if book_id:
                return request.make_json_response({
                    "update record": "done",
                    "id": book_id.id,
                    "title": book_id.title
                }, status=200) 
            else:
                return request.make_json_response({
                    "update record": "the book that you mentioned is not found"
                }, status=404)
        except Exception as error:
            return request.make_json_response({
                "update record": error
            }, status=400)

    @http.route("/books/api/http/<int:book_id>", type="http", auth="none", methods=["GET"], csrf=False)
    def get_book_json(self, book_id):
        try:
            book_id = request.env['library.books'].sudo().search([('id', '=', book_id)])
            if not book_id:
                return request.make_json_response({
                    "get record": "the book that you mentioned is not found"
                }, status=404)
            return request.make_json_response({
                "get record": "done",
                "id": book_id.id,
                "title": book_id.title,
                "isbn": book_id.isbn,
                "price": book_id.price
            }, status=200) 
        except Exception as error:
            return request.make_json_response({
                "get record": error
            }, status=400)

    @http.route("/books/api/http/<int:book_id>", type="http", auth="none", methods=["DELETE"], csrf=False)
    def delete_book_json(self, book_id):
        try:
            book_id = request.env['library.books'].sudo().search([('id', '=', book_id)])
            if not book_id:
                return request.make_json_response({
                    "delete record": "the book that you mentioned is not found"
                }, status=404)
            book_id.unlink()
            return request.make_json_response({
                "delete record": "done"
            }, status=200) 
        except Exception as error:
            return request.make_json_response({
                "delete record": error
            }, status=400)

    @http.route("/library/books/search", type="http", auth="none", methods=["GET"], csrf=False)
    def search_books(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            books_domain = []
            limit = 10
            page = 1
            offset = 0
            
            if params:
                limit_val = params.get('limit')
                if limit_val:
                    limit = int(limit_val[0])
                    
                offset_val = params.get('offset')
                if offset_val:
                    offset = int(offset_val[0])
                    
                page_val = params.get('page')
                if page_val:
                    page = int(page_val[0])
                    offset = (page - 1) * limit

                state_val = params.get('state')
                if state_val:
                    books_domain += [('state', '=', state_val[0])]
                    
                author_val = params.get('author_id')
                if author_val:
                    books_domain += [('author_id', '=', author_val[0])]
                    
                category_val = params.get('category_id')
                if category_val:
                    books_domain += [('category_id', '=', category_val[0])]
            
            books_obj = request.env['library.books'].sudo()
            total_count = books_obj.search_count(books_domain)
            books = books_obj.search(books_domain, limit=limit, offset=offset)
            
            if not books:
                return request.make_json_response({
                    "search record": "no books found",
                    "total_count": total_count
                }, status=404)
            
            total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
                
            return request.make_json_response({
                "search record": "done",
                "total_count": total_count,
                "limit": limit,
                "page": page,
                "total_pages": total_pages,
                "books": [
                    {
                        "id": book.id,
                        "title": book.title,
                        "isbn": book.isbn,
                        "price": book.price,
                        "author": book.author_name,
                        "category": book.category_id.name,
                        "state": book.state,
                        "copies": book.copies
                    }
                    for book in books
                ]
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                "search record": str(error)
            }, status=400)

from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter



class ExcelBooks(http.Controller):
    @http.route('/library/excel/books/<string:book_id>', type='http', auth='user')
    def download_excel_books(self, book_id):
        book_id = request.env['library.books'].browse(literal_eval(book_id))
        
        rep_file = io.BytesIO()
        workbook = xlsxwriter.Workbook(rep_file, {'in_memory': True})
        worksheet = workbook.add_worksheet('Books')
        

        header_format = workbook.add_format({'bold': True, 'bg_color': 'yellow', 'border': 1, 'align': 'center'})
        string_format = workbook.add_format({'border': 1, 'align': 'center'})
        float_format = workbook.add_format({'num_format': '##,##0.00', 'border': 1, 'align': 'center'})
        int_format = workbook.add_format({'num_format': '##,##0', 'border': 1, 'align': 'center'})


        headers = ['Title', 'Author', 'Publisher', 'Published Date', 'ISBN', 'Pages', 'Price', 'Copies', 'State']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        for row_num, book in enumerate(book_id, start=1):
            worksheet.write(row_num, 0, book.title, string_format)
            worksheet.write(row_num, 1, book.author_id.name or '', string_format)
            worksheet.write(row_num, 2, book.publisher_id.name or '', string_format)
            worksheet.write(row_num, 3, str(book.published_date) if book.published_date else '', string_format)
            worksheet.write(row_num, 4, book.isbn, string_format)
            worksheet.write(row_num, 5, book.pages, int_format)
            worksheet.write(row_num, 6, book.price, float_format)
            worksheet.write(row_num, 7, book.copies, int_format)    
            worksheet.write(row_num, 8, book.state, string_format)

        workbook.close()
        rep_file.seek(0)
        
        file_name = 'books.xlsx'
        
        return request.make_response(
            rep_file.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={file_name}')])

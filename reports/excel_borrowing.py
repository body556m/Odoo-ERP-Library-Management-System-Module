from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter

class ExcelBorrowing(http.Controller):

    @http.route('/library/excel/borrowing/<string:borrowing_ids>', type='http', auth='user')
    def download_excel_borrowing(self, borrowing_ids):
        # Parse the IDs, handling both single ID and list of IDs
        try:
            ids = literal_eval(borrowing_ids)
            if isinstance(ids, int):
                ids = [ids]
        except ValueError:
            return request.not_found()

        borrowings = request.env['borrowing.records'].browse(ids)
        if not borrowings:
            return request.not_found()
            
        rep_file = io.BytesIO()
        workbook = xlsxwriter.Workbook(rep_file, {'in_memory': True})
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        title_format = workbook.add_format({'bold': True, 'size': 14, 'align': 'center'})
        string_format = workbook.add_format({'border': 1, 'align': 'center'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1, 'align': 'center'})

        for borrowing in borrowings:
            # Sheet name limited to 31 chars
            sheet_name = borrowing.name.replace('/', '-') if borrowing.name else f'Record {borrowing.id}'
            worksheet = workbook.add_worksheet(sheet_name[:31])
            
            worksheet.merge_range('A1:E1', f'Borrowing Record: {borrowing.name}', title_format)
            
            worksheet.write(2, 0, 'Member:', header_format)
            worksheet.write(2, 1, borrowing.member_id.partner_id.name, string_format)
            worksheet.write(3, 0, 'Card #:', header_format)
            worksheet.write(3, 1, borrowing.member_id.card_number, string_format)
            
            worksheet.write(2, 3, 'Date Borrowed:', header_format)
            worksheet.write(2, 4, str(borrowing.date_borrowed), date_format)
            worksheet.write(3, 3, 'Expected Return:', header_format)
            worksheet.write(3, 4, str(borrowing.date_expected_return), date_format)
    
            headers = ['Book Title', 'ISBN', 'Status', 'Return Date']
            for col_num, header in enumerate(headers):
                worksheet.write(5, col_num, header, header_format)
    
            for row_num, line in enumerate(borrowing.borrowing_line_ids, start=6):
                worksheet.write(row_num, 0, line.book_id.title, string_format)
                worksheet.write(row_num, 1, line.book_id.isbn, string_format)
                worksheet.write(row_num, 2, line.line_state, string_format)
                worksheet.write(row_num, 3, str(line.date_returned_line) if line.date_returned_line else '-', string_format)

        workbook.close()
        rep_file.seek(0)
        
        if len(borrowings) > 1:
            file_name = 'borrowing_records.xlsx'
        else:
            file_name = f'borrowing_{borrowings[0].name}.xlsx'
        
        return request.make_response(
            rep_file.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={file_name}')])

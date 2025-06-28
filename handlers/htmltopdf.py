import tornado.web
import json
import os
import uuid
import pdfkit

class PdfConverterHandler(tornado.web.RequestHandler):
    def get(self):
        # Serve an HTML form for users to enter HTML content
        self.render("pdf_converter.html")
    def post(self):
        try:
            data = json.loads(self.request.body)
            html_content = data.get('html')
            
            if not html_content:
                self.set_status(400)
                self.write({"error": "No HTML content provided"})
                return
                
            filename = f"document_{uuid.uuid4()}.pdf"
            temp_dir = os.path.join(os.path.dirname(__file__), "..", "temp")
            os.makedirs(temp_dir, exist_ok=True)
            output_path = os.path.join(temp_dir, filename)
            
            pdfkit.from_string(html_content, output_path)
            
            # Set headers for file download
            self.set_header('Content-Type', 'application/pdf')
            self.set_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            # Stream the file to the client
            with open(output_path, 'rb') as file:
                self.write(file.read())
            
            self.finish()
            os.remove(output_path)
            
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
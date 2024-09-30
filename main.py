from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
import shutil
import re
import base64
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def generate_invoice(invoice_data, template_name):
    env = Environment(loader=FileSystemLoader(resource_path('assets')))
    template = env.get_template(template_name)
    
    rendered_html = template.render(invoice_data)
    
    template_folder = os.path.join('results', template_name.replace('.html', ''))
    os.makedirs(template_folder, exist_ok=True)
    
    logo_src = resource_path(os.path.join('assets', 'next_logo.PNG'))
    logo_dest = os.path.join(template_folder, 'next_logo.PNG')
    shutil.copy2(logo_src, logo_dest)
    
    with open(logo_src, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    rendered_html = re.sub(
        r'src="[^"]*next_logo\.PNG"',
        f'src="data:image/png;base64,{encoded_string}"',
        rendered_html
    )
    
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    pdf_filename = os.path.join(template_folder, f"invoice_{invoice_data['invoice_id']}.pdf")
    try:
        pdfkit.from_string(rendered_html, pdf_filename, configuration=config, options={'enable-local-file-access': None})
        print(f"PDF generated successfully: {pdf_filename}")
    except OSError as e:
        print(f"Error generating PDF: {e}")
        print("Saving HTML file instead.")
    
    html_filename = os.path.join(template_folder, f"invoice_{invoice_data['invoice_id']}.html")
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    print(f"HTML file saved: {html_filename}")
    
    return rendered_html

def generate_random_invoice_id():
    import random
    import string
    return ''.join(random.choice(string.digits) for _ in range(10))

def get_template_files():
    return [f for f in os.listdir('assets') if f.endswith('.html')]

invoice_data = {
    'customer_name': 'John Doe',
    'customer_address_street_housenumber': '123 Main St',
    'customer_postal_code': '1234 AB',
    'customer_city': 'Amsterdam',
    'customer_country': 'Netherlands',
    'customer_registration_number': '12345678',
    'customer_vat_number': 'NL123456789B01',
    'customer_iban': 'NL91ABNA0417164300',
    'title': 'Energy Supply Invoice',
    'invoice_id': generate_random_invoice_id(),
    'invoice_date': '2024-03-15',
    'issue_date': '2024-03-15',
    'due_date': '2024-04-14',
    'client_id': '12345678',
    'contract_id': '12345678',
    'description': 'Energy Supply - March 2024',
    'quantity': 1000,
    'amount': 500.00,
    'vat_percentage': 21,
    'subtotal': 500.00,
    'vat': 105.00,
    'total': 605.00
}

if __name__ == "__main__":
    os.makedirs('results', exist_ok=True)
    
    template_file = 'invoice_template.html'

    try:
        html = generate_invoice(invoice_data, template_file)
        print(f"Invoice generated successfully using template: {template_file}")
    except Exception as e:
        print(f"Error generating invoice using template {template_file}: {e}")

    print("Invoice generation completed.")
from markdown import markdown
import tempfile
import os
from xhtml2pdf import pisa
import datetime

srs_text = """
# Test SRS Document
## 1. Introduction
This is a bold **test**!
| Header 1 | Header 2 |
|----------|----------|
| Row 1    | Row 2    |
"""

try:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    srs_html = markdown(srs_text, extensions=['tables'])

    style_css = """
    @page {
        size: a4 portrait;
        margin: 40px;
    }

    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
    }

    h1 {
        font-size: 24px;
        border-bottom: 2px solid #333;
        padding-bottom: 5px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    table, th, td {
        border: 1px solid black;
    }
    """

    generation_date = datetime.datetime.now().strftime("%B %d, %Y")

    html_content = f"""
    <html>
    <head>
        <meta charset=\"utf-8\">
        <style>{style_css}</style>
    </head>
    <body>
        <div style="text-align: right; color: #666; font-size: 12px; border-bottom: 2px solid #333; padding-bottom: 5px; margin-bottom: 20px; font-family: Arial, sans-serif;">
            <strong>Software Requirements Specification</strong><br>
            Generated on: {generation_date}
        </div>
        {srs_html}
    </body>
    </html>
    """

    with open(path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html_content, dest=result_file)
    
    if pisa_status.err:
        raise Exception("PDF generation with xhtml2pdf failed")
    
    print("SUCCESS")
    print(path)

except Exception as e:
    import traceback
    traceback.print_exc()

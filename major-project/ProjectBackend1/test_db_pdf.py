import asyncio
import os
import tempfile
import traceback
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from markdown import markdown
from xhtml2pdf import pisa
import datetime

async def test_generation():
    # Connect to local MongoDB exactly like the app does
    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
    db = client["genai_srs"]  # Assuming this from the startup logs of user
    
    # Use the failed ID the user reported
    srs_id = "69a6e2976a942c64abca6471"
    if not ObjectId.is_valid(srs_id):
        # The user's ID is exactly 24 hex characters, so this is fine
        pass
        
    print(f"Fetching document {srs_id} from DB...")
    srs_doc = await db.srs_documents.find_one({"_id": ObjectId(srs_id)})
    
    if not srs_doc:
        print("Document not found!")
        return
        
    srs_text = srs_doc.get("srs_document", "")
    if not srs_text:
        print("SRS document is empty!")
        return
        
    print(f"Successfully fetched {len(srs_text)} chars of markdown.")
    
    try:
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        srs_html = markdown(srs_text, extensions=['tables'])

        style_css = """
        @page {
            size: a4 portrait;
            margin: 40px;
        }
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 5px; }
        h2 { font-size: 20px; margin-top: 20px; }
        h3 { font-size: 16px; }
        table { width: 100%; border-collapse: collapse; }
        table, th, td { border: 1px solid black; }
        th, td { padding: 6px; }
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
            print("Rendering PDF...")
            pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
        if pisa_status.err:
            raise Exception("PDF generation with xhtml2pdf failed")
        
        print("SUCCESS")
        print(path)
        
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())

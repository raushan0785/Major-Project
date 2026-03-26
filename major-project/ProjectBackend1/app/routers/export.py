"""SRS export routes."""

import tempfile
import os
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional
import datetime

from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/export", tags=["export"])

from fastapi import BackgroundTasks

@router.get("/{srs_id}")
async def export_srs(
    srs_id: str,
    background_tasks: BackgroundTasks,
    filename: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Export an SRS document as a PDF file.
    """
    # 1. Validate ObjectId
    if not ObjectId.is_valid(srs_id):
        raise HTTPException(status_code=400, detail="Invalid SRS ID format")

    # 2. Query Database
    srs_doc = await db.srs_documents.find_one({
        "_id": ObjectId(srs_id),
        "user_id": ObjectId(current_user["_id"])
    })

    if not srs_doc:
        raise HTTPException(status_code=404, detail="SRS not found or access denied")

    srs_text = srs_doc.get("srs_document", "")
    if not srs_text:
        raise HTTPException(status_code=500, detail="SRS document content is empty")

    # 3. Generate PDF
    try:
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd) # Close file descriptor immediately, we will write using xhtml2pdf
        
        # Localize imports so GTK/DLL errors don't crash the entire Router
        from markdown import markdown
        
        # Convert Markdown to HTML
        srs_html = markdown(srs_text, extensions=['tables'])

        # Style HTML logically
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

        h2 {
            font-size: 20px;
            margin-top: 20px;
        }

        h3 {
            font-size: 16px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }

        table, th, td {
            border: 1px solid black;
        }

        th, td {
            padding: 6px;
        }
        """

        # Add generation timestamp logic
        import datetime
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

        # Write generated HTML layout to PDF
        from xhtml2pdf import pisa
        with open(path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
        if pisa_status.err:
            raise Exception("PDF generation with xhtml2pdf failed")
        
        # Determine filename
        download_filename = filename if filename else f"srs_{srs_id}.pdf"
        if not download_filename.endswith(".pdf"):
            download_filename += ".pdf"

        # 4. Return FileResponse with background cleanup
        background_tasks.add_task(os.unlink, path)
        
        return FileResponse(
            path=path, 
            filename=download_filename, 
            media_type="application/pdf"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        if 'path' in locals() and os.path.exists(path):
            os.unlink(path)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

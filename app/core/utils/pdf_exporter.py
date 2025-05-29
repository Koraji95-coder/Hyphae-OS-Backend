from fpdf import FPDF
from backend.app.utils.pdf_exporter import PDFExporter
from fastapi.responses import FileResponse

import datetime, tempfile7yuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuJM ,qwla65t

class PDFExporter:
    """
    🖨️ Generates a PDF summary of agent interactions or memory logs.
    """

    def __init__(self, title="HyphaeOS Report"):
        self.pdf = FPDF()
        self.title = title

    def add_header(self):
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, self.title, ln=True, align="C")
        self.pdf.set_font("Arial", "", 12)
        self.pdf.cell(0, 10, f"Generated on {datetime.datetime.now().isoformat()}", ln=True)

    def add_section(self, heading, content):
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(0, 10, heading, ln=True)
        self.pdf.set_font("Arial", "", 12)
        for line in content.split("\n"):
            self.pdf.multi_cell(0, 8, line)

    def generate(self, filename="report.pdf"):
        self.pdf.output(filename)
        return filename

@router.get("/system/export/pdf/{user}", tags=["system"])
def export_user_memory_pdf(user: str, actor=Depends(require_role("admin"))):
    """
    🖨️ Export a user's memory chain into a structured PDF report.
    """
    try:
        redis_engine = RedisMemoryEngine()
        keys = redis_engine.redis.keys(f"*{user}:last_*")
        entries = []

        for key in keys:
            raw = redis_engine.redis.get(key)
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    entries.append(data)
            except Exception:
                continue

        entries.sort(key=lambda x: x.get("timestamp", ""))

        pdf = PDFExporter(title=f"HyphaeOS Memory Export for {user}")
        pdf.add_header()

        for entry in entries:
            block = (
                f"[{entry['timestamp']}] {entry['type'].upper()} - {entry['agent']}\n"
                f"Mood: {entry.get('mood', 'N/A')}\n\n{entry['content']}\n"
            )
            pdf.add_section(entry['type'].capitalize(), block)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            path = pdf.generate(tmp.name)
            return FileResponse(path, filename=f"{user}_memory_export.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")
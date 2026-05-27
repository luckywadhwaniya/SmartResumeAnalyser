from xhtml2pdf import pisa
import io

def create_ats_pdf(tailored_data: dict) -> bytes:
    """Takes JSON resume data and converts it into a formatted PDF byte stream."""
    
    # We use a clean, minimalist HTML template which ATS systems love
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ margin: 1in; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #111; line-height: 1.4; }}
            h1 {{ color: #111; text-align: center; border-bottom: 2px solid #a855f7; padding-bottom: 5px; font-size: 24px; text-transform: uppercase; }}
            h2 {{ color: #a855f7; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #ccc; text-transform: uppercase; padding-bottom: 2px; }}
            h3 {{ font-size: 12px; margin-bottom: 2px; margin-top: 10px; }}
            p {{ font-size: 11px; margin: 5px 0; }}
            ul {{ font-size: 11px; margin-top: 5px; margin-bottom: 10px; }}
            li {{ margin-bottom: 4px; }}
            .summary {{ font-style: italic; }}
            .skills {{ font-weight: bold; color: #333; }}
        </style>
    </head>
    <body>
        <h1>Tailored Professional Resume</h1>
        
        <h2>Professional Summary</h2>
        <p class="summary">{tailored_data.get('tailored_summary', '')}</p>
        
        <h2>Core Competencies</h2>
        <p class="skills">{', '.join(tailored_data.get('tailored_skills', []))}</p>
        
        <h2>Professional Experience</h2>
    """
    
    # Dynamically generate the experience section
    for exp in tailored_data.get('experience', []):
        html_content += f"""
        <h3>{exp.get('job_title', 'Role')} | {exp.get('company', 'Company')}</h3>
        <ul>
        """
        for bullet in exp.get('tailored_bullets', []):
            html_content += f"<li>{bullet}</li>"
        html_content += "</ul>"
        
    html_content += """
    </body>
    </html>
    """
    
    # Convert HTML to PDF in memory
    result_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=result_file)
    
    if pisa_status.err:
        raise Exception("Failed to generate PDF document.")
        
    result_file.seek(0)
    return result_file.read()
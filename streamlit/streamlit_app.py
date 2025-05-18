import streamlit as st
import webbrowser
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# Set page config with dark theme
st.set_page_config(
    page_title="VulneraX Security Scanner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode styling
st.markdown("""
<style>
/* Global dark theme */
.stApp {
    background-color: #202124;
    color: #e8eaed;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Main heading */
.animated-heading {
    font-size: 3.5rem;
    font-weight: 500;
    text-align: center;
    color: #8ab4f8;
    margin: 2rem auto;
    padding: 1rem;
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    border-right: 3px solid #8ab4f8;
    animation: typewriter 4s steps(35) 1s forwards, blink 0.75s step-end;
    font-family: 'Google Sans', sans-serif;
}

/* Button styling */
.stButton>button {
    width: 50%;
    background-color: #8ab4f8;
    color: #202124;
    font-size: 1.1rem;
    padding: 0.8rem;
    border-radius: 4px;
    border: none;
    margin: 1rem auto;
    display: block;
    font-family: 'Google Sans', sans-serif;
    font-weight: 500;
    text-transform: none;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background-color: #93bbf9;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

/* Report content styling */
.report-content {
    background-color: #292a2d;
    padding: 2rem;
    border-radius: 8px;
    margin: 1rem auto;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    white-space: pre-wrap;
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    line-height: 1.6;
    max-height: 600px;
    overflow-y: auto;
    color: #e8eaed;
    border: 1px solid #3c4043;
}

/* Download button styling */
.stDownloadButton>button {
    background-color: #3c4043;
    color: #e8eaed;
    border: 1px solid #5f6368;
    font-family: 'Google Sans', sans-serif;
    font-weight: 500;
}

.stDownloadButton>button:hover {
    background-color: #5f6368;
}

/* Animation */
@keyframes typewriter {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes blink {
    from, to { border-color: transparent }
    50% { border-color: #8ab4f8 }
}

/* Error message styling */
.stAlert {
    background-color: #3c4043;
    color: #e8eaed;
    border: 1px solid #5f6368;
}
</style>
""", unsafe_allow_html=True)

def load_report():
    try:
        with open(r'C:\Users\Alfiya Fatima\code\aventus\VulneraX\output.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error("output.txt file not found. Please make sure the file exists.")
        return None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def format_report_content(text):
    # Replace the website URL with vulnerable.com
    text = text.replace('https://vulnerable-me.vercel.app', 'https://vulnerable.com')
    
    # Split the text into lines
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Format headers
        if line.strip().endswith(':'):
            formatted_lines.append(f"**{line}**")
        # Format vulnerability types
        elif any(vuln in line for vuln in ['SQL Injection:', 'Cross-Site Scripting (XSS):', 'Path Traversal/Local File Inclusion (LFI):']):
            formatted_lines.append(f"**{line}**")
        # Format payloads
        elif line.strip().startswith('Payload:'):
            formatted_lines.append(f"`{line}`")
        # Format reasons
        elif line.strip().startswith('Reason:'):
            formatted_lines.append(f"*{line}*")
        # Format recommendations
        elif line.strip().startswith('Change') or line.strip().startswith('Implement') or line.strip().startswith('Add') or line.strip().startswith('Consider'):
            formatted_lines.append(f"• {line}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def create_pdf_report(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='Vulnerability',
        parent=styles['Heading2'],
        textColor=colors.red,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='Recommendation',
        parent=styles['Normal'],
        bulletIndent=12,
        leftIndent=36,
        spaceAfter=12
    ))
    
    # Process the text
    story = []
    lines = text.split('\n')
    
    for line in lines:
        if line.strip():
            if line.strip().endswith(':'):
                story.append(Paragraph(line, styles['Heading2']))
            elif any(vuln in line for vuln in ['SQL Injection:', 'Cross-Site Scripting (XSS):', 'Path Traversal/Local File Inclusion (LFI):']):
                story.append(Paragraph(line, styles['Vulnerability']))
            elif line.strip().startswith('Payload:'):
                story.append(Paragraph(line, styles['Code']))
            elif line.strip().startswith('Reason:'):
                story.append(Paragraph(line, styles['Italic']))
            elif line.strip().startswith('Change') or line.strip().startswith('Implement') or line.strip().startswith('Add') or line.strip().startswith('Consider'):
                story.append(Paragraph(f"• {line}", styles['Recommendation']))
            else:
                story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    # Animated Heading
    st.markdown('<div class="animated-heading">VulneraX Security Scanner</div>', unsafe_allow_html=True)
    
    # Show Report Button
    if st.button("🔍 Open Security Report", key="show_security_report"):
        # Open localhost:8000
        webbrowser.open('http://localhost:8000')
        
        # Load and display report
        report_text = load_report()
        if report_text:
            # Format and display the report content
            formatted_report = format_report_content(report_text)
            st.markdown(formatted_report)
            
            # Create PDF
            pdf_data = create_pdf_report(report_text)
            
            # Download PDF button
            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name=f"vulnerax_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()

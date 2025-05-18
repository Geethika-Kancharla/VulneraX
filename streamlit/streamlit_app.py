import streamlit as st
import webbrowser
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import markdown
from bs4 import BeautifulSoup

# Set page config with dark theme
st.set_page_config(
    page_title="VulneraX Security Scanner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for browser opening
if 'browser_opened' not in st.session_state:
    st.session_state.browser_opened = False

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

def load_report(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"{os.path.basename(file_path)} file not found. Please make sure the file exists.")
        return None
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def markdown_to_html(text):
    # Convert markdown to HTML
    html = markdown.markdown(text)
    # Parse HTML to get clean text
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def create_pdf_report(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Use existing styles and modify them
    title_style = styles['Title']
    title_style.fontSize = 24
    title_style.spaceAfter = 30
    title_style.textColor = colors.HexColor('#8ab4f8')
    
    heading1_style = styles['Heading1']
    heading1_style.fontSize = 20
    heading1_style.spaceAfter = 20
    heading1_style.textColor = colors.HexColor('#8ab4f8')
    
    heading2_style = styles['Heading2']
    heading2_style.fontSize = 16
    heading2_style.spaceAfter = 15
    heading2_style.textColor = colors.HexColor('#8ab4f8')
    
    # Create custom styles that don't exist
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
            # Convert markdown to clean text
            clean_text = markdown_to_html(line)
            
            if line.startswith('## '):
                story.append(Paragraph(clean_text, title_style))
            elif line.startswith('**') and line.endswith('**'):
                story.append(Paragraph(clean_text, heading2_style))
            elif any(vuln in line for vuln in ['SQL Injection:', 'Cross-Site Scripting (XSS):', 'Path Traversal/Local File Inclusion (LFI):']):
                story.append(Paragraph(clean_text, styles['Vulnerability']))
            elif line.strip().startswith('Payload:'):
                story.append(Paragraph(clean_text, styles['Code']))
            elif line.strip().startswith('Result:'):
                story.append(Paragraph(clean_text, styles['Italic']))
            elif line.strip().startswith('Change') or line.strip().startswith('Implement') or line.strip().startswith('Add') or line.strip().startswith('Consider'):
                story.append(Paragraph(f"• {clean_text}", styles['Recommendation']))
            elif line.strip().startswith('* '):
                story.append(Paragraph(f"• {clean_text[2:]}", styles['Normal']))
            else:
                story.append(Paragraph(clean_text, styles['Normal']))
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    # Animated Heading
    st.markdown('<div class="animated-heading">VulneraX Security Scanner</div>', unsafe_allow_html=True)
    
    # Show Report Button
    if st.button("🔍 Scan Now", key="show_security_report"):
        # Open localhost:8000
        webbrowser.open('http://localhost:8000')
        
        # Load and display reports
        report1_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'reports', 'attack_report.txt')
        report2_path = os.path.join(os.path.dirname(__file__), '..', 'agent', 'reports', 'attack_report2.txt')
        
        report1_text = load_report(report1_path)
        report2_text = load_report(report2_path)
        
        if report1_text and report2_text:
            # Display the reports content using markdown
            st.markdown("### Initial Security Assessment")
            st.markdown(report1_text)
            
            st.markdown("### Updated Security Assessment")
            st.markdown(report2_text)
            
            # Create PDFs
            pdf1_data = create_pdf_report(report1_text)
            pdf2_data = create_pdf_report(report2_text)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Initial Assessment PDF",
                    data=pdf1_data,
                    file_name=f"vulnerax_initial_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            with col2:
                st.download_button(
                    label="Download Updated Assessment PDF",
                    data=pdf2_data,
                    file_name=f"vulnerax_updated_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()

import streamlit as st
import pdfplumber
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

def parse_date(date_str):
    if date_str.lower() == 'current':
        return datetime.now()
    try:
        return datetime.strptime(date_str.strip(), '%b %Y')
    except ValueError:
        # Fallback for other formats
        return datetime(2022, 1, 1)

# Function to extract text from PDF
def extract_resume_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

# Parse the resume text into sections
def parse_resume(text):
    lines = text.split('\n')
    sections = {}
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.upper() in ['EXPERIENCE', 'EDUCATION', 'TECHNICAL SKILLS']:
            current_section = line.upper()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)
    return sections

# Main app
def main():
    st.set_page_config(page_title="Wesley Thompson - Interactive Resume", layout="wide")
    
    # Load resume data
    pdf_path = 'Wesley_Thompson_Resume_2026.pdf'
    resume_text = extract_resume_text(pdf_path)
    sections = parse_resume(resume_text)
    
    # Extract personal info
    lines = resume_text.split('\n')
    name = lines[0].strip()
    contact = lines[1].strip()
    summary = ' '.join(lines[3:6]).strip()
    
    # Sidebar for widgets
    st.sidebar.title("Navigation")
    
    # Widget 1: Section selector
    section_options = list(sections.keys()) + ['Overview']
    selected_section = st.sidebar.selectbox("Choose Section", section_options, index=0)
    
    # Widget 2: Skills filter slider
    skill_levels = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
    min_level = st.sidebar.slider("Minimum Skill Level", 1, 4, 1, format="%d")
    
    # Widget 3: Show contact checkbox
    show_contact = st.sidebar.checkbox("Show Contact Info", value=True)
    
    # Main content
    st.title(f"{name} - Interactive Resume")
    
    if show_contact:
        st.subheader("Contact Information")
        st.write(contact)
    
    st.subheader("Professional Summary")
    st.write(summary)
    
    # Display selected section
    if selected_section == 'Overview':
        for sec, content in sections.items():
            st.header(sec)
            for item in content:
                st.write(f"- {item}")
    else:
        st.header(selected_section)
        for item in sections[selected_section]:
            st.write(f"- {item}")
    
    # Skills Table
    st.header("Technical Skills")
    skills_text = ' '.join(sections.get('TECHNICAL SKILLS', []))
    skills_list = [s.strip() for s in skills_text.replace('Skills:', '').split(',')]
    # Assign levels (dummy for now, can be improved)
    skills_data = [{'Skill': skill, 'Level': 3 if 'Python' in skill or 'SQL' in skill else 2} for skill in skills_list]
    skills_df = pd.DataFrame(skills_data)
    skills_df = skills_df[skills_df['Level'] >= min_level]
    st.table(skills_df)
    
    # Skills Chart
    fig = px.bar(skills_df, x='Skill', y='Level', title='Skills Proficiency')
    st.plotly_chart(fig)
    
    # Experience Timeline (simple)
    st.header("Experience Timeline")
    # Parse experience
    exp_lines = sections.get('EXPERIENCE', [])
    experiences = []
    current_exp = {}
    months = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    for line in exp_lines:
        if re.search(months, line):
            # This is a title line with dates
            match = re.search(months, line)
            pos = match.start()
            title = line[:pos].strip().rstrip('-').strip()
            dates = line[pos:].strip()
            if current_exp:
                experiences.append(current_exp)
            current_exp = {'title': title, 'dates': dates}
        elif '|' in line:
            current_exp['company'] = line.split('|')[0].strip()
        elif line.startswith('●'):
            if 'bullets' not in current_exp:
                current_exp['bullets'] = []
            current_exp['bullets'].append(line[1:].strip())
    if current_exp:
        experiences.append(current_exp)
    
    # Correct dates if needed
    for exp in experiences:
        if 'Applied AI' in exp['title']:
            exp['dates'] = 'Jan 2026 - Current'
    
    # Create timeline
    fig_timeline = go.Figure()
    for exp in experiences:
        dates_part = exp.get('dates', '')
        if ' - ' in dates_part:
            start_str, end_str = dates_part.split(' - ', 1)
        else:
            start_str = dates_part
            end_str = 'Current'
        start_date = parse_date(start_str)
        end_date = parse_date(end_str)
        fig_timeline.add_trace(go.Scatter(x=[start_date, end_date], y=[exp['title'], exp['title']], mode='lines+markers', name=exp['title'], line=dict(width=4)))
    fig_timeline.update_layout(title='Career Timeline', xaxis_title='Time', yaxis_title='Position')
    st.plotly_chart(fig_timeline)
    
    # Download PDF
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    st.download_button(label="Download Full Resume PDF", data=pdf_bytes, file_name="Wesley_Thompson_Resume_2026.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
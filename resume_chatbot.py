import streamlit as st
import os
import pandas as pd
import re
from resume_parser import extract_text_from_pdf, extract_text_from_docx
from datetime import datetime

def extract_resume_data(raw_text):
    """Extract structured data from resume text"""
    lines = raw_text.split('\n')
    
    data = {
        'name': '',
        'email': '',
        'phone': '',
        'education': [],
        'skills': [],
        'experience': [],
        'projects': [],
        'certifications': []
    }
    
    current_section = ""
    current_project = []
    current_experience = []
    current_education = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect sections
        if line.upper() in ['EDUCATION', 'SKILLS', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS', 'WORK EXPERIENCE']:
            # Save current project/experience/education before switching sections
            if current_section == "PROJECTS" and current_project:
                data['projects'].append(' '.join(current_project))
                current_project = []
            elif current_section in ["EXPERIENCE", "WORK EXPERIENCE"] and current_experience:
                data['experience'].append(' '.join(current_experience))
                current_experience = []
            elif current_section == "EDUCATION" and current_education:
                data['education'].append(' '.join(current_education))
                current_education = []
            
            current_section = line.upper()
            continue
            
        # Extract name (first non-empty line that's not a section header)
        if not data['name'] and current_section == "" and line and not line.upper() in ['EDUCATION', 'SKILLS', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS']:
            data['name'] = line
            continue
            
        # Extract email
        if '@' in line and '.' in line:
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
            if email_match:
                data['email'] = email_match.group()
                
        # Extract phone
        phone_match = re.search(r'[\+]?[1-9][\d]{0,15}', line)
        if phone_match and len(phone_match.group()) >= 10:
            data['phone'] = phone_match.group()
            
        # Extract content based on current section
        if current_section == "EDUCATION":
            # Check if this looks like a new education entry (contains degree keywords or dates)
            if any(keyword in line.lower() for keyword in ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'school', '202', '201', '2020', '2021', '2022', '2023', '2024']):
                if current_education:  # Save previous education entry
                    data['education'].append(' '.join(current_education))
                    current_education = []
            current_education.append(line)
            
        elif current_section == "SKILLS":
            data['skills'].append(line)
            
        elif current_section in ["EXPERIENCE", "WORK EXPERIENCE"]:
            # Check if this looks like a new job entry (contains job keywords or dates)
            if any(keyword in line.lower() for keyword in ['202', '202', '201', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) or \
               any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 'intern', 'associate']):
                if current_experience:  # Save previous experience entry
                    data['experience'].append(' '.join(current_experience))
                    current_experience = []
            current_experience.append(line)
            
        elif current_section == "PROJECTS":
            # Better project detection - look for project titles or bullet points
            # Project titles usually end with '|' or ':' or are short lines
            if (line.endswith('|') or line.endswith(':') or 
                len(line) < 60 and any(keyword in line.lower() for keyword in ['project', 'app', 'website', 'system', 'platform', 'tool', 'dashboard', 'api', 'bot', 'game', 'website']) or
                line.startswith('•') or line.startswith('-') or line.startswith('*')):
                if current_project:  # Save previous project entry
                    data['projects'].append(' '.join(current_project))
                    current_project = []
            current_project.append(line)
            
        elif current_section == "CERTIFICATIONS":
            data['certifications'].append(line)
    
    # Save any remaining entries
    if current_project:
        data['projects'].append(' '.join(current_project))
    if current_experience:
        data['experience'].append(' '.join(current_experience))
    if current_education:
        data['education'].append(' '.join(current_education))
    
    return data

def get_job_description_by_title(job_title):
    """Auto-generate job description and skills based on job title"""
    job_templates = {
        "software engineer": {
            "description": """We are seeking a talented Software Engineer to join our dynamic team. You will be responsible for designing, developing, and maintaining software applications. The ideal candidate should have strong programming skills, experience with modern development frameworks, and a passion for creating high-quality code.

Key Responsibilities:
• Design and develop scalable software solutions
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews and technical discussions
• Debug and resolve software issues
• Stay updated with latest technologies and best practices""",
            "skills": ["Python", "JavaScript", "Java", "React", "Node.js", "SQL", "Git", "Docker", "AWS", "REST APIs"]
        },
        "data scientist": {
            "description": """We are looking for a Data Scientist to help us extract insights from complex data sets. You will work on machine learning models, statistical analysis, and data visualization to drive business decisions.

Key Responsibilities:
• Develop and implement machine learning models
• Perform statistical analysis and data mining
• Create data visualizations and reports
• Collaborate with stakeholders to understand business needs
• Optimize model performance and accuracy
• Present findings to technical and non-technical audiences""",
            "skills": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Data Visualization"]
        },
        "frontend developer": {
            "description": """We are seeking a Frontend Developer to create engaging user interfaces and experiences. You will work with modern web technologies to build responsive and accessible applications.

Key Responsibilities:
• Develop responsive web applications
• Implement user interface designs
• Optimize application performance
• Ensure cross-browser compatibility
• Collaborate with designers and backend developers
• Write clean, maintainable code""",
            "skills": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "TypeScript", "SASS", "Webpack", "Responsive Design"]
        },
        "backend developer": {
            "description": """We are looking for a Backend Developer to build robust server-side applications and APIs. You will work on scalable architectures and database design.

Key Responsibilities:
• Design and develop server-side applications
• Create and maintain RESTful APIs
• Design and optimize databases
• Implement security best practices
• Monitor and optimize application performance
• Collaborate with frontend developers""",
            "skills": ["Python", "Java", "Node.js", "SQL", "MongoDB", "Redis", "Docker", "AWS", "REST APIs", "Microservices"]
        },
        "devops engineer": {
            "description": """We are seeking a DevOps Engineer to streamline our development and deployment processes. You will work on infrastructure automation and CI/CD pipelines.

Key Responsibilities:
• Design and maintain CI/CD pipelines
• Manage cloud infrastructure
• Automate deployment processes
• Monitor system performance and security
• Implement infrastructure as code
• Collaborate with development teams""",
            "skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Terraform", "Linux", "Bash", "Python", "Git", "Monitoring"]
        },
        "product manager": {
            "description": """We are looking for a Product Manager to drive product strategy and development. You will work with cross-functional teams to deliver successful products.

Key Responsibilities:
• Define product strategy and roadmap
• Gather and prioritize product requirements
• Work with development teams to deliver features
• Analyze market trends and competition
• Collaborate with stakeholders
• Measure product success metrics""",
            "skills": ["Product Strategy", "Market Research", "Agile", "User Research", "Data Analysis", "SQL", "Python", "A/B Testing", "Product Analytics", "JIRA", "Confluence"]
        },
        "ui/ux designer": {
            "description": """We are seeking a UI/UX Designer to create intuitive and engaging user experiences. You will work on user research, wireframing, and visual design.

Key Responsibilities:
• Conduct user research and usability testing
• Create wireframes and prototypes
• Design user interfaces and experiences
• Collaborate with developers and product managers
• Create design systems and style guides
• Iterate designs based on user feedback""",
            "skills": ["Figma", "Adobe Creative Suite", "Sketch", "InVision", "HTML", "CSS", "JavaScript", "Prototyping", "Design Systems", "User Research", "Wireframing", "Usability Testing"]
        },
        "machine learning engineer": {
            "description": """We are looking for a Machine Learning Engineer to develop and deploy machine learning models. You will work on data preprocessing, model training, and production deployment.

Key Responsibilities:
• Develop and implement machine learning models
• Preprocess and analyze large datasets
• Deploy models to production environments
• Optimize model performance and accuracy
• Collaborate with data scientists and engineers
• Maintain and monitor ML pipelines""",
            "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "SQL", "Docker", "AWS", "MLOps", "Data Preprocessing", "Model Deployment", "Statistics", "Deep Learning"]
        },
        "cybersecurity analyst": {
            "description": """We are seeking a Cybersecurity Analyst to protect our systems and data from security threats. You will monitor security systems and respond to incidents.

Key Responsibilities:
• Monitor security systems and networks
• Investigate security incidents and threats
• Implement security controls and policies
• Conduct vulnerability assessments
• Respond to security breaches
• Maintain security documentation""",
            "skills": ["SIEM", "Wireshark", "Nmap", "Metasploit", "Python", "Linux", "Network Security", "Incident Response", "Vulnerability Assessment", "Security Tools", "Firewall Management"]
        },
        "cloud engineer": {
            "description": """We are looking for a Cloud Engineer to design and manage cloud infrastructure. You will work on cloud migration, automation, and optimization.

Key Responsibilities:
• Design and implement cloud architectures
• Manage cloud infrastructure and services
• Automate deployment and scaling processes
• Monitor cloud performance and costs
• Implement security best practices
• Support cloud migration projects""",
            "skills": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "CI/CD", "Python", "Bash", "Infrastructure as Code", "Cloud Security", "Monitoring"]
        }
    }
    
    # Find the best match for the job title
    job_title_lower = job_title.lower()
    for key, value in job_templates.items():
        if key in job_title_lower or job_title_lower in key:
            return value["description"], value["skills"]
    
    # Default template for unknown job titles
    return """We are seeking a talented professional to join our team. The ideal candidate should have relevant experience and skills in their field.

Key Responsibilities:
• Perform assigned duties and responsibilities
• Collaborate with team members
• Meet project deadlines and goals
• Continuously improve skills and knowledge
• Contribute to team success""", ["Technical Analysis", "Problem Solving", "Data Analysis", "Project Management", "System Design"]

def calculate_selection_probability(resume_data, job_requirements, gaps):
    """Calculate the probability of being selected for the job"""
    score = 100
    
    # Skills match (40% weight)
    skills_match_percentage = max(0, 100 - (len(gaps['missing_skills']) * 10))
    score -= (100 - skills_match_percentage) * 0.4
    
    # Experience quality (30% weight)
    if gaps['weak_experience']:
        score -= 20 * 0.3
    else:
        score += 10 * 0.3
    
    # Education match (15% weight)
    if gaps['education_gaps']:
        score -= 15 * 0.15
    else:
        score += 5 * 0.15
    
    # Projects quality (15% weight)
    if gaps['project_gaps']:
        score -= 15 * 0.15
    else:
        score += 5 * 0.15
    
    # Bonus for having certifications
    if resume_data['certifications']:
        score += 5
    
    return max(0, min(100, score))

def generate_honest_review(resume_data, job_requirements, gaps, selection_probability):
    """Generate an honest review of the resume"""
    review = "🔍 **Honest Resume Review:**\n\n"
    
    # Overall assessment
    if selection_probability >= 80:
        review += "🎯 **Overall Assessment: Strong Candidate**\n"
        review += "Your resume shows strong alignment with the job requirements. You have a good chance of being selected.\n\n"
    elif selection_probability >= 60:
        review += "📈 **Overall Assessment: Good Candidate**\n"
        review += "Your resume is competitive but has some areas for improvement. With some enhancements, you could be a strong candidate.\n\n"
    elif selection_probability >= 40:
        review += "⚠️ **Overall Assessment: Needs Improvement**\n"
        review += "Your resume needs significant improvements to be competitive for this position.\n\n"
    else:
        review += "❌ **Overall Assessment: Not Ready**\n"
        review += "Your resume is not well-aligned with this job. Consider applying for positions that better match your current skills.\n\n"
    
    # Strengths
    strengths = []
    if not gaps['missing_skills']:
        strengths.append("Strong skill match")
    if not gaps['weak_experience']:
        strengths.append("Good experience descriptions")
    if not gaps['project_gaps']:
        strengths.append("Relevant projects")
    if resume_data['certifications']:
        strengths.append("Professional certifications")
    
    if strengths:
        review += "✅ **Strengths:**\n"
        for strength in strengths:
            review += f"• {strength}\n"
        review += "\n"
    
    # Areas for improvement
    improvements = []
    if gaps['missing_skills']:
        improvements.append(f"Missing key skills: {', '.join(gaps['missing_skills'][:3])}")
    if gaps['weak_experience']:
        improvements.append("Experience section needs strengthening")
    if gaps['education_gaps']:
        improvements.append("Education requirements not fully met")
    if gaps['project_gaps']:
        improvements.append("Need more relevant projects")
    
    if improvements:
        review += "🔧 **Areas for Improvement:**\n"
        for improvement in improvements:
            review += f"• {improvement}\n"
        review += "\n"
    
    # Selection probability
    review += f"📊 **Selection Probability: {selection_probability:.1f}%**\n"
    if selection_probability >= 80:
        review += "🎉 High chance of being selected!"
    elif selection_probability >= 60:
        review += "👍 Good chance with some improvements"
    elif selection_probability >= 40:
        review += "⚠️ Moderate chance, needs work"
    else:
        review += "💡 Consider other opportunities or significant improvements"
    
    return review

def analyze_resume_gaps(resume_data, job_description, job_requirements):
    """Analyze gaps between resume and job requirements"""
    gaps = {
        'missing_skills': [],
        'weak_experience': [],
        'education_gaps': [],
        'project_gaps': [],
        'suggestions': []
    }
    
    # Analyze skills
    resume_skills = ' '.join(resume_data['skills']).lower()
    for skill in job_requirements.get('skills', []):
        if skill.lower() not in resume_skills:
            gaps['missing_skills'].append(skill)
    
    # Analyze experience
    if job_requirements.get('min_experience', 0) > 0:
        experience_text = ' '.join(resume_data['experience']).lower()
        experience_keywords = ['years', 'experience', 'worked', 'developed', 'managed']
        experience_indicators = sum(1 for keyword in experience_keywords if keyword in experience_text)
        
        if experience_indicators < 3:
            gaps['weak_experience'].append(f"Add more detailed work experience descriptions")
    
    # Analyze education
    education_text = ' '.join(resume_data['education']).lower()
    required_education = job_requirements.get('education_level', '').lower()
    
    if required_education == "bachelor's" and 'bachelor' not in education_text:
        gaps['education_gaps'].append("Consider adding Bachelor's degree or equivalent")
    elif required_education == "master's" and 'master' not in education_text:
        gaps['education_gaps'].append("Consider adding Master's degree or equivalent")
    
    # Analyze projects
    if len(resume_data['projects']) < 2:
        gaps['project_gaps'].append("Add more relevant projects to showcase practical skills")
    
    return gaps

def generate_improvement_suggestions(resume_data, job_description, gaps):
    """Generate personalized improvement suggestions"""
    suggestions = []
    
    # Skills suggestions
    if gaps['missing_skills']:
        suggestions.append({
            'category': 'Skills',
            'priority': 'High',
            'suggestion': f"Add these missing skills: {', '.join(gaps['missing_skills'])}",
            'action': "Consider taking online courses or adding relevant projects that demonstrate these skills"
        })
    
    # Experience suggestions
    if gaps['weak_experience']:
        suggestions.append({
            'category': 'Experience',
            'priority': 'High',
            'suggestion': "Strengthen your work experience section",
            'action': "Add quantifiable achievements, use action verbs, and include specific technologies used"
        })
    
    # Education suggestions
    if gaps['education_gaps']:
        suggestions.append({
            'category': 'Education',
            'priority': 'Medium',
            'suggestion': gaps['education_gaps'][0],
            'action': "Highlight relevant coursework or certifications that demonstrate required knowledge"
        })
    
    # Project suggestions
    if gaps['project_gaps']:
        suggestions.append({
            'category': 'Projects',
            'priority': 'Medium',
            'suggestion': "Add more relevant projects",
            'action': "Create projects that showcase the required skills and technologies"
        })
    
    # General suggestions
    if not resume_data['certifications']:
        suggestions.append({
            'category': 'Certifications',
            'priority': 'Low',
            'suggestion': "Consider adding relevant certifications",
            'action': "Look for industry-recognized certifications in your field"
        })
    
    return suggestions

def chatbot_response(user_message, resume_data, job_description, job_requirements):
    """Generate chatbot response based on user message and context"""
    
    # Analyze resume gaps
    gaps = analyze_resume_gaps(resume_data, job_description, job_requirements)
    suggestions = generate_improvement_suggestions(resume_data, job_description, gaps)
    selection_probability = calculate_selection_probability(resume_data, job_requirements, gaps)
    
    # Common user questions and responses
    if "improve" in user_message.lower() or "better" in user_message.lower():
        response = "🔍 **Resume Improvement Analysis:**\n\n"
        
        if suggestions:
            response += "**Priority Improvements:**\n"
            for suggestion in suggestions[:3]:  # Top 3 suggestions
                priority_emoji = "🔴" if suggestion['priority'] == 'High' else "🟡" if suggestion['priority'] == 'Medium' else "🟢"
                response += f"{priority_emoji} **{suggestion['category']}**: {suggestion['suggestion']}\n"
                response += f"   💡 *Action*: {suggestion['action']}\n\n"
        else:
            response += "✅ Your resume looks well-aligned with the job requirements!\n\n"
        
        return response
    
    elif "selected" in user_message.lower() or "chance" in user_message.lower() or "probability" in user_message.lower():
        honest_review = generate_honest_review(resume_data, job_requirements, gaps, selection_probability)
        return honest_review
    
    elif "honest" in user_message.lower() or "review" in user_message.lower():
        honest_review = generate_honest_review(resume_data, job_requirements, gaps, selection_probability)
        return honest_review
    
    elif "skills" in user_message.lower():
        if gaps['missing_skills']:
            response = "🎯 **Skills Analysis:**\n\n"
            response += f"**Missing Skills**: {', '.join(gaps['missing_skills'])}\n\n"
            response += "**Recommendations:**\n"
            response += "• Take online courses (Coursera, Udemy, edX)\n"
            response += "• Work on personal projects using these technologies\n"
            response += "• Add relevant certifications to your resume\n"
            response += "• Include these skills in your projects section\n"
        else:
            response = "✅ **Skills Analysis:** Your skills match well with the job requirements!"
        return response
    
    elif "experience" in user_message.lower():
        response = "💼 **Experience Analysis:**\n\n"
        if gaps['weak_experience']:
            response += "**Areas for Improvement:**\n"
            response += "• Add quantifiable achievements (e.g., 'Increased efficiency by 25%')\n"
            response += "• Use strong action verbs (Developed, Implemented, Managed)\n"
            response += "• Include specific technologies and tools used\n"
            response += "• Add metrics and results where possible\n"
        else:
            response += "✅ Your experience section looks strong!"
        return response
    
    elif "projects" in user_message.lower():
        response = "🚀 **Projects Analysis:**\n\n"
        if gaps['project_gaps']:
            response += "**Recommendations:**\n"
            response += "• Add 2-3 relevant projects that showcase required skills\n"
            response += "• Include GitHub links and live demos if available\n"
            response += "• Describe the technologies used and your role\n"
            response += "• Highlight problem-solving and technical skills\n"
        else:
            response += "✅ Your projects section looks good!"
        return response
    
    elif "help" in user_message.lower() or "what" in user_message.lower():
        response = "📊 **ResumePro Career Advisor**\n\n"
        response += "I can help you improve your resume! Ask me about:\n\n"
        response += "• **'How can I improve my resume?'** - Get overall suggestions\n"
        response += "• **'Will I be selected?'** - Check selection probability\n"
        response += "• **'Give me an honest review'** - Get detailed feedback\n"
        response += "• **'Analyze my skills'** - Check skill gaps\n"
        response += "• **'Review my experience'** - Experience section tips\n"
        response += "• **'Check my projects'** - Project section advice\n\n"
        response += "Just type your question and I'll provide personalized advice! 💡"
        return response
    
    else:
        # Default response with general tips
        response = "💡 **General Resume Tips:**\n\n"
        response += "• **Tailor your resume** to match the job description\n"
        response += "• **Use keywords** from the job posting\n"
        response += "• **Quantify achievements** with numbers and metrics\n"
        response += "• **Keep it concise** (1-2 pages maximum)\n"
        response += "• **Proofread carefully** for errors\n\n"
        response += "Ask me specific questions like 'Will I be selected?' or 'Give me an honest review' for detailed feedback! 🎯"
        return response

def process_resume_file(uploaded_file):
    """Process uploaded resume file"""
    try:
        # Create a temporary file
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_path = f"temp_{uploaded_file.name}"
        
        # Extract text based on file type
        if uploaded_file.name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_path)
        elif uploaded_file.name.endswith(".docx"):
            raw_text = extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX files.")
        
        # Clean up temporary file
        os.remove(file_path)
        
        return raw_text
        
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="ResumePro Analyzer", page_icon="📊", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stTextArea > div > div > textarea {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>📊 ResumePro Analyzer</h1><p>AI-Powered Resume Analysis & Career Guidance Platform</p></div>', unsafe_allow_html=True)

# Main layout with better proportions
col1, col2, col3 = st.columns([2, 1, 2])

# Left column - Job Description
with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📋 Job Requirements")
    
    job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer", key="job_title")
    
    # Auto-generate job description and skills based on job title
    if job_title and job_title.strip():
        auto_description, auto_skills = get_job_description_by_title(job_title)
        
        st.info("✨ Auto-generated content based on job title. You can edit below:")
        
        job_description = st.text_area(
            "Job Description",
            value=auto_description,
            height=150,
            help="Auto-generated job description. Feel free to modify it."
        )
        
        st.write("**Required Skills:**")
        skills_input = st.text_area(
            "Skills (one per line)",
            value='\n'.join(auto_skills),
            height=80,
            help="Auto-generated skills. Feel free to add or modify."
        )
    else:
        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the full job description here...",
            height=150
        )
        
        st.write("**Required Skills:**")
        skills_input = st.text_area(
            "Skills (one per line)",
            placeholder="Python\nJavaScript\nReact\nMachine Learning",
            height=80
        )
    
    col1a, col1b = st.columns(2)
    with col1a:
        min_experience = st.number_input("Min Experience (Years)", min_value=0, value=2)
    with col1b:
        education_level = st.selectbox(
            "Education Level",
            ["Any", "High School", "Associate's", "Bachelor's", "Master's", "PhD"]
        )
    st.markdown('</div>', unsafe_allow_html=True)

# Middle column - Upload and Analyze
with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📄 Resume Upload")
    
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        
        if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
            if not job_description.strip():
                st.error("Please enter a job description")
            else:
                with st.spinner("Analyzing your resume..."):
                    raw_text = process_resume_file(uploaded_file)
                    
                    if raw_text:
                        # Extract resume data
                        resume_data = extract_resume_data(raw_text)
                        
                        # Parse job requirements
                        skills = [skill.strip() for skill in re.split(r'[,\n]', skills_input) if skill.strip()]
                        job_requirements = {
                            'skills': skills,
                            'min_experience': min_experience,
                            'education_level': education_level
                        }
                        
                        # Store in session state
                        st.session_state.resume_data = resume_data
                        st.session_state.job_description = job_description
                        st.session_state.job_requirements = job_requirements
                        st.session_state.analyzed = True
                        
                        st.success("✅ Analysis complete!")
    st.markdown('</div>', unsafe_allow_html=True)

# Right column - Resume Summary
with col3:
    if 'resume_data' in st.session_state and st.session_state.analyzed:
        resume_data = st.session_state.resume_data
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Resume Summary")
        
        # Basic info in metric cards
        st.markdown(f'<div class="metric-card"><strong>Name:</strong> {resume_data["name"] or "Not found"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><strong>Email:</strong> {resume_data["email"] or "Not found"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><strong>Skills:</strong> {len(resume_data["skills"])} items</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><strong>Experience:</strong> {len(resume_data["experience"])} entries</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><strong>Projects:</strong> {len(resume_data["projects"])} projects</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><strong>Education:</strong> {len(resume_data["education"])} entries</div>', unsafe_allow_html=True)
        
        # Quick analysis
        if 'job_requirements' in st.session_state:
            gaps = analyze_resume_gaps(resume_data, st.session_state.job_description, st.session_state.job_requirements)
            selection_probability = calculate_selection_probability(resume_data, st.session_state.job_requirements, gaps)
            
            st.markdown("---")
            st.subheader("🔍 Quick Analysis")
            
            # Selection probability with better styling
            if selection_probability >= 80:
                st.markdown(f'<div style="background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;"><strong>🎯 Selection Probability: {selection_probability:.1f}%</strong><br>Strong Candidate!</div>', unsafe_allow_html=True)
            elif selection_probability >= 60:
                st.markdown(f'<div style="background: #d1ecf1; padding: 1rem; border-radius: 8px; border-left: 4px solid #17a2b8;"><strong>📈 Selection Probability: {selection_probability:.1f}%</strong><br>Good Candidate</div>', unsafe_allow_html=True)
            elif selection_probability >= 40:
                st.markdown(f'<div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;"><strong>⚠️ Selection Probability: {selection_probability:.1f}%</strong><br>Needs Improvement</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background: #f8d7da; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545;"><strong>❌ Selection Probability: {selection_probability:.1f}%</strong><br>Not Ready</div>', unsafe_allow_html=True)
            
            # Skills analysis
            if gaps['missing_skills']:
                st.warning(f"Missing skills: {', '.join(gaps['missing_skills'][:3])}")
            else:
                st.success("✅ Skills match well!")
        st.markdown('</div>', unsafe_allow_html=True)

# Full width sections below
st.markdown("---")

# Projects and Education Details
if 'resume_data' in st.session_state and st.session_state.analyzed:
    resume_data = st.session_state.resume_data
    
    col_details1, col_details2 = st.columns(2)
    
    with col_details1:
        if resume_data['projects']:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🚀 Projects Details")
            for i, project in enumerate(resume_data['projects'][:3], 1):
                with st.expander(f"Project {i}: {project[:40]}..."):
                    st.write(project)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col_details2:
        if resume_data['education']:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🎓 Education Details")
            for i, education in enumerate(resume_data['education'], 1):
                with st.expander(f"Education {i}: {education[:40]}..."):
                    st.write(education)
            st.markdown('</div>', unsafe_allow_html=True)

# Chatbot interface
if 'analyzed' in st.session_state and st.session_state.analyzed:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.subheader("💬 Chat with ResumePro Advisor")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hi! I'm your ResumePro Career Advisor. I've analyzed your resume against the job description. Ask me anything about improving your resume! Try asking:\n\n• 'How can I improve my resume?'\n• 'Analyze my skills'\n• 'Review my experience'\n• 'What's missing?'"
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about improving your resume..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = chatbot_response(
                prompt,
                st.session_state.resume_data,
                st.session_state.job_description,
                st.session_state.job_requirements
            )
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.info("👆 Please upload your resume and enter a job description to start chatting with ResumePro Advisor!")
    st.markdown('</div>', unsafe_allow_html=True)

# Instructions in a subtle footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>How to use:</strong> Upload resume → Enter job details → Analyze → Chat with assistant<br>
    <strong>Example questions:</strong> "How can I improve my resume?" • "Will I be selected?" • "Give me an honest review"
</div>
""", unsafe_allow_html=True)

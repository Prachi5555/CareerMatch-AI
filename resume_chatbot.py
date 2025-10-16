import streamlit as st
import os
import pandas as pd
import re
from resume_parser import extract_text_from_pdf, extract_text_from_docx
# from free_ai_analyzer import FreeAIAnalyzer  # Temporarily disabled
from datetime import datetime, date

# Import database modules
from auth import (
    register_user, login_user, logout_user,
    get_user_profile, update_user_profile, check_authentication
)
from resume_manager import (
    save_resume, get_user_resumes, save_analysis,
    get_analysis_history, get_resume_improvement_trends
)
from job_tracker import (
    add_job_application, get_user_applications,
    update_application_status, get_application_statistics
)

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
            # Detect new project: Look for project titles (short lines without bullet points)
            # or lines that end with | or : which typically indicate project names
            is_new_project = False
            
            # Check if it's a project title (not a bullet point)
            if not (line.startswith('•') or line.startswith('-') or line.startswith('*') or line.startswith('○')):
                # Check if it looks like a title (ends with | or :, or contains "Project" keyword)
                if (line.endswith('|') or line.endswith(':') or 
                    ('project' in line.lower() and len(line) < 80)):
                    is_new_project = True
            
            if is_new_project and current_project:
                # Save previous project
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
    """Generate enhanced chatbot response with AI features"""
    
    # Initialize AI analyzer
    # if 'ai_analyzer' not in st.session_state:
    #     st.session_state.ai_analyzer = FreeAIAnalyzer()  # Temporarily disabled
    
    # Analyze resume gaps
    gaps = analyze_resume_gaps(resume_data, job_description, job_requirements)
    suggestions = generate_improvement_suggestions(resume_data, job_description, gaps)
    selection_probability = calculate_selection_probability(resume_data, job_requirements, gaps)
    
    # Get AI-powered analysis
    # ai_analysis = st.session_state.ai_analyzer.advanced_resume_analysis(
    #     ' '.join([str(v) for v in resume_data.values() if isinstance(v, (str, list))]),
    #     job_description
    # )
    ai_analysis = {'similarity_score': 0, 'missing_keywords': [], 'strengths': [], 'improvements': []}
    
    # Try AI-powered response first (Temporarily disabled)
    # try:
    #     ai_response = st.session_state.ai_analyzer.enhanced_chatbot_response(
    #         user_message, resume_data, job_requirements
    #     )
    #     
    #     # Add AI insights
    #     ai_insights = st.session_state.ai_analyzer.generate_ai_insights(resume_data, job_requirements)
    #     
    #     # Combine AI response with insights
    #     enhanced_response = f"{ai_response}\n\n"
    #     if ai_insights:
    #         enhanced_response += "🎯 **AI Insights:**\n"
    #         for insight in ai_insights[:3]:
    #             enhanced_response += f"• {insight}\n"
    #     
    #     return enhanced_response
    #     
    # except Exception as e:
    #     st.warning(f"AI response failed: {str(e)}")
    #     # Fallback to original logic
    
    # Common user questions and responses (fallback)
    if "improve" in user_message.lower() or "better" in user_message.lower():
        response = "🔍 **Enhanced Resume Analysis:**\n\n"
        
        # Add AI analysis results
        response += f"📊 **AI Similarity Score: {ai_analysis['similarity_score']:.1f}%**\n\n"
        
        if ai_analysis['missing_keywords']:
            response += f"⚠️ **Missing Keywords:** {', '.join(ai_analysis['missing_keywords'][:5])}\n\n"
        
        if ai_analysis['strengths']:
            response += "✅ **Strengths:**\n"
            for strength in ai_analysis['strengths']:
                response += f"• {strength}\n"
            response += "\n"
        
        if ai_analysis['improvements']:
            response += "🔧 **AI Suggestions:**\n"
            for improvement in ai_analysis['improvements']:
                response += f"• {improvement}\n"
            response += "\n"
        
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
#jo user upload krta vo memory me hoti h use computr me temp file banate hai wb->write binary (binary mode me file banata hai)
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

# ============================================================================
# AUTHENTICATION CHECK
# ============================================================================
def show_login_page():
    """Show login/register page"""
    st.markdown('<div class="main-header"><h1>🔐 ResumePro AI Analyzer</h1><p>Login or Register to Continue</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state['user'] = result
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                reg_name = st.text_input("Full Name", placeholder="John Doe")
                reg_email = st.text_input("Email", placeholder="your.email@example.com")
            with col2:
                reg_phone = st.text_input("Phone (Optional)", placeholder="+1234567890")
                reg_password = st.text_input("Password", type="password")
            
            reg_submit = st.form_submit_button("Register", use_container_width=True)
            
            if reg_submit:
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in required fields (Name, Email, Password)")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register_user(reg_email, reg_password, reg_name, reg_phone)
                    if success:
                        st.success(f"✅ {message} Please login to continue.")
                    else:
                        st.error(f"❌ {message}")

# Check if user is authenticated
if not check_authentication():
    show_login_page()
    st.stop()

# User is authenticated - show logout button in sidebar
with st.sidebar:
    st.write(f"**👤 {st.session_state['user']['full_name']}**")
    st.write(f"_{st.session_state['user']['email']}_")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user(st.session_state['user']['session_token'])
        del st.session_state['user']
        st.rerun()
    st.divider()
    
    # Show user statistics
    st.subheader("📊 Your Stats")
    user_id = st.session_state['user']['user_id']
    
    # Resume stats
    resumes = get_user_resumes(user_id)
    st.metric("Resumes", len(resumes))
    
    # Job application stats
    app_stats = get_application_statistics(user_id)
    if app_stats:
        st.metric("Applications", app_stats['total_applications'])
        st.metric("Success Rate", f"{app_stats['success_rate']:.1f}%")
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("📄 My Resumes", use_container_width=True):
        st.session_state.show_resumes = True
        st.session_state.show_jobs = False
        st.rerun()
    
    if st.button("💼 Job Tracker", use_container_width=True):
        st.session_state.show_jobs = True
        st.session_state.show_resumes = False
        st.rerun()
    
    st.divider()

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
st.markdown('<div class="main-header"><h1>🤖 ResumePro AI Analyzer</h1><p>Enhanced AI-Powered Resume Analysis & Career Guidance Platform</p><p>✨ Now with Free AI Models & Advanced ML Analysis</p></div>', unsafe_allow_html=True)

# ============================================================================
# SHOW RESUME HISTORY OR JOB TRACKER IF REQUESTED
# ============================================================================
if st.session_state.get('show_resumes', False):
    st.markdown("---")
    st.header("📄 My Resume History")
    
    user_id = st.session_state['user']['user_id']
    resumes = get_user_resumes(user_id)
    
    if resumes:
        for resume in resumes:
            with st.expander(f"📄 {resume['resume_name']} - {resume['uploaded_at']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Versions", resume['version_count'])
                col2.metric("Analyses", resume['analysis_count'])
                col3.metric("Size", f"{resume['file_size'] / 1024:.1f} KB")
                
                # Show analysis history
                st.subheader("Analysis History")
                history = get_analysis_history(resume['resume_id'])
                if history:
                    history_data = []
                    for h in history:
                        history_data.append({
                            'Job Title': h['job_title'],
                            'Score': f"{h['selection_probability']:.1f}%",
                            'Date': h['analyzed_at']
                        })
                    st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)
                else:
                    st.info("No analysis history yet")
    else:
        st.info("No resumes uploaded yet. Upload your first resume below!")
    
    if st.button("❌ Close Resume History", use_container_width=True):
        st.session_state.show_resumes = False
        st.rerun()
    
    st.stop()  # Stop rendering the rest of the page

if st.session_state.get('show_jobs', False):
    st.markdown("---")
    st.header("💼 Job Application Tracker")
    
    user_id = st.session_state['user']['user_id']
    
    # Add new application form
    with st.expander("➕ Add New Job Application", expanded=False):
        with st.form("add_job_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name *")
                job_title_app = st.text_input("Job Title *")
                job_url = st.text_input("Job URL")
            with col2:
                application_date = st.date_input("Application Date", value=date.today())
                status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
                location = st.text_input("Location")
            
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Application", use_container_width=True):
                if company_name and job_title_app:
                    app_data = {
                        'company_name': company_name,
                        'job_title': job_title_app,
                        'job_url': job_url,
                        'application_date': application_date,
                        'status': status,
                        'location': location,
                        'notes': notes
                    }
                    success, app_id, msg = add_job_application(user_id, app_data)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.error("Company Name and Job Title are required")
    
    # Show statistics
    app_stats = get_application_statistics(user_id)
    if app_stats and app_stats['total_applications'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Applications", app_stats['total_applications'])
        col2.metric("Active", app_stats['active_applications'])
        col3.metric("Success Rate", f"{app_stats['success_rate']:.1f}%")
        col4.metric("Avg Days to Offer", f"{app_stats['avg_days_to_offer']:.0f}")
    
    # Show applications
    st.subheader("All Applications")
    applications = get_user_applications(user_id)
    
    if applications:
        for app in applications:
            with st.expander(f"{app['company_name']} - {app['job_title']} ({app['status']})", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Status:** {app['status']}")
                    st.write(f"**Applied:** {app['application_date']}")
                    if app['location']:
                        st.write(f"**Location:** {app['location']}")
                    if app['notes']:
                        st.write(f"**Notes:** {app['notes']}")
                
                with col2:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Applied", "Interview", "Offer", "Rejected"],
                        index=["Applied", "Interview", "Offer", "Rejected"].index(app['status'])
                        if app['status'] in ["Applied", "Interview", "Offer", "Rejected"] else 0,
                        key=f"status_{app['application_id']}"
                    )
                    
                    if st.button("Update", key=f"update_{app['application_id']}"):
                        success, msg = update_application_status(
                            app['application_id'],
                            user_id,
                            new_status
                        )
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("No job applications yet. Add your first application above!")
    
    if st.button("❌ Close Job Tracker", use_container_width=True):
        st.session_state.show_jobs = False
        st.rerun()
    
    st.stop()  # Stop rendering the rest of the page

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
    st.subheader("🤖 AI Features")
    
    # AI Features Toggle
    enable_ai = st.checkbox("Enable AI Analysis", value=True, help="Use free AI models for enhanced analysis")
    enable_ml = st.checkbox("Enable ML Scoring", value=True, help="Use machine learning for better scoring")
    
    st.markdown("---")
    st.subheader("📄 Resume Upload")
    #file upload 
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
                        
                        # Save resume to database
                        user_id = st.session_state['user']['user_id']
                        success, resume_id, msg = save_resume(
                            user_id=user_id,
                            resume_name=uploaded_file.name,
                            file_path=f"uploads/{uploaded_file.name}",
                            file_size=uploaded_file.size,
                            file_type=uploaded_file.name.split('.')[-1],
                            raw_text=raw_text,
                            extracted_data=resume_data
                        )
                        
                        if success:
                            st.session_state.current_resume_id = resume_id
                        
                        # Store in session state
                        st.session_state.resume_data = resume_data
                        st.session_state.job_description = job_description
                        st.session_state.job_requirements = job_requirements
                        st.session_state.analyzed = True
                        
                        st.success("✅ Analysis complete! Resume saved to database.")
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
            
            # Save analysis to database
            if 'current_resume_id' in st.session_state and 'analysis_saved' not in st.session_state:
                analysis_results = {
                    'selection_probability': selection_probability,
                    'missing_skills': gaps.get('missing_skills', []),
                    'strengths': gaps.get('matching_skills', []),
                    'weaknesses': gaps.get('missing_skills', []),
                    'suggestions': []
                }
                
                save_analysis(
                    resume_id=st.session_state.current_resume_id,
                    version_id=None,
                    job_title=st.session_state.get('job_title', 'Unknown'),
                    job_description=st.session_state.job_description,
                    analysis_results=analysis_results
                )
                st.session_state.analysis_saved = True
            
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
    st.subheader("🤖 Chat with AI Career Advisor")
    
    # AI Status
    if enable_ai:
        st.success("✅ AI Analysis Enabled - Enhanced responses with free AI models")
    else:
        st.info("ℹ️ Basic Analysis Mode - Standard rule-based responses")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = "🤖 Hi! I'm your AI Career Advisor powered by free AI models! I've analyzed your resume against the job description. Ask me anything about improving your resume! Try asking:\n\n• 'How can I improve my resume?'\n• 'Analyze my skills'\n• 'Review my experience'\n• 'What's missing?'\n• 'Give me AI insights'\n• 'What are trending skills?'"
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg
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

# Duplicate sections removed - they are now at the top of the page

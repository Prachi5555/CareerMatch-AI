import streamlit as st
import pandas as pd
import re
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class FreeAIAnalyzer:
    def __init__(self):
        """Initialize free AI models"""
        self.text_generator = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.stop_words = set(stopwords.words('english'))
        
    def load_ai_model(self):
        """Load free AI model"""
        try:
            with st.spinner("Loading AI model..."):
                self.text_generator = pipeline(
                    'text-generation',
                    model='gpt2',
                    max_length=150,
                    temperature=0.7,
                    do_sample=True
                )
            st.success("✅ AI model loaded successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Error loading AI model: {str(e)}")
            return False
    
    def enhanced_chatbot_response(self, user_message, resume_data, job_requirements):
        """Generate enhanced AI response using free models"""
        if not self.text_generator:
            if not self.load_ai_model():
                return self.fallback_response(user_message, resume_data, job_requirements)
        
        try:
            # Create context-aware prompt
            context = f"""
            Resume Data: {resume_data}
            Job Requirements: {job_requirements}
            User Question: {user_message}
            
            Provide helpful career advice based on the resume and job requirements:
            """
            
            # Generate AI response
            response = self.text_generator(
                context,
                max_length=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            # Extract and clean response
            ai_response = response[0]['generated_text']
            clean_response = self.clean_ai_response(ai_response, context)
            
            return clean_response
            
        except Exception as e:
            st.warning(f"AI model error: {str(e)}")
            return self.fallback_response(user_message, resume_data, job_requirements)
    
    def clean_ai_response(self, response, context):
        """Clean and format AI response"""
        # Remove the original context from response
        if context in response:
            response = response.replace(context, "").strip()
        
        # Limit response length
        if len(response) > 500:
            response = response[:500] + "..."
        
        # Add emojis and formatting
        formatted_response = f"🤖 **AI Career Advisor:**\n\n{response}\n\n💡 *Powered by free AI models*"
        
        return formatted_response
    
    def fallback_response(self, user_message, resume_data, job_requirements):
        """Fallback response when AI model fails"""
        return f"💡 **Career Advice:**\n\nBased on your resume and job requirements, here are some suggestions:\n\n• Focus on matching skills mentioned in the job description\n• Quantify your achievements with numbers\n• Add relevant projects that showcase required skills\n• Customize your resume for each application"
    
    def advanced_resume_analysis(self, resume_text, job_description):
        """Advanced resume analysis using free ML techniques"""
        try:
            # Text preprocessing
            resume_clean = self.preprocess_text(resume_text)
            job_clean = self.preprocess_text(job_description)
            
            # Vectorize texts
            texts = [resume_clean, job_clean]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Extract keywords
            resume_keywords = self.extract_keywords(resume_clean)
            job_keywords = self.extract_keywords(job_clean)
            
            # Find missing keywords
            missing_keywords = job_keywords - resume_keywords
            
            # Calculate advanced score
            base_score = similarity * 100
            keyword_penalty = len(missing_keywords) * 5
            final_score = max(0, base_score - keyword_penalty)
            
            return {
                'similarity_score': final_score,
                'missing_keywords': list(missing_keywords)[:10],
                'resume_keywords': list(resume_keywords)[:15],
                'job_keywords': list(job_keywords)[:15],
                'strengths': self.identify_strengths(resume_clean, job_clean),
                'improvements': self.suggest_improvements(missing_keywords, resume_clean)
            }
            
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return self.basic_analysis(resume_text, job_description)
    
    def preprocess_text(self, text):
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        # Simple keyword extraction
        words = text.split()
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Only words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return set([word for word, freq in sorted_words[:20]])
    
    def identify_strengths(self, resume_text, job_text):
        """Identify resume strengths"""
        strengths = []
        
        # Check for technical skills
        tech_skills = ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git']
        found_skills = [skill for skill in tech_skills if skill in resume_text]
        
        if found_skills:
            strengths.append(f"Strong technical skills: {', '.join(found_skills)}")
        
        # Check for experience indicators
        exp_indicators = ['experience', 'worked', 'developed', 'managed', 'led', 'created']
        found_exp = [exp for exp in exp_indicators if exp in resume_text]
        
        if len(found_exp) >= 3:
            strengths.append("Good experience descriptions with action verbs")
        
        # Check for projects
        if 'project' in resume_text:
            strengths.append("Project portfolio mentioned")
        
        return strengths
    
    def suggest_improvements(self, missing_keywords, resume_text):
        """Suggest improvements based on missing keywords"""
        improvements = []
        
        if missing_keywords:
            improvements.append(f"Add these missing skills: {', '.join(list(missing_keywords)[:5])}")
        
        # Check for quantified achievements
        if not re.search(r'\d+', resume_text):
            improvements.append("Add quantified achievements (numbers, percentages, metrics)")
        
        # Check for action verbs
        action_verbs = ['developed', 'implemented', 'created', 'managed', 'led', 'improved']
        found_verbs = [verb for verb in action_verbs if verb in resume_text]
        
        if len(found_verbs) < 3:
            improvements.append("Use more strong action verbs in experience descriptions")
        
        return improvements
    
    def basic_analysis(self, resume_text, job_description):
        """Basic analysis fallback"""
        return {
            'similarity_score': 70,
            'missing_keywords': ['python', 'react', 'sql'],
            'resume_keywords': ['experience', 'project', 'skills'],
            'job_keywords': ['python', 'react', 'sql', 'experience'],
            'strengths': ['Good experience section'],
            'improvements': ['Add more technical skills', 'Quantify achievements']
        }
    
    def generate_ai_insights(self, resume_data, job_requirements):
        """Generate AI-powered insights"""
        insights = []
        
        # Industry insights
        if 'software' in job_requirements.get('description', '').lower():
            insights.append("💻 **Tech Industry Insight:** Software engineering roles highly value practical projects and GitHub portfolios")
        
        if 'data' in job_requirements.get('description', '').lower():
            insights.append("📊 **Data Industry Insight:** Data roles require strong statistical knowledge and visualization skills")
        
        # Skill trends
        trending_skills = ['python', 'react', 'aws', 'docker', 'kubernetes']
        resume_skills = ' '.join(resume_data.get('skills', [])).lower()
        
        found_trending = [skill for skill in trending_skills if skill in resume_skills]
        if found_trending:
            insights.append(f"🚀 **Trending Skills:** You have {len(found_trending)} trending skills: {', '.join(found_trending)}")
        
        # Career advice
        insights.append("💡 **Career Tip:** Tailor your resume for each application by matching keywords from the job description")
        
        return insights


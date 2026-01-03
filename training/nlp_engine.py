import pandas as pd
import numpy as np
import nltk
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import os

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class NLPEngine:
    def __init__(self, model_path='training/model.pkl', vectorizer_path='training/vectorizer.pkl'):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_model()

    def clean_text(self, text):
        """
        Clean the input text (remove special characters, urls, etc.)
        """
        if not isinstance(text, str):
            return ""
        text = re.sub(r'http\S+\s*', ' ', text)  # remove URLs
        text = re.sub(r'RT|cc', ' ', text)  # remove RT and cc
        text = re.sub(r'#\S+', '', text)  # remove hashtags
        text = re.sub(r'@\S+', '  ', text)  # remove mentions
        text = re.sub(r'[^\x00-\x7f]', r' ', text) 
        text = re.sub(r'\s+', ' ', text)  # remove extra whitespace
        text = text.lower()
        return text.strip()

    def train(self, dataset_path):
        """
        Train TF-IDF vectorizer on the resume dataset
        """
        if not os.path.exists(dataset_path):
            print(f"Dataset not found at {dataset_path}")
            return False

        print("Loading dataset...")
        df = pd.read_csv(dataset_path)
        
        # Assume 'Resume_str' is the column
        if 'Resume_str' not in df.columns:
            print("Column 'Resume_str' not found in dataset")
            return False

        print("Cleaning text...")
        df['cleaned_resume'] = df['Resume_str'].apply(self.clean_text)
        
        print("Training Vectorizer...")
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(df['cleaned_resume'])
        
        print("Saving model...")
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.tfidf_matrix, self.model_path)
        print("Model saved successfully.")
        return True

    def load_model(self):
        """
        Load trained vectorizer and matrix
        """
        if os.path.exists(self.vectorizer_path) and os.path.exists(self.model_path):
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.tfidf_matrix = joblib.load(self.model_path)
            return True
        return False

    def calculate_score(self, resume_text, job_description):
        """
        Calculate cosine similarity between resume and JD
        """
        if not self.vectorizer:
            if not self.load_model():
                # If no model, try to train on the fly or fail
                # For now, return 0 if no model
                return 0.0

        clean_resume = self.clean_text(resume_text)
        clean_jd = self.clean_text(job_description)
        
        # Transform 
        resume_vec = self.vectorizer.transform([clean_resume])
        jd_vec = self.vectorizer.transform([clean_jd])
        
        # Similarity
        similarity = cosine_similarity(resume_vec, jd_vec)[0][0]
        return round(similarity * 100, 2)

nlp_engine = NLPEngine()

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

class Generate_Company_names:
    def __init__(self):
        self.names = []
        self.tickers = []
        
        with open('nasdaq', 'r') as file:
            for line in file:
                line = line.strip()

                if line:
                    if '(' in line and ')' in line:
                        name = line.split('(')[0].strip()
                        ticker = line.split('(')[1].replace(')', '').strip()
                        
                        self.names.append(name)
                        self.tickers.append(ticker)
        
        self.vectorizer = CountVectorizer(analyzer='char', ngram_range=(3, 5)).fit(self.names)
        self.names_vectorized = self.vectorizer.transform(self.names)

    def get_names(self):
        return self.names

    def ticker_exist(self, input):
        return input in self.tickers
    
    def cosine_similarity_manual(self, vector_a, vector_b):
        vector_a = vector_a.toarray().flatten()
        vector_b = vector_b.toarray().flatten()

        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0 
        
        return dot_product / (norm_a * norm_b)

    def compute_cosine_similarities(self, input_vectorized, names_vectorized):

        
        val = 0
        index = 0
        i = 0
        for name_vector in names_vectorized:
            similarity = self.cosine_similarity_manual(input_vectorized, name_vector)
            if similarity > val:
                val = similarity
                index = i
                
            i += 1
        
        return index, val


    def match(self, input, threshold=0.5):
        input_vectorized = self.vectorizer.transform([input])
        
        index, val = self.compute_cosine_similarities(input_vectorized, self.names_vectorized)
        
        if val >= threshold:
            return self.tickers[index]
        else:
            return "No match found"


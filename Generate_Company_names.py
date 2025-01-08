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
        
        self.vocabulary = self.fit(self.names)
        self.names_vectorized = self.transform(self.names)

    def n_gram(self, n1, n2, input_text):
        input_text = input_text.lower()
        ngrams = []
        for n in range(n1, n2 + 1):
            for i in range(len(input_text) - n + 1):
                ngrams.append(input_text[i:i + n])
        return ngrams

    def fit(self, texts):
        ngram_count = {}

        for text in texts:
            ngrams = self.n_gram(3, 5, text)
            for ngram in ngrams:
                if ngram in ngram_count:
                    ngram_count[ngram] += 1
                else:
                    ngram_count[ngram] = 1

        return {ngram: idx for idx, (ngram, _) in enumerate(sorted(ngram_count.items()))}

    def transform(self, texts):
        feature_matrix = np.zeros((len(texts), len(self.vocabulary)))

        for row_idx, text in enumerate(texts):
            ngrams = self.n_gram(3, 5, text)
            for ngram in ngrams:
                if ngram in self.vocabulary:
                    col_idx = self.vocabulary[ngram]
                    feature_matrix[row_idx, col_idx] += 1

        return feature_matrix

    
    def get_names(self):
        return self.names

    def ticker_exist(self, input_text):
        return input_text in self.tickers
    
    def cosine_similarity_manual(self, vector_a, vector_b):
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0 
        
        return dot_product / (norm_a * norm_b)

    def compute_cosine_similarities(self, input_vector, names_vectorized):
        val = 0
        index = 0
        for i, name_vector in enumerate(names_vectorized):
            similarity = self.cosine_similarity_manual(input_vector, name_vector)
            if similarity > val:
                val = similarity
                index = i
                
        return index, val

    def match(self, input_text, threshold=0.5):
        input_vectorized = self.transform([input_text])[0]  
        index, val = self.compute_cosine_similarities(input_vectorized, self.names_vectorized)
        
        if val >= threshold:
            return self.tickers[index]
        else:
            return "No match found"

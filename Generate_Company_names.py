from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

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

    def match(self, input, threshold=0.5):
        input_vectorized = self.vectorizer.transform([input])
        
        cosine_similarities = cosine_similarity(input_vectorized, self.names_vectorized)
        
        best_match_index = cosine_similarities.argmax()
        max_score = cosine_similarities.max()

        best_match_score = cosine_similarities[0, best_match_index]
        
        if best_match_score >= threshold:
            return self.tickers[best_match_index]
        else:
            return "No match found"


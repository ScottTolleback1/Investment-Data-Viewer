from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

class Generate_Company_names:
    def __init__(self):
        self.names = []
        self.tickers = []
        
        # Open the file that contains the company names and tickers
        with open('nasdaq', 'r') as file:
            # Read each line in the file
            for line in file:
                # Remove any leading/trailing whitespaces
                line = line.strip()

                if line:
                    if '(' in line and ')' in line:
                        name = line.split('(')[0].strip()
                        ticker = line.split('(')[1].replace(')', '').strip()
                        
                        self.names.append(name)
                        self.tickers.append(ticker)
        self.vectorizer = CountVectorizer().fit(self.names)
        self.names_vectorized = self.vectorizer.transform(self.names)


    def get_names(self):
        return self.names

    def ticker_exist(self, input):
        if input in self.tickers: return True
        else: return False
    
    def match(self, input):
        # Vectorize the input string and compare with pre-calculated vectors of company names
        input_vectorized = self.vectorizer.transform([input])
        cosine_similarities = cosine_similarity(input_vectorized, self.names_vectorized)
        
        # Find the index of the best match
        best_match_index = cosine_similarities.argmax()
        best_match = self.tickers[best_match_index]
        return best_match


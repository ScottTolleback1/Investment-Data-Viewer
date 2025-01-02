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

                # Check if the line is non-empty
                if line:
                    # Split the line into company name and ticker (by finding the opening parenthesis)
                    if '(' in line and ')' in line:
                        name = line.split('(')[0].strip()
                        ticker = line.split('(')[1].replace(')', '').strip()
                        
                        # Add the name and ticker to the respective lists
                        self.names.append(name)
                        self.tickers.append(ticker)

    def get_names(self):
        return self.names

    def get_tickers(self):
        return self.tickers


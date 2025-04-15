import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download nltk dependencies 
# punkt_tab
try: nltk.data.find('punkt_tab')
except LookupError: nltk.download('punkt_tab'.split('/')[-1])

# stopwords
try: nltk.data.find('stopwords')
except LookupError: nltk.download('stopwords'.split('/')[-1])


def tokenize_no_stopwords(text:str) -> list[str]: 
    """Takes in a text string, tokenizes the text, removes stopwords, and returns
    the list of tokens."""
    return [word for word in word_tokenize(text) if word.lower() not in stopwords.words('english') and word.isalnum()]
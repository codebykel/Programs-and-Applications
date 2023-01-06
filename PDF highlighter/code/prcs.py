import fitz
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


def extractText(dir, bar):
    bar["value"] = 0

    try:
        doc = fitz.open(dir)
    except fitz.fitz.FileNotFoundError:
        return 400

    numPages = len(doc) # Variable for calculating the progress bar

    pages = [] # Store the whole text for every page in doc
    for pageNum, page in enumerate(doc):
        pages.append(page.get_text())

        bar["value"] = (pageNum + 1/numPages) * 100
    
    return pages


def getHighlight(mode, keywords, pages, bar):
    bar["value"] = 0

    pageHighlights = {}

    if mode == "keyword":
        numPages = len(pages)
 
        for pageNum, text in enumerate(pages):
            sentences = sent_tokenize(text)
            sentenceHighlights = [] 

            # Go to each sentences  and check if one of the keyword is a subtring of a sentence.  
            for sentence in sentences:

                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        sentenceHighlights.append(sentence)
                        break
            
            # Ensure that there is a sentence in a page to highlight.
            if len(sentenceHighlights) != 0:
                pageHighlights[pageNum] = sentenceHighlights
                
            bar["value"] = (pageNum + 1 / numPages) * 100
        
    else:
        numPages = len(pages)

        for pageNum, text in enumerate(pages):
            # Tokenize text into words
            stop_words = set(stopwords.words("english"))
            words = word_tokenize(text)

            # Create a frequency table to keep the score of each word.
            freq_table = {} 
            for word in words:
                word = word.lower()
                if word in stop_words:
                    continue
                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1
            
            # Tokenize text into sentences
            sentences = sent_tokenize(text)

            # Create a dictionary to keep the score of each sentence
            sentence_value = {}
            for sentence in sentences:
                for word, freq in freq_table.items():
                    if word in sentence.lower():
                        if sentence in sentence_value:
                            sentence_value[sentence] += freq
                        else:
                            sentence_value[sentence] = freq
            
            # Sum value of all score of each sentence
            sum_values = 0
            for sentence in sentence_value:
                sum_values += sentence_value[sentence]

            try:
                # Average value of a sentence from the original text
                average = int(sum_values / len(sentence_value))
            except ZeroDivisionError:
                continue

            # Storing sentences into the page summary that will then be appended in pageHighlights.
            pageSummary = []
            for sentence in sentences:
                if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)):
                    pageSummary.append(sentence)
            
            pageHighlights[pageNum] = pageSummary
                
            bar["value"] = (pageNum + 1 / numPages) * 100
        
    return pageHighlights


def makeHighlightedPDF(mode, pageHighlights, dir, bar):

    bar["value"] = 0

    doc = fitz.open(dir)
    numPages = len(doc)

    for pageNum, page in enumerate(doc):

        # Ensure that the page number is in the pages that should be highlighted.
        if pageNum in pageHighlights:

            for highlight in pageHighlights[pageNum]:

                # Don't highlight one word
                if len(highlight.strip().split(" ")) < 2:
                    continue

                # Search for any instances of highlights in the curent page.
                textInstances = page.search_for(highlight)

                # Highlight all the instances that need to be highlighted.
                for inst in textInstances:
                    try:
                        highlightedPage = page.add_highlight_annot(inst)
                        highlightedPage.update()
                    except ValueError:
                        continue
            
            bar["value"] = (pageNum + 1 / numPages) * 100
        

    # Save the new highlighted PDF file.
    if mode == "summary":
        doc.save(f"{dir[:-5]}-summarized.pdf")
    else:
        doc.save(f"{dir[:-5]}-keywords.pdf")

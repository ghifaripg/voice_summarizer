import speech_recognition as sr
import pyttsx3 
import nltk
import sys
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.tokenize.treebank import TreebankWordDetokenizer
import time

nltk.download('punkt')
nltk.download('stopwords')

# Initialize the recognizer 
r = sr.Recognizer() 

# Function to summarize text
def text_summarizer(text, num_sentences=3):
    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text)

    # Remove stop words and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]

    # Calculate word frequency
    freq_dist = FreqDist(filtered_words)

    # Assign score to each sentence based on word frequency
    sentence_scores = {}
    for sentence in sentences:
        for word, freq in freq_dist.items():
            if word.lower() in sentence.lower():
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq
                else:
                    sentence_scores[sentence] += freq

    # Get the top N sentences with highest scores
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]

    # Detokenize the selected sentences for the final summary
    summary = TreebankWordDetokenizer().detokenize([sentence[0] for sentence in sorted_sentences])

    return summary

# Function to convert text to speech
def SpeakText(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command) 
    engine.runAndWait()

# Function to recognize speech with automatic punctuation based on pauses
def recognize_speech_with_punctuation():
    try:
        with sr.Microphone() as source:
            print("Please speak something...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source, timeout= 5)
            text = r.recognize_google(audio)
            print("You said:", text)
            
            # Analyze the duration of pauses between spoken words
            words = text.split()
            punctuated_text = ""
            previous_time = time.time()
            for word in words:
                # Calculate the duration of the pause between words
                current_time = time.time()
                pause_duration = current_time - previous_time
                
                # Add appropriate punctuation based on the pause duration
                if 0 < pause_duration < 0.5:
                    punctuated_text += ", "
                elif 0.5 <= pause_duration < 1:
                    punctuated_text += ". "
                elif 1 <= pause_duration < 1.5:
                    punctuated_text += "! "
                elif 1.5 <= pause_duration < 2:
                    punctuated_text += "? "
                
                punctuated_text += word + " "
                previous_time = current_time
            
            return punctuated_text
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
    except sr.UnknownValueError:
        print("unknown error occurred")

# Function to replace spoken punctuation with actual punctuation marks
def replace_punctuation(text):
    replacements = {
        'comma': ',',
        'dot': '.',
        'semicolon': ';',
        'colon': ':',
        'question mark': '?',
        'exclamation mark': '!',
        'dash': '-',
        'hyphen': '-',
        'underscore': '_'
    }
    for word, punctuation in replacements.items():
        text = text.replace(word, punctuation)
    return text

# Switch-case like function to handle user choices
def switch_case(choice):
    switcher = {
        '1': summarize_text,
        '2': summarize_speech,
        '3': exit_program
    }
    func = switcher.get(choice, lambda: print("Invalid choice"))
    func()

# Function to summarize text
def summarize_text():
    user_input = input("Enter the text you want to summarize:\n")
    num_sentences = int(input("Enter the number of sentences for the summary (default is 3): ") or 3)
    summary = text_summarizer(user_input, num_sentences)
    print("\nSummary:\n", summary)

# Function to summarize speech
def summarize_speech():
    # Call the function to recognize speech with automatic punctuation
    recognized_text = recognize_speech_with_punctuation()

    # Replace spoken punctuation with actual punctuation marks
    recognized_text = replace_punctuation(recognized_text)
 
    # Print recognized text and let the user choose the number of sentences for summarization
    print("Recognized Text:\n", recognized_text)
    num_sentences = int(input("Enter the number of sentences for the summary (default is 3): ") or 3)

    # Generate and print the summary
    summary = text_summarizer(recognized_text, num_sentences)
    print("\nSummary:\n", summary)

# Function to exit the program
def exit_program():
    print("Exiting...")
    sys.exit()

# Main loop
while True:
    # User input
    user_choice = input("Choose an option:\n1. Summarize text\n2. Summarize speech\n3. Exit\n")
    switch_case(user_choice)

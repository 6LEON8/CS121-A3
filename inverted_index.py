from ast import List
import os
import json
import re
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
from report import Report

nltk.download('punkt')
stemmer = PorterStemmer()

def tokenize(text):
    """Tokenize text into words (lowercase, alphanumeric only) and apply stemming."""
    words = re.findall(r'\b\w+\b', text.lower())
    stemmed_words = [stemmer.stem(word) for word in words]
    return stemmed_words

def extract_important_text(html):
    """Extracts important words from titles, headings, and bold text."""
    soup = BeautifulSoup(html, 'html.parser')
    important_text = ""

    for tag in soup.find_all(['title', 'h1', 'h2', 'h3', 'b', 'strong']):
        important_text += " " + tag.get_text()

    return important_text

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.final_index = defaultdict(list)

    def add_document(self, doc_id, text, important_text):
        """Tokenize the text and add it to the inverted index with prioritization for important words."""
        tokens = tokenize(text)
        important_tokens = tokenize(important_text)

        tf = Counter(tokens)
        
        for token, freq in tf.items():
            weight = 2 if token in important_tokens else 1  
            self.index[token].append({
                "doc_id": doc_id,
                "term_frequency": freq * weight  
            })

    def save_batch(self, output_dir, batch_num):
        file_path = os.path.join(output_dir, f"batch_{batch_num}.json")
        with open(file_path, "w") as file:
            json.dump(dict(self.index), file)

        self.index.clear()
        
    # def save_to_disk(self, file_path):
    #     """Save the inverted index to disk as a JSON file."""
    #     with open(file_path, 'w') as file:
    #         json.dump(self.index, file)



    def merge_batches(self, output_dir, new_dir):
        json_files = [indexes for indexes in os.listdir(output_dir) if indexes.endswith(".json")]
        json_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))

        for file in json_files:
            file_path = os.path.join(output_dir, file)

            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for key, item in data.items():
                    self.final_index[key].append(item)

        with open(new_dir, "w", encoding="utf-8") as output:
            json.dump(new_dir, output)

    def get_metrics(self):
        """Calculate metrics for the report."""
        num_documents = len(set(posting["doc_id"] for postings in self.final_index.values() for posting in postings))
        num_unique_tokens = len(self.final_index)
        index_size_kb = os.path.getsize("inverted_index.json") / 1024
        return {
            "num_documents": num_documents,
            "num_unique_tokens": num_unique_tokens,
            "index_size_kb": index_size_kb

        }

def main():
    dev_directory = "/Users/a../Downloads/DEV" #change this according to local file location
    output_directory = "/Users/a../Downloads/IndexBatches"
    Final_index = "/Users/a../Downloads/Final_Index"
    os.makedirs(output_directory, exist_ok=True)  # Ensure folder exists

    inverted_index = InvertedIndex()
    report = Report()
    doc_count = 0
    batch_number = 0

    for root, dirs, files in os.walk(dev_directory):
        print(f"Searching in: {root}")
        for file_name in files:
            if file_name.endswith(".json"):  
                file_path = os.path.join(root, file_name)
                print(f"Found JSON file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                    if "content" in data:
                        doc_id = file_name  
                        text = data["content"]
                        important_text = extract_important_text(text)

                        inverted_index.add_document(doc_id, text, important_text)
                        doc_count += 1
                        print(f"Indexed: {doc_id}")

                        if doc_count >= 1000:
                            inverted_index.save_batch(output_directory, batch_number)
                            batch_number += 1
                            doc_count = 0                            
                    else:
                        print(f"Skipping JSON file without 'content' field: {file_path}")

                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    if doc_count > 0:
        inverted_index.save_batch(output_directory, batch_number)
        
    inverted_index.merge_batches(output_directory, Final_index)
    metrics = inverted_index.get_metrics()
    report.add_metrics(metrics)
    report.write_to_file()

    print("Inverted index and report generated successfully!")

if __name__ == "__main__":
    main()

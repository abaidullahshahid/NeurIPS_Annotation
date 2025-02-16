import concurrent.futures
import csv
import time
import random

# Simulating the classification function (Replace with actual API call)
def classify_paper(title):
    time.sleep(random.uniform(1, 3))  # Simulating delay
    return random.choice(["Theory", "Computer Vision", "NLP", "Reinforcement Learning", "Robotics"])

# File paths
input_file = "output.csv"
output_file = "output_annotated.csv"

# Read input CSV (including all columns)
papers = []
with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # Read the header
    papers = [row for row in reader]  # Store all rows

# Add 'Category' to the header for output
header.append("Category")

# Write header to output file (overwrite if exists)
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

# Function to classify a single paper and save results
def process_paper(row):
    try:
        year, title, pdf_url, abstract = row  # Unpack row
        category = classify_paper(title)  # Get category
        print(f"Classified: {title} -> {category}")

        # Save result immediately to avoid losing progress
        with open(output_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([year, title, pdf_url, abstract, category])
    except Exception as e:
        print(f"Error processing paper: {title} - {e}")

# Use ThreadPoolExecutor to process multiple papers in parallel
MAX_WORKERS = 10  # Increase if needed
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    executor.map(process_paper, papers)

print(f"✅ Classification completed. Results saved in {output_file}")

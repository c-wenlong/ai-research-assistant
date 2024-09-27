import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import time

from mongo_utils import save_to_mongodb

def clean_parsed_sections(text):
    text = text.replace('Â', '').replace('â', '').replace('â\x80\x93', '-')  # Fix common encoding issues
    text = text.replace('\n', ' ')  # Replace newlines with space for continuous text
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space
    text = re.sub(r'([.,!?;])', r'\1 ', text)  # Ensure spacing after punctuation
    text = re.sub(r'\s+([.,!?;])', r'\1', text)  # Remove space before punctuation
    return text

def get_pmc_full_text(pmc_id, attempts=2):
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc_id}/unicode"
    for attempt in range(attempts):
        response = requests.get(url)
        if response.status_code == 200 and response.text.strip():
            return response.text
        else:
            print(f"Attempt {attempt + 1}: No full text available for PMC ID: {pmc_id}. Response: {response.text}")
    return None  # Return None after exhausting attempts

def search_open_access_articles(query, retmax):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pmc',
        'term': query,
        'retmode': 'xml',
        'retmax': retmax,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve search results. Status code: {response.status_code}")
        return None

def fetch_article_metadata(pmc_id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        'db': 'pmc',
        'id': pmc_id.replace("PMC", ""),  # Remove "PMC" prefix for the API call
        'retmode': 'xml'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch metadata for {pmc_id}. Status code: {response.status_code}")
        return None

def parse_metadata(xml_content):
    metadata = {}
    root = ET.fromstring(xml_content)
    docsum = root.find('.//DocSum')
    
    if docsum is not None:
        metadata["article_id"] = docsum.find('Id').text if docsum.find('Id') is not None else ""
        metadata["title"] = docsum.find('Item[@Name="Title"]').text if docsum.find('Item[@Name="Title"]') is not None else "No Title Available"
        # metadata["abstract"] = docsum.find('Item[@Name="Abstract"]').text if docsum.find('Item[@Name="Abstract"]') is not None else "No Abstract Available"
        metadata["authors"] = [author.text for author in docsum.findall('Item[@Name="AuthorList"]/Item[@Name="Author"]')]
        metadata["publication_date"] = docsum.find('Item[@Name="PubDate"]').text if docsum.find('Item[@Name="PubDate"]') is not None else ""
        metadata["journal_name"] = docsum.find('Item[@Name="Source"]').text if docsum.find('Item[@Name="Source"]') is not None else ""
        metadata["doi"] = docsum.find('Item[@Name="DOI"]').text if docsum.find('Item[@Name="DOI"]') is not None else "No DOI Available"
        # metadata["keywords"] = [keyword.text for keyword in docsum.findall('Item[@Name="Keyword"]')]
    else:
        print("No DocSum found in the metadata XML.")
    return metadata

def check_full_text_availability(pmc_id, attempts=3, delay=1):
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc_id}/unicode"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Full text available for {pmc_id}.")  # Debugging
        return True
    else:
        print(f"Failed to retrieve full text for {pmc_id}. Status code: {response.status_code}. Response text: {response.text}")  # Debugging
    return False

def parse_bioc_xml(xml_text):
    root = ET.fromstring(xml_text)
    sections = {
        "Abstract": "",
        "Introduction": "",
        "Methods": "",
        "Results": "",
        "Discussion": "",
        "Conclusion": "",
        "References": []
    }
    
    for passage in root.findall('.//passage'):
        section_type = passage.find('./infon[@key="section_type"]')
        passage_text = passage.find('text')
        
        if section_type is not None and passage_text is not None:
            section_type_text = section_type.text
            passage_text_content = passage_text.text or ""
            
            if "abstract" in section_type_text.lower():
                sections["Abstract"] += clean_parsed_sections(passage_text_content)
            elif "intro" in section_type_text.lower():
                sections["Introduction"] += clean_parsed_sections(passage_text_content)
            elif "method" in section_type_text.lower():
                sections["Methods"] += clean_parsed_sections(passage_text_content)
            elif "result" in section_type_text.lower():
                sections["Results"] += clean_parsed_sections(passage_text_content)
            elif "discuss" in section_type_text.lower():
                sections["Discussion"] += clean_parsed_sections(passage_text_content)
            elif "concl" in section_type_text.lower():
                sections["Conclusion"] += clean_parsed_sections(passage_text_content)

    for reference in root.findall('.//reference'):
        ref_title = reference.findtext('./title')  # Title of the reference
        ref_authors = [author.text for author in reference.findall('.//person')]  # Authors of the reference
        ref_journal = reference.findtext('./journal')  # Journal of the reference (if available)
        ref_year = reference.findtext('./year')  # Year of the reference

        # Combine reference information into a string
        ref_entry = f"{', '.join(ref_authors)} ({ref_year}). {ref_title}. {ref_journal}." if ref_authors and ref_title and ref_year else "Reference information not available."

        sections["References"].append(ref_entry)  # Add the cleaned reference entry to the references list

    return sections

# ToDo: CRAAP Test Calculation
def calculate_score(metadata):
    # Initialize score
    score = 0
    
    # Currency: Score based on publication date
    pub_date = metadata.get("publication_date")
    if pub_date:
        pub_year = int(pub_date.split()[0])  # Extract year
        current_year = datetime.now().year
        # Score: Newer articles get higher scores (lower difference)
        score += max(0, 10 - (current_year - pub_year))  # Max score of 10 for the most recent year
    
    # # Relevance: Score based on keywords
    # if metadata.get("keywords"):
    #     score += len(metadata["keywords"])  # More keywords = higher relevance

    return score

def count_filled_sections(parsed_sections):
    """Count the ratio of filled sections in the parsed content."""
    filled_count = sum(1 for content in parsed_sections.values() if content)  # Count filled sections
    total_count = len(parsed_sections)  # Total sections count
    ratio = filled_count / total_count if total_count > 0 else 0  # Calculate ratio
    return ratio

def main():
    start_time = time.time()  # Start timer for the entire script

    user_input = "microbiome"
    search_query = user_input + " [Title/Abstract] AND open access[filter]"
    
    # Step 1: Search for articles
    search_results = search_open_access_articles(search_query, retmax=5)

    if search_results:
        tree = ET.fromstring(search_results)
        id_list = tree.findall('.//Id')
        pmc_ids = [f"PMC{id_elem.text}" for id_elem in id_list]

        # Step 2: Gather metadata and check for full text availability
        articles = []
        for pmc_id in pmc_ids:
            print(f"Fetching metadata for PMC ID: {pmc_id}")
            metadata_xml = fetch_article_metadata(pmc_id)
            if metadata_xml:
                metadata = parse_metadata(metadata_xml)
                metadata['pmc_id'] = pmc_id  # Add PMC ID to metadata
                articles.append(metadata)

        # Step 3: Filter articles based on full text availability and score them
        available_articles = []
        for article in articles:
            pmc_id = article['pmc_id']
            if check_full_text_availability(pmc_id):
                article['score'] = calculate_score(article)
                available_articles.append(article)

        # Step 4: Sort articles by score (higher is better)
        available_articles.sort(key=lambda x: x['score'], reverse=True)

        # Step 5: Fetch and parse full text for available articles
        successful_fetch_count = 0  # Counter for successfully fetched full texts
        parsed_articles = []  # To store articles with their parsed sections
        
        for article in available_articles:
            pmc_id = article['pmc_id']
            print(f"Fetching full text for PMC ID: {pmc_id}")
            full_text = get_pmc_full_text(pmc_id)

            if full_text:
                try:
                    parsed_sections = parse_bioc_xml(full_text)
                    if parsed_sections:  # Only process if parsing was successful
                        filled_sections_count = count_filled_sections(parsed_sections)  # Count filled sections
                        article['filled_sections_count'] = filled_sections_count  # Add filled sections count
                        parsed_articles.append((article, parsed_sections))  # Store both article and its parsed sections
                        successful_fetch_count += 1  # Increment the success counter

                except ET.ParseError as e:
                    print(f"Failed to parse XML for PMC ID: {pmc_id}. Error: {e}")

        # Sort parsed articles based on the filled sections count
        parsed_articles.sort(key=lambda x: x[0]['filled_sections_count'], reverse=True)

        # Prepare to save the top 5 articles to MongoDB
        top_articles_to_save = []
        print("\nTop 5 Articles by Filled Sections Count:")
        for article, sections in parsed_articles[:5]:  # Get top 5
            # print(f"\nTitle: {article['title']}")
            # # print("Abstract:", article["abstract"])
            # print("Authors:", article["authors"])
            # print("Publication Date:", article["publication_date"])
            # print("Journal Name:", article["journal_name"])
            # print("DOI:", article["doi"])
            # # print("Keywords:", article["keywords"])
            # print("Score:", article.get('score', 'No Score'))
            # print("Filled Sections Count:", article['filled_sections_count'])  # Print filled sections count
            
            # Prepare the document to save
            document = {
                "pmc_id": article['pmc_id'],
                "article_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article['pmc_id']}/",
                "title": article['title'],
                # "abstract": article["abstract"],
                "authors": article["authors"],
                "publication_date": article["publication_date"],
                "journal_name": article["journal_name"],
                "doi": article["doi"],
                # "keywords": article["keywords"],
                "score": article.get('score', 'No Score'),
                # "filled_sections_count": article['filled_sections_count'],
                "introduction": sections.get("Introduction", 'Section not available'),
                "methods": sections.get("Methods", 'Section not available'),
                "results": sections.get("Results", 'Section not available'),
                "discussion": sections.get("Discussion", 'Section not available'),
                "conclusion": sections.get("Conclusion", 'Section not available'),
                "references": sections.get("References", 'Section not available')
            }
            top_articles_to_save.append(document)  # Collect documents for batch insertion
            print(document)

        # Save to MongoDB in bulk
        if top_articles_to_save:
            save_to_mongodb(top_articles_to_save, "trial_gut_microbiome")  # Save to MongoDB using a batch insert

        end_time = time.time()  # End timer for the entire script
        print(f"\nTotal time taken for the script to run: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
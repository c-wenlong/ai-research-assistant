import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import time
import openai
from dotenv import load_dotenv
import os
from openai import OpenAI
from datetime import datetime

from .gap_analysis import perform_gap_analysis
from .mongo_utils import save_to_mongodb

load_dotenv()

NCBI_API_KEY = os.getenv("NCBI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_parsed_sections(text):
    text = text.replace('Â', '').replace('â', '').replace('â\x80\x93', '-')  # Fix common encoding issues
    text = text.replace('\n', ' ')  # Replace newlines with space for continuous text
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space
    text = re.sub(r'([.,!?;])', r'\1 ', text)  # Ensure spacing after punctuation
    text = re.sub(r'\s+([.,!?;])', r'\1', text)  # Remove space before punctuation
    return text

async def fetch_full_text(session, pmc_id):
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc_id}/unicode"
    for attempt in range(5):  # Retry up to 5 times
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 429:  # Rate limit exceeded
                wait_time = 2 ** attempt
                print(f"Rate limit exceeded for {pmc_id}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue
            else:
                print(f"Failed to retrieve full text for {pmc_id}. Status: {response.status}")
                return None
    return None

async def search_open_access_articles(session, query, retmax):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pmc',
        'term': query,
        'retmode': 'xml',
        'retmax': retmax,
        'api_key': NCBI_API_KEY
    }
    async with session.get(url, params=params) as response:
        if response.status == 200:
            return await response.read()
        print(f"Failed to retrieve search results. Status code: {response.status}")
        return None


async def fetch_article_metadata(session, pmc_id, retries=3, delay=0.5):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        'db': 'pmc',
        'id': pmc_id.replace("PMC", ""),  # Remove "PMC" prefix for the API call
        'retmode': 'xml',
        'api_key': NCBI_API_KEY
    }
    for attempt in range(retries):
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 429:
                print(f"Rate limit exceeded for {pmc_id}. Retrying (attempt {attempt + 1})...")
                await asyncio.sleep(delay)
                delay *= 2  # Increase delay for next attempt
    print(f"Failed to fetch metadata for {pmc_id}. Status code: {response.status}")
    return None

def parse_metadata(xml_content):
    metadata = {}
    root = ET.fromstring(xml_content)
    docsum = root.find('.//DocSum')
    
    if docsum is not None:
        metadata["article_id"] = docsum.find('Id').text if docsum.find('Id') is not None else ""
        metadata["title"] = docsum.find('Item[@Name="Title"]').text if docsum.find('Item[@Name="Title"]') is not None else "No Title Available"
        metadata["authors"] = [author.text for author in docsum.findall('Item[@Name="AuthorList"]/Item[@Name="Author"]')]
        metadata["publication_date"] = docsum.find('Item[@Name="PubDate"]').text if docsum.find('Item[@Name="PubDate"]') is not None else ""
        metadata["journal_name"] = docsum.find('Item[@Name="Source"]').text if docsum.find('Item[@Name="Source"]') is not None else ""
        metadata["doi"] = docsum.find('Item[@Name="DOI"]').text if docsum.find('Item[@Name="DOI"]') is not None else "No DOI Available"
    return metadata

async def check_full_text_availability(session, pmc_id):
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc_id}/unicode"
    async with session.get(url) as response:
        return response.status == 200

async def summarize_sections(article):
    sections_to_summarize = ['introduction', 'abstract', 'methods', 'results', 'discussion', 'conclusion']
    summaries = {}

    for section in sections_to_summarize:
        if section in article:
            # Prompt designed for concise, well-formatted summarization for table display
            prompt = (
                f"Summarize the {section} section of the scientific research article below in no more than 2-3 sentences in a concise way. "
                "Avoid unnecessary numbers, percentages, or statistical data unless they are critical to understanding the results. "
                "Focus only on key points, avoiding fillers or redundant phrasing like 'this study' and numbers can represent numerically and you MUST AVOID extra words or punctuation or SQUARE BRACKETS in the front and end of sentence that do not add any meaning. "
                "Ensure the summary is concise and suitable for presentation in a table. "
                f"Here is the content:\n\n{article[section]}\n\n"
                "Return the summary in the following format:\n"
                f"[Summary here]"
            )

            # Call the synchronous function in a separate thread
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a research summarizing assistant who generates concise, formatted summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1100  # Set an appropriate limit for concise summaries
            )

            # Update this line to correctly access the response content
            summaries[section] = response.choices[0].message.content.strip()

    return summaries

def parse_bioc_xml(xml_text):
    root = ET.fromstring(xml_text)
    sections = {
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "discussion": "",
        "conclusion": ""
    }
    
    for passage in root.findall('.//passage'):
        section_type = passage.find('./infon[@key="section_type"]')
        passage_text = passage.find('text')
        
        if section_type is not None and passage_text is not None:
            section_type_text = section_type.text
            passage_text_content = passage_text.text or ""
            
            if "abstract" in section_type_text.lower():
                sections["abstract"] += clean_parsed_sections(passage_text_content)
            elif "intro" in section_type_text.lower():
                sections["introduction"] += clean_parsed_sections(passage_text_content)
            elif "method" in section_type_text.lower():
                sections["methods"] += clean_parsed_sections(passage_text_content)
            elif "result" in section_type_text.lower():
                sections["results"] += clean_parsed_sections(passage_text_content)
            elif "discuss" in section_type_text.lower():
                sections["discussion"] += clean_parsed_sections(passage_text_content)
            elif "concl" in section_type_text.lower():
                sections["conclusion"] += clean_parsed_sections(passage_text_content)

    return sections

def calculate_score(metadata):
    score = 0
    pub_date = metadata.get("publication_date")
    
    if pub_date:
        # Update the date parsing to match the provided format
        pub_date = datetime.strptime(pub_date, "%Y %b %d")
        current_date = datetime.now()
        
        # Calculate the difference in days between the current date and the publication date
        delta_days = (current_date - pub_date).days
        
        # Score based on recency: the more recent, the higher the score
        # Assuming we want to score up to 10 points for the most recent papers
        # Score decreases linearly over time (e.g., 1 point for each month or 30 days)
        score = max(0, 10 - (delta_days // 30))  # Score reduces by 1 for each month older
        
    return score

def count_filled_sections(parsed_sections):
    filled_count = sum(1 for content in parsed_sections.values() if content)
    total_count = len(parsed_sections)
    return filled_count / total_count if total_count > 0 else 0

async def main(user_input):
    start_time = time.time()  # Start timer for the entire script
    # user_input = "microbiome"
    search_query = user_input + " [Title/Abstract] AND open access[filter]"

    timeout = aiohttp.ClientTimeout(total=60)  # Extend timeout to 60 seconds
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Step 1: Search for articles
        search_results = await search_open_access_articles(session, search_query, retmax=20)

        if search_results:
            tree = ET.fromstring(search_results)
            id_list = tree.findall('.//Id')
            pmc_ids = [f"PMC{id_elem.text}" for id_elem in id_list]

            articles = []

            # Step 2: Gather metadata and check for full text availability
            tasks = [fetch_article_metadata(session, pmc_id) for pmc_id in pmc_ids]
            metadata_results = await asyncio.gather(*tasks)

            for pmc_id, metadata_xml in zip(pmc_ids, metadata_results):
                if metadata_xml:
                    metadata = parse_metadata(metadata_xml)
                    metadata['pmc_id'] = pmc_id
                    articles.append(metadata)

            # Step 3: Check full text availability concurrently
            available_articles = []
            tasks = [check_full_text_availability(session, article['pmc_id']) for article in articles]
            availability_results = await asyncio.gather(*tasks)

            for article, is_available in zip(articles, availability_results):
                if is_available:
                    article['score'] = calculate_score(article)
                    available_articles.append(article)

            # Step 4: Sort articles by score (higher is better)
            available_articles.sort(key=lambda x: x['score'], reverse=True)

            # Step : Fetch and parse full text for available articles concurrently
            parsed_articles = []
            tasks = [fetch_full_text(session, article['pmc_id']) for article in available_articles]
            full_text_results = await asyncio.gather(*tasks)

            for article, full_text in zip(available_articles, full_text_results):
                if full_text:
                    try:
                        parsed_sections = parse_bioc_xml(full_text)
                        filled_sections_count = count_filled_sections(parsed_sections)
                        article.update(parsed_sections)
                        article['filled_sections_count'] = filled_sections_count
                        article["article_url"] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article['pmc_id']}/"
                        parsed_articles.append(article)
                    except Exception as e:
                        print(f"Error parsing full text for {article['pmc_id']}: {e}")

            # Step 6: Save only the top 5 parsed articles to MongoDB
            parsed_articles.sort(key=lambda x: (x['filled_sections_count'], x['score']), reverse=True)
            top_5_articles = parsed_articles[:5]  # Get only the top 5 articles
            save_to_mongodb(top_5_articles, 'raw_fields_article')

            # Step 7: Summarize relevant sections and save to a new collection
            summaries = []
            tasks = [summarize_sections(article) for article in top_5_articles]
            summary_results = await asyncio.gather(*tasks)

            for article, summary in zip(top_5_articles, summary_results):
                article.update(summary)  # Add summaries to the article
                summaries.append(article)

            save_to_mongodb(summaries, 'summarized_fields_article')

            # Step 8: Perform gap analysis
            gaps = await perform_gap_analysis(summaries, user_input)
            
            if gaps and isinstance(gaps, dict) and 'analysis' in gaps and gaps['analysis']:
                if isinstance(gaps['analysis'], list) and len(gaps['analysis']) > 0:
                    for gap in gaps['analysis']:
                        try:
                            await save_to_mongodb([gap], 'gap_individual_articles')
                        except Exception as e:
                            print(f"Error saving gap analysis: {e}")

                # Handle comparison section
                if 'comparison_section' in gaps and gaps['comparison_section']:
                    # Check if the comparison section is a dictionary
                    comparison_data = {
                        'commonalities': gaps['comparison_section'].get('commonalities', []),
                        'contrasts': gaps['comparison_section'].get('contrasts', []),
                        'emerging_trends': gaps['comparison_section'].get('emerging_trends', [])
                    }
                    try:
                        await save_to_mongodb([comparison_data], 'gap_comparison_section')  # Wrap in list
                    except Exception as e:
                        print(f"Error saving comparison section item: {e}")
                    else:
                        print("Comparison section is not a dictionary.")
            else:
                print("No valid gaps to save.")

            end_time = time.time()  # End timer for the entire script
            print(f"\nTotal time taken for the script to run: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
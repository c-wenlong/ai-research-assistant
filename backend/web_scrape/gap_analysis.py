import asyncio
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
import json
import re

def extract_json_from_response(response_text):
    """
    Extracts JSON from a given response text. The JSON must be enclosed
    in ```json ... ``` markdown.
    """
    # Define a regex pattern to find the JSON code block
    pattern = r'```json\s*([\s\S]*?)\s*```'
    match = re.search(pattern, response_text)

    if match:
        json_code = match.group(1)  # Capture only the content inside the block
        return json_code.strip()  # Remove any leading/trailing whitespace
    else:
        return None


gap_analysis_prompt_template = ChatPromptTemplate(
    messages=[
        ("system", "You are an expert research analyst assistant that performs gap analysis on research articles."),
        ("human", 
            "Analyze the following summaries of recent research articles in the field of {search_query}. "
            "Identify any gaps in the research, and suggest areas that need further exploration or study. You MUST explain with MORE WORDS to explain better."
            "Additionally, categorize the gaps into the following categories:\n"
            "- Methodological\n"
            "- Conceptual\n"
            "- Evidence\n"
            "- Practical Knowledge\n"
            "- Empirical\n"
            "- Theoretical\n"
            "- Population Gap\n\n"
            "For each gap, quantify how many articles mention it, and provide a detailed summary table with:\n"
            "- Article Titles\n"
            "- Unique Gaps for Each Article\n"
            "- Recommendations for Further Research\n"
            "- Contextual Examples (e.g., mention the specific demographic groups missing, environmental factors not included, specific microbiome taxa absent, etc.)\n\n"
            "When analyzing common gaps, provide specific examples from the articles that illustrate the limitations. For instance, if a study mentions a lack of species-level resolution, specify the taxa that need further investigation."
            "Also, indicate what specific population groups (such as non-European ancestries, indigenous groups, different age groups) should be targeted in future studies.\n"
            "Additionally, compare the articles where applicable to highlight methodological or conceptual gaps that might not be immediately obvious.\n\n"
            "Enhance your recommendations by detailing the following:\n"
            "- For methodological gaps, describe alternate techniques or improvements (e.g., exploring ensemble models, combining unsupervised and supervised learning).\n"
            "- For conceptual gaps, discuss interdisciplinary approaches or frameworks that could bridge ideas from different fields.\n"
            "- For empirical gaps, suggest specific types of empirical data or new data sources to explore.\n"
            "- For evidence gaps, explain what kind of evidence is missing and why it’s crucial for the field.\n"
            "- For practical knowledge gaps, propose applied research directions or collaborations with industry.\n"
            "- For population gaps, specify underrepresented groups and their relevance to the research field.\n"
            "- For theoretical gaps, discuss potential new theories or modifications of existing theories that would address these gaps.\n\n"
            "Present your findings in the following JSON format and provide output ONLY in JSON with nothing extra\n"
            "{{\n"
            '  "analysis": [\n'
            '    {{\n'
            '      "article_title": "Title of the article",\n'
            '      "unique_gaps": ["Unique gap 1 with specific examples", "Unique gap 2 with detailed context"],\n'
            '      "recommendations": ["Detailed recommendation 1", "Detailed recommendation 2"],\n'
            '      "gap_categories": {{\n'
            '        "methodological": ["Detailed methodological gap with example"],\n'
            '        "conceptual": ["Conceptual gap with context"],\n'
            '        "empirical": ["Specific empirical gap and its importance"],\n'
            '        "evidence": ["Evidence gap, why it matters, and what is missing"],\n'
            '        "practical_knowledge": ["Specific practical knowledge gap with examples"],\n'
            '        "theoretical": ["Theoretical gap and its implications"],\n'
            '        "population_gap": ["Details on population gaps with specific groups mentioned"]\n'
            '      }}\n'
            '    }},\n'
            '    ...\n'
            '  ],\n'
            '  "comparison_section": {{\n'
            '    "commonalities": ["Highlight shared gaps across articles, such as similar methodological issues or underrepresented populations"],\n'
            '    "contrasts": ["Point out differences in approach or focus, where one article may address an aspect that another neglects"],\n'
            '    "emerging_trends": ["Identify any new trends or gaps that have appeared only in the most recent research"]\n'
            '  }}\n'
            "}}\n\n"
            "{summaries}"
        )
    ]
)

# Initialize the LLM with chat model
llm = ChatOpenAI(model="gpt-4o-mini")

# Create the complete chain combining prompt and LLM
gap_analysis_chain = (
    RunnableLambda(lambda inputs: gap_analysis_prompt_template.format(**inputs)) | llm
)
    
async def analyze_gap(input_data, retries=3):
    for attempt in range(retries):
        try:
            response = await gap_analysis_chain.ainvoke(input_data)
            response_text = response.content if hasattr(response, 'content') else str(response)
            # Extract JSON from response
            json_code = extract_json_from_response(response_text)

            if json_code:
                response_data = json.loads(json_code)
                return response_data
            else:
                print("No JSON code block found in the response.")
                return None

        except json.JSONDecodeError as json_err:
            print(f"JSON decoding error: {json_err}")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < retries - 1:  # If not the last attempt
                print("Retrying...")
                await asyncio.sleep(2)  # Wait before retrying
            else:
                print("Max retries reached. Exiting.")
                return None

    
async def perform_gap_analysis(summaries, search_query):
    input_data = {
        "summaries": "\n".join(
            [f"- {summary['title']}: {summary['abstract']} + {summary['methods']} + {summary['discussion']}" for summary in summaries]
        ),
        "search_query": search_query
    }
    try:
        response = await analyze_gap(input_data)
        if response is None:
            print("analyze_gap returned None.")
            return None
        print(type(response))
        return response
    
    except Exception as e:
        print(f"An error occurred in perform_gap_analysis: {e}")
        return None
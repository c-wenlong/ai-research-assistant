# Research Paper Summarization Task

You are tasked with analyzing a research paper and extracting key information to fill in a structured JSON format. Your goal is to provide an accurate and concise summary of the paper's content. Do not output any additional text, only the JSON.

## Input:

You will be given the full text of a research paper. This may include all sections typically found in academic papers such as title, abstract, introduction, methods, results, discussion, conclusion, and references.

## Output:

You must fill in the following JSON structure with the extracted information:

```json
{
  "title": "",
  "abstract": "",
  "authors": [],
  "publication_date": "",
  "journal_name": "",
  "doi": "",
  "keywords": [],
  "introduction": "",
  "methods": "",
  "results": "",
  "discussion": "",
  "conclusion": "",
  "references": []
}
```

## Instructions:

1. title: Extract the full title of the paper.

2. abstract: Provide a concise summary of the paper's abstract. If no abstract is present, summarize the paper's main points in 2-3 sentences.

3. authors: List all authors of the paper. Include full names if available.

4. publication Date: Extract the publication date and format it as "YYYY MMM DD" (e.g., "2023 Sep 15"). If only the year or year and month are available, provide what's given.

5. journal Name: Provide the full name of the journal. If not available, leave it blank.

6. doi: Include the DOI (Digital Object Identifier) if present. If not available, leave it blank.

7. keywords: List the keywords provided in the paper. If not explicitly stated, extract 3-5 key terms that best represent the paper's content.

8. introduction, methods, results, discussion, and conclusion: For each of these sections, provide a concise summary (2-3 sentences) capturing the main points. If a section is missing or combined with another, adapt accordingly and note this in your summary.

9. references: For each reference, extract the following information if available:

   - title
   - authors (full names if possible)
   - publication date (in "YYYY MMM DD" format)
   - journal name

   Include up to 10 of the most relevant or frequently cited references. If there are more than 10, prioritize those that appear most crucial to the paper's argument or findings.

## Additional Guidelines:

- Maintain objectivity in your summaries. Avoid personal interpretations or evaluations of the research.
- If certain information is not available or unclear, leave the corresponding field blank rather than making assumptions.
- Ensure that your summaries are coherent and grammatically correct.
- If the paper uses specialized terminology, include brief explanations where necessary to make the summary accessible to a broader audience.
- If you encounter any ambiguities or difficulties in extracting information, note these in your response.

Remember, the goal is to provide an accurate and useful summary of the research paper that can be easily parsed and utilized in a research summarization tool.

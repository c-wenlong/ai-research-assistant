from pymongo import MongoClient
import os
import json
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field
from typing import Tuple, List, Optional
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.graphs import Neo4jGraph
from langchain.text_splitter import TokenTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from neo4j import GraphDatabase
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.runnables import ConfigurableField, RunnableParallel, RunnablePassthrough
from langchain.schema import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.schema import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from dotenv import load_dotenv
import time

# Uncomment the following line to enable debugging
# from neo4j.debug import watch
# watch("neo4j")

...  # your code here
# Initialise Neo4j db and env settings
load_dotenv()

class Entities(BaseModel):
    """Extracting information about research papers and related entities."""
    # People and Institutions
    # authors: List[str] = Field(
    #     ..., description="Names of authors, contributors, and affiliated institutions."
    # )
    # affiliations: List[str] = Field(
    #     ..., description="Institutions, universities, and organizations affiliated with the authors."
    # )
    
    # Publications
    titles: List[str] = Field(
        ..., description="Titles of research papers and articles"
    )
    # publication_dates: List[str] = Field(
    #     ..., description="Publication dates of the research papers."
    # )
    # journals: List[str] = Field(
    #     ..., description="Names of journals or conferences where the papers were published."
    # )
    
    # Research Topics and Domains
    topics: List[str] = Field(
        ..., description="Primary research topics or fields covered in the papers."
    )
    subtopics: List[str] = Field(
        ..., description="Subtopics or more specific areas within the primary topics."
    )
    
    # Methods and Techniques
    methods: List[str] = Field(
        ..., description="Research methodologies and analytical techniques used."
    )
    
    # Tools and Technologies
    tools: List[str] = Field(
        ..., description="Software, hardware, and other tools employed in the research."
    )
    
    # Datasets and Resources
    # datasets: List[str] = Field(
    #     ..., description="Data sources utilized or generated."
    # )
    
    # Concepts and Theories
    concepts: List[str] = Field(
        ..., description="Key concepts, theories, and frameworks discussed."
    )
    
    # Events and Conferences
    # events: List[str] = Field(
    #     ..., description="Events, workshops, and conferences where the research was presented."
    # )
    
    # Citations
    # citations: List[str] = Field(
    #     ..., description="References to other research papers cited in the documents."
    # )

def create_knowledge_graph(client, mongo_uri: str, db_name: str, collection_name: str, llm, batch_size: int = 10, max_workers: int = 13):
    print("Knowledge graph creation started")
    start_time = time.time()
    # Connect to MongoDB
    # client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    graph = Neo4jGraph()  

    # Pull articles from MongoDB
    papers = collection.find()
    documents = []

    # Process each paper into a Document for the graph
    for json_data in papers:
        json_data_lower = {key.lower(): value for key, value in json_data.items()}
        content = (
            json_data_lower.get("methods", "") +
            json_data_lower.get("results", "") +
            json_data_lower.get("discussion", "") +
            json_data_lower.get("conclusion", "")
        )       

        # metadata = {
        #     "title": json_data_lower.get("title", "Untitled"),
        #     "authors": json_data_lower.get("authors", "Unknown"),
        #     "publication_date": json_data_lower.get("publication_date", "Unknown"),
        #     "journal_name": json_data_lower.get("journal_name", "Unknown")
        # }

        document = Document(page_content=content)
        documents.append(document)

    llm_transformer = LLMGraphTransformer(llm=llm)
    
    # Split documents into batches
    batched_documents = [documents[i:i+batch_size] for i in range(0, len(documents), batch_size)]
    
    # Process documents in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_batch = {executor.submit(llm_transformer.convert_to_graph_documents, batch): batch for batch in batched_documents}
        
        # Wait for all futures to complete
        for future in as_completed(future_to_batch):
            graph_documents = future.result()
            graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
    
    client.close()
    print("Knowledge graph creation completed")
    end_time = time.time()
    print("Time taken for Knowledge Graph Generation: ", end_time-start_time)
    
    return graph

def fetchGraphData(cypher: str = "MATCH (s)-[r:!MENTIONS]->(t) RETURN s,r,t LIMIT 50"):
    # create a neo4j session to run queries
    driver = GraphDatabase.driver(
        uri=os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
    )
    session = driver.session()

    # Run the query and fetch results
    result = session.run(cypher)

    # Convert results to a format suitable for JSON
    graph_data = []
    for record in result:
        source = record['s']
        relationship = record['r']
        target = record['t']
        
        graph_data.append({
            'source': dict(source),  # Convert Node to dict
            'relationship': {
                'type': relationship.type,  # Extract relationship type
                'properties': dict(relationship)  # Convert Relationship properties to dict
            },
            'target': dict(target)  # Convert Node to dict
        })

    session.close()
    return graph_data

graph = Neo4jGraph()

vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding"
)

def saveGraphDataToJSON(graph_data, filename='graph_data.json'):
    # Save the graph data to a JSON file
    with open(filename, 'w') as json_file:
        json.dump(graph_data, json_file, indent=4)

def generate_full_text_query(input: str) -> str:
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()

def structured_retriever(question: str, entity_chain, graph) -> str:
    result = ""
    entities = entity_chain.invoke({"question": question})
    for entity in entities.names:
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit: 2})
                YIELD node, score
                CALL (node) {
                WITH node
                MATCH (node)-[r:MENTIONS]->(neighbor)
                RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r:MENTIONS]-(neighbor)
                RETURN neighbor.id + ' - ' + type(r) + ' -> ' + node.id AS output
                }
                RETURN output LIMIT 50
            """,
            {"query": generate_full_text_query(entity)},
        )
        result += "\n".join([el['output'] for el in response])
    return result

def retriever(question: str, entity_chain, graph, vector_index) -> str:
    # print(f"Search query: {question}")
    structured_data = structured_retriever(question, entity_chain, graph)
    unstructured_data = [el.page_content for el in vector_index.similarity_search(question)]
    final_data = f"""Structured data:
{structured_data}
Unstructured data:
{"#Document ".join(unstructured_data)}
    """
    return final_data

def llm_generation(question: str, llm, graph, vector_index) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a research assistant specialized in extracting structured information from academic papers to build a comprehensive knowledge graph. 
                Your task is to analyze the provided text and extract the following entities:

                1. **Titles:** Titles of research papers, articles, and publications.
                2. **Topics:** Primary research topics or fields covered in the papers.
                3. **Subtopics:** Subtopics or more specific areas within the primary topics.
                4. **Methods:** Research methodologies and analytical techniques used.
                5. **Tools:** Software, hardware, and other tools employed in the research.
                6. **Datasets:** Datasets and data sources utilized or generated.
                7. **Concepts:** Key concepts, theories, and frameworks discussed.
                8. **Events:** Events, workshops, and conferences where the research was presented.
                """,
            ),
            (
                "human",
                "Use the given format to extract information from the following input: {question}",
            ),
        ]
    )
    entity_chain = prompt | llm.with_structured_output(Entities)

    return retriever(question, entity_chain, graph, vector_index)


def run_full_workflow(mongo_uri: str, db_name: str, collection_name: str, llm, question: str, json_filename: str = 'graph_data.json') -> str:    
    # Step 1: Fetch Graph Data
    graph_data= fetchGraphData()
    
    # Step 2: Save Graph Data to JSON
    # saveGraphDataToJSON(graph_data, json_filename)
    
    # Step 3: LLM Generation and Retrieval
    final_response = llm_generation(question, llm, graph, vector_index)
    
    return final_response


# Example usage

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME")
collection_name = 'gut_microbiome'
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini-2024-07-18")


def llm_output(question):
    final_context = run_full_workflow(mongo_uri, db_name, collection_name, llm, question)
    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question,
                in its original language.
                Chat History:
                {chat_history}
                Follow Up Input: {question}
                Standalone question:"""  # noqa: E501
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:
        buffer = []
        for human, ai in chat_history:
            buffer.append(HumanMessage(content=human))
            buffer.append(AIMessage(content=ai))
        return buffer

    _search_query = RunnableBranch(
        # If input includes chat_history, we condense it with the follow-up question
        (
            RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
                run_name="HasChatHistoryCheck"
            ),  # Condense follow-up question and chat into a standalone_question
            RunnablePassthrough.assign(
                chat_history=lambda x: _format_chat_history(x["chat_history"])
            )
            | CONDENSE_QUESTION_PROMPT
            | ChatOpenAI(temperature=0)
            | StrOutputParser(),
        ),
        # Else, we have no chat history, so just pass through the question
        RunnableLambda(lambda x : x["question"]),
    )

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    "You are a knowledgeable research assistant trained to provide insights from a curated selection of academic papers. 
    Your task is to answer questions based on the content of these papers. When responding, ensure your answers are accurate, 
    concise, and cite specific findings or details from the papers whenever applicable. If the question requires further elaboration, 
    feel free to provide context or explain relevant concepts.
    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        RunnableParallel(
            {
                "context": RunnableLambda(lambda _: final_context),
                "question": RunnablePassthrough(),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({"question": question})

# print("-----------------------------")
# print(llm_output("What is good about MicrobiotaCN?"))
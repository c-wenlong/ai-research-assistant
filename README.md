# AIRA: Artificial Intelligence Research Assistant 🧠

Revolutionizing Academic Research with AI, Watch our [Demo](https://youtu.be/YiBkB2KtX3M?si=ktj0nATbIRdvrPBm).

## Project Overview

AIRA is an advanced AI-powered platform designed to transform the way researchers interact with academic literature. By leveraging cutting-edge natural language processing and machine learning techniques, AIRA addresses the challenges of information overload and inefficient literature review processes in academic research.

Our vision is to empower researchers to discover, analyze, and synthesize scientific knowledge more effectively, ultimately accelerating the pace of scientific progress.

![AIRA Overview](../frontend/src/assets/images/aira_overview.png)

## Key Features

- **Smart Search**: AI-powered search engine that understands context and semantic meaning
- **Interactive Literature Database**: Dynamic, filterable table of research papers with key metadata
- **Automated Paper Summaries**: AI-generated concise summaries of research papers
- **Knowledge Graph Visualization**: Interactive graph showing connections between papers and concepts
- **Chatbot Research Assistant**: AI-powered chatbot for answering research-related questions
- **PDF Analysis and Upload**: Automatic extraction and analysis of content from uploaded PDFs

Each feature of AIRA is designed to address specific pain points in the research process:

- Smart Search saves time by quickly identifying the most relevant papers.
- The Interactive Database provides a comprehensive overview of the literature landscape.
- Automated Summaries allow researchers to quickly grasp the key points of numerous papers.
- Knowledge Graphs help in identifying research gaps and potential collaborations.
- The Chatbot Assistant offers instant answers to research queries, enhancing productivity.
- PDF Analysis streamlines the process of incorporating new papers into the research workflow.

## Tech Stack

![AIRA Tech Stack](../frontend/src/assets/images/tech_stack.png)

Our technology stack is carefully chosen to provide a robust, scalable, and efficient solution:

1. Python: The core language for our backend, chosen for its rich ecosystem of scientific and ML libraries.
2. Streamlit: Enables rapid development of interactive web applications with Python.
3. OpenAI API: Powers our advanced natural language processing capabilities.
4. MongoDB: Provides a flexible, document-based database for storing complex research data.
5. Neo4j: Graph database used for creating and querying knowledge graphs.
6. LangChain: Enhances our ability to work with large language models and create AI-powered applications.
7. PyPDF2: Facilitates PDF parsing and text extraction.
8. PubMed API: Allows us to access a vast database of biomedical literature.

## Engineering Design

![RAG Retrieval](../frontend/src/assets/images/rag_retrieval.png)

### 1. Multithreading

We utilize async functions to perform multiple tasks simultaneously:

- Generating paper summaries
- Uploading to the database
- Creating knowledge graphs

This approach significantly reduces processing time and enhances user experience by allowing multiple operations to occur in parallel.

### 2. Microservices Architecture

Our application is built on a microservices architecture, which:

- Improves scalability by allowing independent scaling of different components
- Enhances maintainability through modular design
- Enables easier updates and feature additions without disrupting the entire system

### 3. Modularization

We've adopted a highly modular approach in our codebase:

- Enhances code reusability across different parts of the application
- Simplifies development and testing processes
- Allows for easier collaboration among team members working on different features

## Problem-Solving Approaches

### Efficient Collaboration

- Separate repositories for backend and frontend components
- Utilization of Git for version control:
  - Feature branching for parallel development
  - Pull requests and code reviews for quality assurance
  - Continuous integration to catch issues early

### Agile Development

- Adopted a sprint-based approach with short, intensive development cycles
- Team meetings every 3 hours to:
  - Share progress
  - Identify and resolve blockers quickly
  - Adjust priorities based on project needs
- This approach allowed us to maintain high velocity while staying flexible to changing requirements

### Leveraging Large Language Models

We integrated advanced Large Language Models (LLMs) from OpenAI and Anthropic into our development process:

- Code Assistance: Used LLMs to generate code snippets, debug issues, and optimize algorithms.
- Documentation: Leveraged AI to draft and refine documentation, ensuring clarity and comprehensiveness.
- Ideation: Employed LLMs for brainstorming sessions, generating innovative feature ideas and solution approaches.
- Problem-solving: Utilized AI to analyze complex problems and suggest potential solutions or approaches.
- Code Review: Integrated LLMs into our code review process to catch potential issues and suggest improvements.

This integration of AI tools significantly enhanced our development speed and code quality, allowing us to tackle complex challenges more effectively and innovate rapidly.

## User Stories

### The Time-Pressed PhD Student

Sarah, a PhD student in neuroscience, needs to conduct a comprehensive literature review for her thesis. With AIRA, she quickly generates summaries of hundreds of papers, identifying key trends and gaps in her field. The knowledge graph feature helps her discover unexpected connections between different research areas, inspiring a novel approach for her thesis.

### The Interdisciplinary Researcher

Dr. Lee is working on a project that spans both computer science and biology. He uses AIRA's smart search to find papers that bridge these fields, which traditional search engines often miss. The chatbot assists him in understanding unfamiliar terminology, enabling him to confidently explore new research territories.

### The Research Team Leader

Professor Garcia leads a large research team. She uses AIRA to keep track of the latest developments in their field, assigning relevant papers to team members based on AIRA's summaries. The interactive database helps her team collaboratively build a shared knowledge base, enhancing their collective research output.

## Competitive Advantage

While there are other research assistance tools available, AIRA stands out in several key areas:

1. Comprehensive Solution: Unlike tools that focus on a single aspect (e.g., just paper search or summarization), AIRA provides an end-to-end solution for the entire research workflow.
2. Advanced AI Integration: Our use of state-of-the-art language models allows for more nuanced understanding and generation of research content compared to keyword-based systems.
3. Interactive Knowledge Graphs: While some competitors offer basic citation networks, our knowledge graphs provide deeper insights into concept relationships across papers.
4. Customizability: AIRA's modular design allows for easy customization to specific research fields or institutional needs.
5. User-Centric Design: Developed based on extensive feedback from actual researchers, ensuring it addresses real-world pain points in the research process.

## Future Roadmap

- Q4 2023:
  - Integration with additional academic databases (e.g., ArXiv, IEEE Xplore)
  - Enhanced collaboration features for research teams
- Q1 2024:
  - Implementation of a recommendation system for related papers and potential collaborators
  - Development of a mobile app for on-the-go research assistance
- Q2 2024:
  - Integration of a citation management system
  - Addition of data visualization tools for quantitative research papers
- Q3 2024:
  - Implementation of multi-language support for global research communities
  - Development of an API for third-party integrations

## Join the Research Revolution

AIRA represents the future of academic research assistance. By supporting AIRA, you're not just backing a product; you're investing in the acceleration of scientific progress and innovation.

Here's how you can get involved:

1. 🚀 Early Adopter Program: Be among the first to experience the full power of AIRA and shape its future development.
2. 💼 Partnership Opportunities: Explore how AIRA can be customized for your institution or research organization.
3. 💡 Feedback and Collaboration: Share your insights to help us refine and expand AIRA's capabilities.

Together, we can transform the landscape of academic research, making it more efficient, insightful, and impactful than ever before.

## To run locally

run frontend

```bash
streamlit run frontend/src/$'\360\237\247\221'$'\342\200\215'🔬_AIRA.py
```

run backend

```bash
cd backend
flask run
```

---

AIRA - Empowering researchers with AI

© 2024 AIRA Team

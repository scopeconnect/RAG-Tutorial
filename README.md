# RAG System

A simple **PDF-based Retrieval-Augmented Generation (RAG) system**
designed as an AI Study Assistant.

Students can upload a PDF and ask questions about its content. The
application retrieves relevant information from the PDF and sends that
information to a local Large Language Model running through Ollama.

------------------------------------------------------------------------

## Architecture

``` text
PDF
 ↓
PyPDFLoader
 ↓
Text Splitter
 ↓
Chunks
 ↓
Ollama Embeddings
 ↓
Chroma Vector Database
 ↓
Student Question
 ↓
Similarity Search
 ↓
Top-K Relevant Chunks
 ↓
Prompt + Context
 ↓
Ollama LLM
 ↓
Answer + Source Pages
```

------------------------------------------------------------------------

## Technologies Used

-   Python
-   Gradio
-   LangChain
-   Ollama
-   ChromaDB
-   PyPDF

------------------------------------------------------------------------

## 1. Install Python

Recommended:

-   Python 3.10
-   Python 3.11

Check the installation:

``` bash
python --version
pip --version
```

On Windows, if `python` does not work, try:

``` bash
py --version
```

------------------------------------------------------------------------

## 2. Install Ollama

Install Ollama for your operating system.

After installation, verify:

``` bash
ollama --version
```

------------------------------------------------------------------------

## 3. Download the LLM

Run:

``` bash
ollama pull llama3.1:8b
```

This model generates the final answers.

------------------------------------------------------------------------

## 4. Download the Embedding Model

Run:

``` bash
ollama pull nomic-embed-text
```

This model converts text into numerical vectors called embeddings.

------------------------------------------------------------------------

## 5. Check Ollama Models

Run:

``` bash
ollama list
```

You should see models such as:

``` text
llama3.1:8b
nomic-embed-text
```

------------------------------------------------------------------------

## 6. Create the Project Folder

``` bash
mkdir student-rag
cd student-rag
```

The project should contain:

``` text
student-rag/
│
├── app.py
├── requirements.txt
└── venv/
```

------------------------------------------------------------------------

## 7. Create a Virtual Environment

Run:

``` bash
python -m venv venv
```

### Windows CMD

``` bash
venv\Scripts\activate
```

### Windows PowerShell

``` powershell
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

``` bash
source venv/bin/activate
```

After activation, you should normally see:

``` text
(venv)
```

at the beginning of the terminal prompt.

------------------------------------------------------------------------

## 8. Install Python Libraries

Upgrade pip:

``` bash
python -m pip install --upgrade pip
```

Then install the project dependencies:

``` bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:

``` text
gradio
langchain
langchain-community
langchain-text-splitters
langchain-ollama
langchain-chroma
chromadb
pypdf
```

------------------------------------------------------------------------

## 9. Run the RAG System

Make sure Ollama is running.

Then run:

``` bash
python app.py
```

Gradio should start the application.

Normally, it will be available at:

``` text
http://127.0.0.1:7860
```

Open this address in your browser.

------------------------------------------------------------------------

# How to Use the Application

## Step 1 --- Upload a PDF

Upload a text-based PDF such as:

-   Textbook
-   Class notes
-   Study material
-   Research paper
-   Handout

## Step 2 --- Process the PDF

Click:

``` text
Process PDF
```

The application will:

1.  Read the PDF.
2.  Extract the text.
3.  Split the text into chunks.
4.  Generate embeddings.
5.  Store the embeddings in Chroma.

## Step 3 --- Ask a Question

Example:

``` text
Explain photosynthesis in simple language.
```

The system searches the PDF and retrieves relevant chunks.

## Step 4 --- Generate the Answer

The retrieved chunks are sent to the Ollama LLM together with the
student's question.

The final response is displayed together with source page numbers.

------------------------------------------------------------------------

# What Is RAG?

RAG means:

**Retrieval-Augmented Generation**

Instead of asking the LLM to answer directly, the application first
retrieves relevant information from the uploaded document.

The basic process is:

``` text
Question
   ↓
Retrieve Information
   ↓
Give Information to LLM
   ↓
Generate Answer
```

This allows the LLM to answer using information from the student's
document.

------------------------------------------------------------------------

# What Is Chunking?

Large PDFs are divided into smaller pieces called **chunks**.

This project uses:

``` python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

`CHUNK_SIZE` controls the approximate size of each searchable piece.

`CHUNK_OVERLAP` repeats some text between neighboring chunks so
important context is less likely to be lost at a chunk boundary.

------------------------------------------------------------------------

# What Are Embeddings?

Embeddings convert text into numerical vectors.

For example:

``` text
"What is machine learning?"
        ↓
Embedding Model
        ↓
[0.12, -0.42, 0.78, ...]
```

These vectors allow the RAG system to compare pieces of text based on
their meaning.

The project uses:

``` text
nomic-embed-text
```

for embeddings.

------------------------------------------------------------------------

# What Is Chroma?

Chroma is the vector database used by this project.

It stores information associated with the PDF chunks, including:

-   Text chunks
-   Embeddings
-   PDF metadata
-   Page information

When a student asks a question, the system searches Chroma for chunks
with similar meaning.

------------------------------------------------------------------------

# What Is TOP_K?

The project uses:

``` python
TOP_K = 4
```

This means:

> Retrieve the four most relevant chunks from the PDF for each question.

Example:

``` text
100 PDF Chunks
      ↓
Student Question
      ↓
Similarity Search
      ↓
Rank Chunks
      ↓
Best 4 Chunks
      ↓
LLM
```

A very small `TOP_K` may miss useful context.

A very large `TOP_K` may add unnecessary or less relevant information.

`4` is used as a simple starting value for this project.

------------------------------------------------------------------------

# Why Add 1 to the Page Number?

PyPDFLoader commonly represents page indexes starting from zero.

Example:

``` text
Internal Index    Display Page
0                 Page 1
1                 Page 2
2                 Page 3
3                 Page 4
```

Therefore, the application uses:

``` python
page_number = (
    page_index + 1
    if isinstance(page_index, int)
    else "Unknown"
)
```

If `page_index` is a valid integer, the application adds `1`.

For example:

``` text
page_index = 4
```

becomes:

``` text
Page 5
```

If valid page information is unavailable, the application displays:

``` text
Unknown
```

instead of causing an error.

------------------------------------------------------------------------

# Models Used

## Chat Model

``` text
llama3.1:8b
```

### Purpose

The chat model generates the final natural-language answer.

It receives:

``` text
Student Question
+
Retrieved PDF Context
+
Prompt Instructions
```

and generates the final response.

## Embedding Model

``` text
nomic-embed-text
```

### Purpose

The embedding model converts PDF chunks and student questions into
vectors.

It is used for semantic search, not for writing the final answer.

------------------------------------------------------------------------

# Complete RAG Flow

Suppose a student uploads:

``` text
physics.pdf
```

and asks:

``` text
What is Newton's Third Law?
```

The application performs the following steps:

``` text
Student Question
       ↓
Question Embedding
       ↓
Search Chroma
       ↓
Retrieve TOP_K Relevant Chunks
       ↓
Collect Chunk Text + Page Metadata
       ↓
Build Context
       ↓
Context + Question + Instructions
       ↓
Ollama LLM
       ↓
Generate Answer
       ↓
Display Answer + Source Pages
```

------------------------------------------------------------------------

# Role of Each Technology

## Python

Runs the complete application.

## PyPDFLoader

Reads the uploaded PDF and extracts text page by page.

## RecursiveCharacterTextSplitter

Divides the extracted text into smaller overlapping chunks.

## Ollama Embeddings

Converts the chunks and questions into numerical vectors.

## Chroma

Stores and searches the vector representations.

## LangChain

Connects the document loader, splitter, embeddings, vector store,
prompt, and LLM.

## Ollama

Runs the AI models locally.

## Gradio

Provides the browser-based user interface.

------------------------------------------------------------------------

# Input → Process → Output

## PDF Processing

**Input:** Uploaded PDF

**Process:** Extract text and split it into chunks.

**Output:** Searchable text chunks with metadata.

## Embedding

**Input:** Text chunk

**Process:** Convert meaning into a numerical vector.

**Output:** Embedding vector.

## Vector Storage

**Input:** Chunks + embeddings + metadata

**Process:** Store them in Chroma.

**Output:** Searchable vector knowledge base.

## Retrieval

**Input:** Student question

**Process:** Convert the question to an embedding and compare it with
stored vectors.

**Output:** TOP_K relevant PDF chunks.

## Generation

**Input:** Student question + retrieved context

**Process:** Send the prompt to the Ollama chat model.

**Output:** Student-friendly answer.

## User Interface

**Input:** Student actions

**Process:** Gradio connects the visible controls to Python functions.

**Output:** PDF status, chat questions, answers, and source pages.

------------------------------------------------------------------------

# Common Problems

## Python Is Not Recognized

Try:

``` bash
py --version
```

If necessary, reinstall Python and enable:

``` text
Add Python to PATH
```

------------------------------------------------------------------------

## Ollama Is Not Recognized

Restart the terminal after installing Ollama.

Then test:

``` bash
ollama --version
```

------------------------------------------------------------------------

## Ollama Model Not Found

Run:

``` bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Then verify:

``` bash
ollama list
```

------------------------------------------------------------------------

## Connection Refused on Port 11434

Make sure the Ollama service is running.

The project expects Ollama at:

``` text
http://127.0.0.1:11434
```

------------------------------------------------------------------------

## Python Module Not Found

Make sure the virtual environment is active.

Then run:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## PDF Contains No Readable Text

The PDF may be a scanned or image-only document.

This starter project does not include OCR.

Use a text-based PDF for the demonstration.

------------------------------------------------------------------------

## Application Is Slow

Local AI performance depends on:

-   CPU
-   GPU
-   RAM
-   Model size

The `llama3.1:8b` model can be slow on lower-spec computers.

A smaller compatible Ollama model can be configured in `app.py` if
required.

------------------------------------------------------------------------

# Important Limitations

This is a classroom RAG project, not a perfect document-answering
system.

Students should understand that:

-   RAG improves grounding but does not guarantee correctness.
-   The LLM can still misinterpret retrieved information.
-   Important answers should be checked against the original PDF.
-   Scanned PDFs require OCR.
-   This starter version uses one active vector store.
-   The vector store is not persistent in this basic version.
-   Restarting the application clears the current knowledge base.
-   Chunk size, overlap, and TOP_K can affect retrieval quality.
-   Source pages show where retrieved chunks came from; they do not
    guarantee that every generated sentence appears exactly on those
    pages.

------------------------------------------------------------------------

# Suggested Student Questions

After processing a PDF, try questions such as:

``` text
Explain this topic in simple language.
```

``` text
What are the key points of this chapter?
```

``` text
What does this term mean?
```

``` text
Explain the difference between X and Y.
```

``` text
Give me an example based on the PDF.
```

``` text
Summarize the relevant information about this topic.
```

You can also deliberately ask a question whose answer is not in the PDF
and observe how the grounding instruction behaves.

------------------------------------------------------------------------

# Suggested Classroom Activity

Students do not need to write the implementation themselves.

Instead:

1.  Run the supplied RAG application.
2.  Upload a familiar PDF.
3.  Ask a question whose answer is clearly present.
4.  Check the source page.
5.  Ask the same question using different wording.
6.  Observe semantic retrieval.
7.  Ask something that is not in the document.
8.  Explain what happened between clicking **Ask** and receiving the
    answer.

Students should be able to describe:

``` text
PDF
 ↓
Chunks
 ↓
Embeddings
 ↓
Vector Database
 ↓
Question
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Answer
```

------------------------------------------------------------------------

# Possible Future Improvements

The starter application can later be extended with:

### Multiple PDFs

Allow students to build a knowledge base from several documents.

### Persistent Chroma

Save embeddings so documents do not need to be processed again after
restarting the application.

### OCR

Support scanned and image-only PDFs.

### Chat-Aware Retrieval

Use previous messages to understand follow-up questions.

### Better Citations

Show the exact retrieved passages in addition to page numbers.

### Quiz Generation

Generate MCQs from retrieved study material.

### Notes and Summaries

Add dedicated study modes.

### User Sessions

Keep each student's uploaded documents separate.

### Reranking

Improve the ordering of retrieved chunks.

### Streaming

Display the generated answer progressively.

------------------------------------------------------------------------

# Learning Outcomes

After completing and observing this project, students should understand:

-   What Retrieval-Augmented Generation is
-   Why RAG is useful
-   How PDFs are loaded
-   What text chunks are
-   Why chunk overlap is used
-   What embeddings are
-   What a vector database does
-   How semantic similarity search works
-   What `TOP_K` means
-   How retrieved context is passed to an LLM
-   Why prompt instructions are important
-   How source page information is obtained
-   What Ollama does
-   What LangChain does
-   What Chroma does
-   What Gradio does
-   How the complete RAG pipeline works

------------------------------------------------------------------------

# Final Mental Model

``` text
Prepare the PDF
      ↓
Create Chunks
      ↓
Create Embeddings
      ↓
Store in Chroma
      ↓
Ask a Question
      ↓
Retrieve Relevant Evidence
      ↓
Give Evidence to the LLM
      ↓
Generate an Explanation
      ↓
Show Answer + Source Pages
```

------------------------------------------------------------------------

## Project Purpose

The goal of this project is not only to run an AI application.

The main goal is to understand how a modern **Retrieval-Augmented
Generation system** connects document processing, embeddings, vector
search, retrieval, prompting, and a Large Language Model to answer
questions using external knowledge.

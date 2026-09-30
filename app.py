import gradio as gr

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate


# =========================================================
# CONFIGURATION
# =========================================================

OLLAMA_URL = "http://127.0.0.1:11434"

# Model used to generate answers
LLM_MODEL = "llama3.1:8b"

# Model used to create embeddings
EMBEDDING_MODEL = "nomic-embed-text"

# Text splitting settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Number of relevant chunks to retrieve
TOP_K = 4


# =========================================================
# VECTOR DATABASE
# =========================================================

# Initially there is no vector database.
# It will be created after the student processes a PDF.

vector_store = None


# =========================================================
# EMBEDDING MODEL
# =========================================================

embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_URL,
)


# =========================================================
# CHAT / GENERATION MODEL
# =========================================================

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
)


# =========================================================
# PROMPT
# =========================================================

prompt = ChatPromptTemplate.from_template(
    """
You are an AI Study Assistant.

Answer the student's question using only the supplied PDF context.

Explain the answer clearly and in student-friendly language.

Use examples when they are helpful.

If the answer cannot be found in the supplied context, say:

"I could not find this information in the uploaded PDF."

Context:
{context}

Question:
{question}

Answer:
"""
)


# =========================================================
# PROCESS PDF
# =========================================================

def process_pdf(pdf_file):

    global vector_store

    # Check whether a PDF was uploaded
    if pdf_file is None:
        return "Please upload a PDF first."

    try:

        # -------------------------------------------------
        # STEP 1: LOAD PDF
        # -------------------------------------------------

        loader = PyPDFLoader(pdf_file)

        documents = loader.load()

        if not documents:
            return "No readable text was found in the PDF."


        # -------------------------------------------------
        # STEP 2: SPLIT TEXT INTO CHUNKS
        # -------------------------------------------------

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        chunks = text_splitter.split_documents(documents)

        if not chunks:
            return "Could not create text chunks from the PDF."


        # -------------------------------------------------
        # STEP 3: CREATE VECTOR DATABASE
        # -------------------------------------------------

        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
        )


        # -------------------------------------------------
        # RETURN PROCESSING INFORMATION
        # -------------------------------------------------

        return (
            "PDF processed successfully!\n\n"
            f"Pages loaded: {len(documents)}\n"
            f"Chunks created: {len(chunks)}"
        )

    except Exception as e:

        return f"Error processing PDF:\n{str(e)}"


# =========================================================
# ASK QUESTION
# =========================================================

def ask_question(question, history):

    global vector_store


    # -----------------------------------------------------
    # CHECK VECTOR DATABASE
    # -----------------------------------------------------

    if vector_store is None:

        return "Please upload and process a PDF first."


    # -----------------------------------------------------
    # CHECK QUESTION
    # -----------------------------------------------------

    if not question or not question.strip():

        return "Please enter a question."


    try:

        # -------------------------------------------------
        # STEP 1: RETRIEVE RELEVANT CHUNKS
        # -------------------------------------------------

        docs = vector_store.similarity_search(
            question,
            k=TOP_K,
        )


        if not docs:

            return (
                "I could not find relevant information "
                "in the uploaded PDF."
            )


        # -------------------------------------------------
        # STEP 2: PREPARE CONTEXT
        # -------------------------------------------------

        context_parts = []

        pages = []


        for doc in docs:

            # PyPDFLoader normally stores pages starting at 0
            page_index = doc.metadata.get("page")


            # Convert:
            #
            # 0 -> Page 1
            # 1 -> Page 2
            # 2 -> Page 3
            #
            # If page information is unavailable,
            # display "Unknown".

            page_number = (
                page_index + 1
                if isinstance(page_index, int)
                else "Unknown"
            )


            # Add retrieved text to context

            context_parts.append(
                f"""
Page {page_number}:

{doc.page_content}
"""
            )


            # Save page number for citation

            pages.append(str(page_number))


        # Combine all retrieved chunks

        context = "\n\n".join(context_parts)


        # -------------------------------------------------
        # STEP 3: BUILD PROMPT
        # -------------------------------------------------

        messages = prompt.format_messages(
            context=context,
            question=question,
        )


        # -------------------------------------------------
        # STEP 4: SEND TO OLLAMA
        # -------------------------------------------------

        response = llm.invoke(messages)


        # -------------------------------------------------
        # STEP 5: REMOVE DUPLICATE PAGE NUMBERS
        # -------------------------------------------------

        unique_pages = list(dict.fromkeys(pages))

        source_pages = ", ".join(unique_pages)


        # -------------------------------------------------
        # STEP 6: RETURN ANSWER
        # -------------------------------------------------

        return (
            f"{response.content}"
            f"\n\n📚 Source Pages: {source_pages}"
        )


    except Exception as e:

        return f"Error generating answer:\n{str(e)}"


# =========================================================
# CLEAR KNOWLEDGE BASE
# =========================================================

def clear_pdf():

    global vector_store

    vector_store = None

    return "Knowledge base cleared."


# =========================================================
# GRADIO USER INTERFACE
# =========================================================

with gr.Blocks(title="RAG System") as demo:

    gr.Markdown(
        """
# 📚 RAG System

### AI Study Assistant

Upload your PDF notes, textbook, or study material
and ask questions about the document.

**Technology:**
LangChain + Ollama + Chroma + Gradio
"""
    )


    # -----------------------------------------------------
    # MAIN LAYOUT
    # -----------------------------------------------------

    with gr.Row():


        # =================================================
        # LEFT SIDE
        # =================================================

        with gr.Column(scale=1):

            gr.Markdown("## 📄 Document")


            pdf_upload = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath",
            )


            process_button = gr.Button(
                "Process PDF",
                variant="primary",
            )


            status = gr.Textbox(
                label="PDF Status",
                interactive=False,
                lines=5,
            )


            clear_button = gr.Button(
                "Clear PDF"
            )


        # =================================================
        # RIGHT SIDE
        # =================================================

        with gr.Column(scale=2):

            chatbot = gr.ChatInterface(
                fn=ask_question,
                title="Ask Your PDF",
                description=(
                    "Ask questions based on your "
                    "uploaded study material."
                ),
            )


    # -----------------------------------------------------
    # BUTTON EVENTS
    # -----------------------------------------------------

    process_button.click(
        fn=process_pdf,
        inputs=pdf_upload,
        outputs=status,
    )


    clear_button.click(
        fn=clear_pdf,
        outputs=status,
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
    )

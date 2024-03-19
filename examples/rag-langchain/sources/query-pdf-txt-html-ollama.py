from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, TextLoader # Assume UnstructuredHTMLLoader and TextLoader exist
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata
import argparse

class ChatDocument:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self.model = ChatOllama(model="mistral")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template("""
            <s> [Instruction] You are an assistant tasked with answering questions based on the provided document. Utilize the context from the document to formulate your response. If the answer is not available within the document, indicate that the information is not available. Aim for responses that are direct, informative, and no longer than three sentences. [/Instruction] </s>
            [Instruction] Question: {question}
            Context: {context}
            Answer: [/Instruction]
        """)

    def ingest(self, file_path: str):
        file_type = file_path.split('.')[-1].lower()
        try:
            if file_type == 'pdf':
                docs = PyPDFLoader(file_path=file_path).load()
            elif file_type == 'html':
                docs = UnstructuredHTMLLoader(file_path=file_path).load()  # Assume UnstructuredHTMLLoader exists
            elif file_type == 'txt':
                docs = TextLoader(file_path=file_path).load()  # Assume TextLoader exists
            else:
                return "Unsupported file type"
        except Exception as e:
            return f"Failed to load document: {str(e)}"
        
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        self.vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.2,
            },
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser())

    def ask(self, query: str):
        if not self.chain:
            return "Please, add a document first."

        try:
            return self.chain.invoke(query)
        except Exception as e:
            return f"Error during query processing: {str(e)}"

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None

def main():
    parser = argparse.ArgumentParser(description="CLI for querying documents with ChatDocument. Supports single questions or interactive chat mode. Remember to run ollama in the backend before using this CLI")
    parser.add_argument('-f', '--file', help="Path to the document file (e.g. pdf, html, txt)", required=True)
    parser.add_argument('-q', '--question', help="Question to ask about the document", required=False)

    args = parser.parse_args()

    chat_document = ChatDocument()
    chat_document.ingest(args.file)

    if args.question:
        answer = chat_document.ask(args.question)
        print(f"Answer: {answer}")
    else:
        print("ChatDocument is now in chat mode. Type 'exit' to quit.")
        while True:
            question = input("Ask a question: ")
            if question.lower() == 'exit':
                break
            answer = chat_document.ask(question)
            print(f"Answer: {answer}")

    chat_document.clear()
    if not args.question:
        print("Exiting ChatDocument chat mode. Goodbye!")

if __name__ == "__main__":
    main()

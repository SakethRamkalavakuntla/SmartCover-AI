import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
        self.load_portfolio()

    def load_portfolio(self):
        if self.collection.count() == 0:
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row['Techstack']],
                    metadatas=[{"links": row['Links']}],
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        query_result = self.collection.query(query_texts=[skills], n_results=3)
        metadatas = query_result.get('metadatas', [[]])[0]
        links = [m.get('links', '') for m in metadatas]
        return links

from langchain_google_vertexai import VertexAIEmbeddings
import pickle
from utils.config import settings


class EmbeddingModel:
    """
    A class to handle the creation, saving, and reading of embeddings using OpenAI's embedding model.
    """
    def __init__(self):
        """
        Initializes the EmbeddingModel with the specified OpenAI embedding model and API key.
        """
        self.embedding_model = VertexAIEmbeddings(settings.EMBEDDING_MODEL_NAME)

    def get_embeddings(self, data: dict):
        """
        Generates embeddings for the given data.

        Args:
            data (dict): A dictionary where the keys are identifiers and the values are the texts to be embedded.

        Returns:
            dict: A dictionary with the same keys as the input and the corresponding embeddings as values.
        """
        output = {}
        keys = list(data.keys())
        docs = list(data.values())
        embeddings = self.embedding_model.embed_documents(docs)
        for i in range(len(keys)):
            output[keys[i]] = embeddings[i]
        return output

    @staticmethod
    def save_embeddings(embedding, file_name):
        """
        Saves the given embeddings to a file.

        Args:
            embedding (dict): The embeddings to be saved.
            file_name (str): The name of the file to save the embeddings to.
        """
        with open(settings.OUTPUT_PATH + file_name, 'wb') as handle:
            pickle.dump(embedding, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def read_embeddings(file_name):
        """
        Reads embeddings from a file.

        Args:
            file_name (str): The name of the file to read the embeddings from.

        Returns:
            dict: The embeddings read from the file.
        """
        with open(settings.OUTPUT_PATH + file_name, 'rb') as handle:
            output_dict = pickle.load(handle)
        return output_dict

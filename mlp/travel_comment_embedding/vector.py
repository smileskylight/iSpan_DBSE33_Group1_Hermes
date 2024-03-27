# import packages
import torch
from transformers import BertTokenizer, BertModel, BertTokenizerFast, AutoModel
import requests
import json

# OPTIONAL: if you want to have more information on what's happening, activate the logger as follows
import logging

# logging.basicConfig(level=logging.INFO)
import matplotlib.pyplot as plt

# %matplotlib inline


# model use for word embedding
class TextEmbedder:
    def __init__(self, model_name="ckiplab/bert-tiny-chinese"):
        """
        Initialize the tokenizer and model upon creating an instance of TextEmbedder.

        Parameters:
        - model_name: The name of the pre-trained BERT model to use.
        """
        self.tokenizer = BertTokenizerFast.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # Set the model to evaluation mode

    def texts_to_embeddings(self, texts):
        """
        Convert a list of texts to their corresponding BERT embeddings.

        Parameters:
        - texts: A list of strings, where each string is a text to be processed.

        Returns:
        - embeddings: A list of tensors, each representing the embedding of a text.
        """
        embeddings = []

        for text in texts:
            # Tokenize the text and convert to tensors
            encoded_input = self.tokenizer(
                text, padding=True, truncation=True, return_tensors="pt"
            )
            tokens_tensor = encoded_input["input_ids"]
            segments_tensors = encoded_input["token_type_ids"]

            # Process the inputs through the BERT model
            with torch.no_grad():
                outputs = self.model(tokens_tensor, segments_tensors)
                hidden_states = outputs.last_hidden_state

            # Use the output of the last layer for each token and mean it to represent the sentence
            embeddings.append(torch.mean(hidden_states, dim=1))

        return embeddings


# # Example usage:
# embedder = TextEmbedder()  # Initialize once

# # word embed
# cleaned_lines = []
# file_path = "./travel_comment_embedding/data/travel_comment_clean.txt"

# texts = []
# with open(file_path, "r", encoding="utf-8") as file:
#     for i, line in enumerate(file):
#         texts.append(line)

# embeddings_list = []
# embeddings = embedder.texts_to_embeddings(
#     texts
# )  # Call the method for any list of texts
# for i, embedding in enumerate(embeddings):
#     print(f"Embedding for text {i+1}: Shape = {embedding.shape}")
#     embedding = embedding[0].tolist()
#     embeddings_list.append(embedding)

# # Open a file for writing
# with open("./travel_comment_embedding/data/travel_comment_vec.txt", "w") as file:
#     # Iterate over each element in the list
#     for item in embeddings_list:
#         # Write the item to the file, followed by a newline character
#         file.write("%s\n" % item)

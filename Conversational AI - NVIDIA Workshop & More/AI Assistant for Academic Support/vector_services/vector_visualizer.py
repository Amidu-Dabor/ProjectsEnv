# vector_services/vector_visualizer.py

# ── Monkey‑patch to satisfy "from numpy.core.numeric import ComplexWarning" in sklearn ──
import numpy as _np
import numpy.core.numeric as _numeric
if not hasattr(_numeric, "ComplexWarning"):
    class ComplexWarning(Warning):
        """Placeholder for numpy.core.numeric.ComplexWarning"""
        pass
    _numeric.ComplexWarning = ComplexWarning

# ────────────────────────────────────────────────────────────────────────────────

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE

from data_curator import assign_color, safe_embeddings_constructor


class VectorVisualizer:
    def __init__(self, vector_store):
        """
        Initialize the visualizer with an existing vector store.
        The vector store can either be a dict with a "collection" key
        or a Chroma instance (which has a _collection attribute).
        """
        self.vector_store = vector_store
        self.collection = self._get_collection()

    def _get_collection(self):
        # If vector_store is a dict with a "collection" key, return that.
        if isinstance(self.vector_store, dict) and "collection" in self.vector_store:
            return self.vector_store["collection"]
        # If it has an attribute _collection, use that.
        elif hasattr(self.vector_store, "_collection"):
            return self.vector_store._collection
        # Otherwise, assume the vector_store is already the collection.
        return self.vector_store

    def visualize_2d(self):
        result = self.collection.get(include=['embeddings', 'documents', 'metadatas'])
        vectors = np.array(result['embeddings'])
        documents = result['documents']
        metadatas = result.get('metadatas', [{}] * len(documents))
        n_samples = vectors.shape[0]

        if n_samples < 2:
            print("Not enough samples to visualize TSNE.")
            return

        # perplexity = min(30, max(1, n_samples - 1))
        perplexity = min(30, n_samples - 1)
        colours = [assign_color((md or {}).get("doc_type", "other")) for md in metadatas]
        doc_types = [(md or {}).get("doc_type", "other") for md in metadatas]
        text = [f"Type: {t}<br>Text: {d[:100]}..." for t, d in zip(doc_types, documents)]
        
        tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
        reduced_vectors = tsne.fit_transform(vectors)
        fig = go.Figure(data=[go.Scatter(
            x=reduced_vectors[:, 0],
            y=reduced_vectors[:, 1],
            mode='markers',
            marker=dict(size=5, color=colours, opacity=0.8),
            text=text,
            hoverinfo='text'
        )])
        fig.update_layout(title="2D Vector Store Visualization", width=1000, height=800)
        fig.show()

    def visualize_3d(self):
        result = self.collection.get(include=['embeddings', 'documents', 'metadatas'])
        vectors = np.array(result['embeddings'])
        documents = result['documents']
        metadatas = result.get('metadatas', [{}] * len(documents))
        n_samples = vectors.shape[0]
        
        if n_samples < 2:
            print("Not enough samples to visualize TSNE.")
            return

        # perplexity = min(30, max(1, n_samples - 1))
        perplexity = min(30, n_samples - 1)
        colours = [assign_color((md or {}).get("doc_type", "other")) for md in metadatas]
        doc_types = [(md or {}).get("doc_type", "other") for md in metadatas]
        text = [f"Type: {t}<br>Text: {d[:100]}..." for t, d in zip(doc_types, documents)]
        
        tsne = TSNE(n_components=3, random_state=42, perplexity=perplexity)
        reduced_vectors = tsne.fit_transform(vectors)
        fig = go.Figure(data=[go.Scatter3d(
            x=reduced_vectors[:, 0],
            y=reduced_vectors[:, 1],
            z=reduced_vectors[:, 2],
            mode='markers',
            marker=dict(size=5, color=colours, opacity=0.8),
            text=text,
            hoverinfo='text'
        )])
        fig.update_layout(title="3D Vector Store Visualization", width=1000, height=800)
        fig.show()

    def visualize_both(self):
        result = self.collection.get(include=['embeddings', 'documents', 'metadatas'])
        vectors = np.array(result['embeddings'])
        documents = result['documents']
        metadatas = result.get('metadatas', [{}] * len(documents))
        n_samples = vectors.shape[0]
        
        if n_samples < 2:
            print("Not enough samples to visualize TSNE.")
            return

        # perplexity = min(30, max(1, n_samples - 1))
        perplexity = min(30, n_samples - 1)
        colours = [assign_color((md or {}).get("doc_type", "other")) for md in metadatas]
        doc_types = [(md or {}).get("doc_type", "other") for md in metadatas]
        text = [f"Type: {t}<br>Text: {d[:100]}..." for t, d in zip(doc_types, documents)]
        
        tsne_2d = TSNE(n_components=2, random_state=42, perplexity=perplexity)
        reduced_2d = tsne_2d.fit_transform(vectors)
        trace2d = go.Scatter(
            x=reduced_2d[:, 0],
            y=reduced_2d[:, 1],
            mode='markers',
            marker=dict(size=5, color=colours, opacity=0.8),
            text=text,
            hoverinfo='text'
        )
        tsne_3d = TSNE(n_components=3, random_state=42, perplexity=perplexity)
        reduced_3d = tsne_3d.fit_transform(vectors)
        trace3d = go.Scatter3d(
            x=reduced_3d[:, 0],
            y=reduced_3d[:, 1],
            z=reduced_3d[:, 2],
            mode='markers',
            marker=dict(size=5, color=colours, opacity=0.8),
            text=text,
            hoverinfo='text'
        )
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("2D Visualization", "3D Visualization"),
                            specs=[[{"type": "scatter"}, {"type": "scatter3d"}]])
        fig.add_trace(trace2d, row=1, col=1)
        fig.add_trace(trace3d, row=1, col=2)
        fig.update_layout(title="Combined Vector Store Visualizations", width=1500, height=700)
        fig.show()


if __name__ == "__main__":
    # Load the existing vector store from the persist directory.
    from langchain_chroma import Chroma
    vector_store = Chroma(
        persist_directory="vector_services/usiu_vector_db",
        embedding_function=safe_embeddings_constructor()
    )
    
    # Initialize the visualizer with the loaded vector store.
    visualizer = VectorVisualizer(vector_store)
    
    print("Visualizing in 2D:")
    visualizer.visualize_2d()
    
    print("Visualizing in 3D:")
    visualizer.visualize_3d()
    
    print("Visualizing both 2D and 3D:")
    visualizer.visualize_both()

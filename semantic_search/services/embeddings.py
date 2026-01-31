"""
Servicio de Embeddings
======================
Este módulo gestiona la conversión de texto a vectores numéricos (embeddings).

Conceptos clave:
- Embedding: Vector de 384 números que representa el "significado" de un texto
- SentenceTransformer: Modelo pre-entrenado que hace la conversión
- Thread-safe: Usa locks para que múltiples requests puedan usar el modelo sin problemas
"""
import threading
from sentence_transformers import SentenceTransformer

# Nombre del modelo que usaremos
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Variables globales para el modelo (singleton pattern)
_lock = threading.Lock()  # Para evitar problemas de concurrencia
_model = None  # El modelo se cargará la primera vez que se use


def get_model():
    """
    Obtiene la instancia del modelo de embeddings.
    
    Patrón Singleton + Lazy Loading:
    - Solo carga el modelo la primera vez que se llama
    - Reutiliza la misma instancia en llamadas posteriores
    - Thread-safe: usa un lock para evitar problemas si múltiples
      threads intentan cargar el modelo simultáneamente
    
    Returns:
        SentenceTransformer: Modelo cargado y listo para usar
        
    Ejemplo:
        >>> model = get_model()
        >>> vector = model.encode(["Hola mundo"])
    """
    global _model
    
    # Si ya está cargado, devolverlo directamente
    if _model is None:
        # Double-checked locking pattern
        with _lock:
            # Verificar de nuevo por si otro thread lo cargó mientras esperábamos
            if _model is None:
                print(f"🔄 Cargando modelo: {_MODEL_NAME}")
                print("   (Esto puede tardar ~10-30 segundos la primera vez)")
                _model = SentenceTransformer(_MODEL_NAME)
                print("✅ Modelo cargado correctamente")
    
    return _model


def embed_text(text: str) -> list[float]:
    """
    Convierte un texto en un vector de embeddings.
    
    Proceso:
    1. Limpia el texto (elimina espacios extra)
    2. Si está vacío, retorna lista vacía
    3. Usa el modelo para generar el vector
    4. Normaliza el vector (para poder usar cosine similarity)
    5. Convierte a lista de Python
    
    Args:
        text: Texto a convertir (puede ser título, descripción, etc.)
        
    Returns:
        list[float]: Lista de 384 números flotantes representando el embedding.
                     Lista vacía si el texto está vacío.
    

    """
    # Limpiar y validar el texto
    text = (text or "").strip()
    if not text:
        return []
    
    # Obtener el modelo (se carga solo la primera vez)
    model = get_model()
    
    # Generar el embedding
    # - encode() recibe una lista de textos y devuelve array de numpy
    # - normalize_embeddings=True hace que todos los vectores tengan magnitud 1
    #   (necesario para usar cosine similarity como simple dot product)
    vec = model.encode([text], normalize_embeddings=True)[0]
    
    # Convertir de numpy array a lista de Python (para guardar en JSON)
    return vec.tolist()


def model_name() -> str:
    """
    Retorna el nombre del modelo usado.
    
    Útil para guardar en la BD qué modelo generó cada embedding.
    Si cambiamos de modelo en el futuro, podremos identificar
    qué eventos necesitan recalcular su embedding.
    
    Returns:
    str: Nombre completo del modelo
        
    Ejemplo:
        >>> model_name()
        'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    """
    return _MODEL_NAME
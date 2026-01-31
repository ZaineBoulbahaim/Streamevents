"""
Este módulo compara vectores usando cosine similarity y retorna
los elementos más similares ordenados por puntuación.
"""
import numpy as np

def cosine_top_k(query_vec: list[float], items: list[tuple], k: int = 20):
    """
    Encuentra los K elementos más similares al vector de búsqueda.
    
    Proceso:
    1. Valida que el vector de búsqueda sea válido
    2. Para cada item, calcula cosine similarity con la búsqueda
    3. Ordena por puntuación descendente
    4. Retorna los top K
    Args:
        query_vec: Vector de la búsqueda del usuario (384 números)
        items: Lista de tuplas (objeto, embedding)
               Ejemplo: [(evento1, [0.1, 0.2, ...]), (evento2, [0.3, 0.4, ...])]
        k: Número de resultados a retornar (por defecto 20)
    Returns:
        Lista de tuplas (objeto, score) ordenadas por score descendente
        Ejemplo: [(evento1, 0.95), (evento2, 0.78), ...]
    """
    
    #  VALIDACIÓN 
    # Si el vector de búsqueda está vacío, no podemos comparar
    if not query_vec:
        return []
    
    # Convertir la lista a array de numpy para operaciones matemáticas rápidas
    q = np.array(query_vec, dtype=np.float32)
    
    # Verificar que el vector no sea todo ceros (sería inválido)
    if np.linalg.norm(q) == 0:
        return []
    
    #  CÁLCULO DE SIMILITUDES 
    scored = []  # Aquí guardaremos (objeto, score)
    
    for obj, emb in items:
        # Saltar items sin embedding
        if not emb:
            continue
        
        # Convertir embedding a numpy array
        v = np.array(emb, dtype=np.float32)
        
        # Verificar que los vectores tengan la misma dimensión
        # y que el vector no sea todo ceros
        if v.shape != q.shape or np.linalg.norm(v) == 0:
            continue
        
        #  COSINE SIMILARITY 
        # Fórmula: cos(θ) = (A · B) / (||A|| × ||B||)
        # Pero como normalizamos en embed_text(), ||A|| = ||B|| = 1
        # Por tanto: cos(θ) = A · B (simple dot product)
        score = float(np.dot(q, v))
        
        scored.append((obj, score))
    
    #  ORDENAR Y RETORNAR TOP-K 
    # Ordenar por score descendente (mayor a menor)
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Retornar solo los primeros K elementos
    return scored[:k]
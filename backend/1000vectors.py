import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_experiment():
    print("=" * 60)
    print("Concentration of Measure Experiment: Cosine Similarities")
    print("=" * 60)
    
    num_vectors = 2000
    dimensions = [10, 100, 1000]
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    results = {}
    
    # Setup plotting style
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    colors = ['#FF6B6B', '#4D96FF', '#6BCB77']
    
    for i, d in enumerate(dimensions):
        # 1. Generate 2,000 random vectors in d dimensions
        # Draw from standard normal distribution
        vectors = np.random.normal(0, 1, size=(num_vectors, d))
        
        # 2. Normalize vectors to unit length (L2 norm = 1)
        # One-liner to normalize random vectors
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        # Avoid division by zero (though extremely unlikely with normal distribution)
        norms[norms == 0] = 1e-9
        normalized_vectors = vectors / norms
        
        # 3. Compute pairwise cosine similarities
        # Since vectors are normalized, cosine similarity is just the dot product
        similarity_matrix = np.dot(normalized_vectors, normalized_vectors.T)
        
        # Get the upper triangular indices (excluding the diagonal)
        triu_idx = np.triu_indices(num_vectors, k=1)
        pairwise_similarities = similarity_matrix[triu_idx]
        
        # Calculate statistics
        mean_sim = np.mean(pairwise_similarities)
        var_sim = np.var(pairwise_similarities)
        std_sim = np.std(pairwise_similarities)
        min_sim = np.min(pairwise_similarities)
        max_sim = np.max(pairwise_similarities)
        
        results[d] = {
            'similarities': pairwise_similarities,
            'mean': mean_sim,
            'variance': var_sim,
            'std': std_sim,
            'min': min_sim,
            'max': max_sim
        }
        
        print(f"\nDimensionality: {d}")
        print(f"  Mean similarity:     {mean_sim:+.6f}")
        print(f"  Variance:            {var_sim:.6e}")
        print(f"  Standard Deviation:  {std_sim:.6f}")
        print(f"  Range of similarity: [{min_sim:+.4f}, {max_sim:+.4f}]")
        
        # 4. Plot Histogram
        # Using standard frequency count and setting fixed x-limits [-1, 1]
        sns.histplot(pairwise_similarities, bins=100, kde=True, ax=axes[i], 
                     color=colors[i], stat="count", alpha=0.6)
        axes[i].set_title(f"Cosine Similarity (d = {d})", fontsize=12, fontweight='bold')
        axes[i].set_xlabel("Cosine Similarity", fontsize=11)
        axes[i].set_ylabel("Frequency (Count)" if i == 0 else "") # only label y-axis on leftmost plot for clean look
        axes[i].set_xlim(-1, 1)
        
        # Annotate with statistics (placing on upper-left to avoid blocking the narrow peak around 0)
        stats_text = (
            f"Mean: {mean_sim:+.4f}\n"
            f"Std Dev: {std_sim:.4f}\n"
            f"Var: {var_sim:.2e}\n"
            f"Min/Max: [{min_sim:+.2f}, {max_sim:+.2f}]"
        )
        axes[i].text(0.05, 0.95, stats_text, transform=axes[i].transAxes,
                     verticalalignment='top', horizontalalignment='left',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    # Overall plot formatting
    plt.suptitle("Concentration of Measure: Distribution of Cosine Similarities\n"
                 "As dimensionality (d) increases, random vectors become almost perfectly orthogonal (similarity ≈ 0).", 
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, 'cosine_similarity_distributions.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nHistogram plot saved to: {output_path}")
    print("=" * 60)
    print("CONCLUSION:")
    print("In 10 dimensions, the similarities are spread out across a wider range.")
    print("In 1,000 dimensions, almost all cosine similarities concentrate extremely close to 0.")
    print("This means in high-dimensional space, two random vectors are almost certainly orthogonal.")
    print("This 'Concentration of Measure' is why semantic search works: query vectors can be distinctly")
    print("similar to relevant items, while being completely orthogonal (similarity ~ 0) to random/unrelated items.")
    print("=" * 60)

if __name__ == "__main__":
    run_experiment()

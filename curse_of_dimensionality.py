import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import kurtosis
import matplotlib.pyplot as plt
import os

def explore_curse():
    print("Starting Curse of Dimensionality Exploration...")
    print("-" * 80)
    print(f"{'Dimension':<10} | {'Mean':<8} | {'Variance':<10} | {'Kurtosis':<8} | {'Min':<8} | {'Max':<8}")
    print("-" * 80)
    
    num_vectors = 1000
    dimensions = [2**i for i in range(1, 11)] # 2, 4, 8, ..., 1024
    
    results = []
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    for d in dimensions:
        # Generate 1000 random unit vectors
        # Generate normal values and normalize to unit length
        vectors = np.random.normal(0, 1, (num_vectors, d))
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors /= norms
        
        # Calculate all pairwise distances
        # pdist returns a condensed distance matrix
        distances = pdist(vectors, metric='euclidean')
        
        # Compute statistics
        min_dist = np.min(distances)
        max_dist = np.max(distances)
        mean_dist = np.mean(distances)
        var_dist = np.var(distances)
        kurt_dist = kurtosis(distances)
        
        results.append({
            'dim': d,
            'min': min_dist,
            'max': max_dist,
            'mean': mean_dist,
            'var': var_dist,
            'kurtosis': kurt_dist,
            'all_distances': distances
        })
        
        print(f"{d:<10} | {mean_dist:<8.4f} | {var_dist:<10.6e} | {kurt_dist:<8.4f} | {min_dist:<8.4f} | {max_dist:<8.4f}")

    # Visualization
    print("-" * 80)
    plt.figure(figsize=(14, 8))
    
    # Select a subset of dimensions to plot for clarity
    plot_dims = [2, 8, 32, 128, 512, 1024]
    
    for res in results:
        if res['dim'] in plot_dims:
            plt.hist(res['all_distances'], bins=100, alpha=0.5, 
                     label=f'D={res["dim"]} (Var={res["var"]:.2e})', 
                     density=True, histtype='stepfilled')
            
    plt.title("Evolution of Euclidean Distance Distribution with Increasing Dimensionality", fontsize=14)
    plt.xlabel("Euclidean Distance", fontsize=12)
    plt.ylabel("Probability Density", fontsize=12)
    plt.legend(title="Dimensionality")
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Annotate the trend
    plt.text(0.1, 0.9, "Notice how distributions become narrower\nand concentrate around sqrt(2) ≈ 1.414", 
             transform=plt.gca().transAxes, fontsize=12, color='darkred', weight='bold')
    
    output_path = 'distance_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to '{output_path}'")
    
    # Analysis Summary
    print("\nSummary of Observations:")
    print("1. Concentration of Measure: As dimensions increase, the variance of distances decreases sharply.")
    print("2. Orthogonality: Random vectors in high dimensions become increasingly orthogonal.")
    print("   For unit vectors, the distance between orthogonal vectors is sqrt(2) ≈ 1.414.")
    print("3. Curse of Dimensionality: In 1024D, the difference between the closest and farthest points")
    print("   becomes negligible relative to the mean, making 'nearest neighbor' searches problematic.")

if __name__ == "__main__":
    explore_curse()

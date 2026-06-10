import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set a premium style for the plots
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Roboto', 'Arial', 'sans-serif']

def generate_sampling_analysis():
    # 1. Create an array X with 15 random numbers (e.g., from a uniform distribution 0 to 10)
    # We'll use random integers or floats. Let's use floats for more variation.
    np.random.seed(42) # For reproducibility
    X = np.random.uniform(1, 10, 15)
    
    # 2. Prepare data for the table
    results = []
    
    for T in range(1, 11):
        # Y: e to the power X (original exponentiation)
        Y = np.exp(X)
        
        # Z: e to the power (X / T) - scaled exponentiation with temperature
        Z = np.exp(X / T)
        
        # W: Z divided by sum of all Z values (normalized probabilities)
        W = Z / np.sum(Z)
        
        # Store results for the table
        for i in range(len(X)):
            results.append({
                'Temperature (T)': T,
                'X': X[i],
                'Y': Y[i],
                'Z': Z[i],
                'W': W[i]
            })
            
    df = pd.DataFrame(results)
    
    # Print the table (first few rows to show it works)
    print("\n--- Sampling Analysis Table (First 15 rows for T=1) ---")
    print(df[df['Temperature (T)'] == 1].to_string())
    print("\n--- Summary for different T values (Average W) ---")
    print(df.groupby('Temperature (T)')['W'].describe())

    # 3. Plotting
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    
    # Histogram for X (the original numbers)
    sns.histplot(X, bins=10, kde=True, color='#4A90E2', ax=axes[0])
    axes[0].set_title('Distribution of Original Random Values (X)', fontsize=16, fontweight='bold', pad=20)
    axes[0].set_xlabel('Value', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    
    # Evolution of W (Softmax with Temperature)
    # We'll plot how the probabilities change across different T
    # Create a line plot or bar plot to show the distribution shift
    # Or multiple histplots overlayed
    colors = sns.color_palette("viridis", 10)
    
    for i, T in enumerate(range(1, 11)):
        dist = df[df['Temperature (T)'] == T]['W']
        sns.kdeplot(dist, ax=axes[1], label=f'T={T}', color=colors[i], fill=True, alpha=0.1)
    
    axes[1].set_title('Softmax Probability Distribution (W) over Temperatures', fontsize=16, fontweight='bold', pad=20)
    axes[1].set_xlabel('Probability (W)', fontsize=12)
    axes[1].set_ylabel('Density', fontsize=12)
    axes[1].legend(title='Temperature', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Save the plot
    plot_path = 'sampling_histograms.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\nPlots saved to {plot_path}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    generate_sampling_analysis()

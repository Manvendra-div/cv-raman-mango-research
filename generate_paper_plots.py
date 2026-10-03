import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set style
plt.style.use('default')
plt.rcParams.update({'font.size': 12, 'figure.dpi': 300, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'axes.grid': True})

OUTPUT_DIR = "/home/manvendrasingh/mango_crop_research/CV Raman Research Work Updated/paper_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Regression Performance
def plot_regression():
    models = ['Mean Baseline', 'Linear Reg.', 'Elastic Net', 'Linear SVR', 'Random Forest', 'Gradient Boosting', 'XGBoost']
    rmse = [2.33, 2.01, 2.01, 2.02, 2.01, 2.01, 2.01]
    r2 = [0.00, 0.26, 0.26, 0.25, 0.26, 0.26, 0.26]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(models))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, rmse, width, label='RMSE (Lower is Better)', color='#1f77b4')
    rects2 = ax.bar(x + width/2, r2, width, label='R² Score (Higher is Better)', color='#ff7f0e')
    
    ax.set_ylabel('Score')
    ax.set_title('Regression Model Performance (Test Set)')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    # Highlight champion
    ax.get_xticklabels()[5].set_fontweight("bold")
    ax.get_xticklabels()[5].set_color("darkred")
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "regression_performance.png"))
    plt.close()

# 2. Classification Performance
def plot_classification():
    models = ['Baseline', 'Logistic Reg.', 'Linear SVM', 'Random Forest', 'Gradient Boosting']
    accuracy = [0.48, 0.984, 0.991, 0.983, 0.993]
    roc_auc = [0.50, 0.999, 0.999, 0.999, 0.999]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(models))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, accuracy, width, label='Accuracy', color='#2ca02c')
    rects2 = ax.bar(x + width/2, roc_auc, width, label='ROC-AUC', color='#d62728')
    
    ax.set_ylabel('Score')
    ax.set_title('Classification Model Performance (Disease Risk)')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha='right')
    ax.legend(loc='lower right')
    
    # Highlight champion
    ax.get_xticklabels()[4].set_fontweight("bold")
    ax.get_xticklabels()[4].set_color("darkred")
    
    # Add values on top of bars
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
                    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "classification_performance.png"))
    plt.close()

# 3. Confusion Matrix
def plot_confusion_matrix():
    data = np.array([[761, 5, 0], [6, 1069, 0], [0, 10, 390]])
    labels = ['Low', 'Medium', 'High']
    
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(data, cmap='Blues')
    plt.colorbar(im)
    
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    
    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax.text(j, i, data[i, j], ha="center", va="center", color="black" if data[i, j] < 500 else "white")
            
    ax.set_title('Confusion Matrix (Gradient Boosting)')
    ax.set_ylabel('True Class')
    ax.set_xlabel('Predicted Class')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"))
    plt.close()

# 4. Feature Importance
def plot_feature_importance():
    features = [
        'Soil_Health_Index', 'Micronutrient_Balance', 'EC', 'Rainfall', 'pH', 
        'Air_Temp_Avg', 'Mn', 'Pathogen_Load_Index', 'Soil_Physical_Cond.', 
        'Climate_Comfort'
    ]
    importances = [0.315, 0.023, 0.023, 0.023, 0.023, 0.022, 0.022, 0.022, 0.022, 0.022]
    
    # Reverse for horizontal bar chart (top to bottom)
    features.reverse()
    importances.reverse()
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(features, importances, color='steelblue')
    # Highlight top feature
    bars[-1].set_color('darkred')
    
    plt.title('Top 10 Feature Importances (Gini)')
    plt.xlabel('Importance Score')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "feature_importance.png"))
    plt.close()

if __name__ == "__main__":
    plot_regression()
    plot_classification()
    plot_confusion_matrix()
    plot_feature_importance()
    print("Plots generated successfully in", OUTPUT_DIR)

"""
train_model.py
Machine Learning Surrogate Model Training Script for ECE Final Year Project

Loads circuit_dataset.csv, preprocesses data, trains a Random Forest Regressor
multi-output surrogate model, computes evaluation metrics (R2, MAE, RMSE),
and exports the trained model as circuit_model.pkl using Joblib.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_surrogate_model():
    dataset_path = "circuit_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset '{dataset_path}' not found. Please run generate_dataset.py first.")
    
    print(f"Loading dataset from '{dataset_path}'...")
    df = pd.read_csv(dataset_path)
    
    feature_cols = ['R1', 'R2', 'RC', 'RE', 'C1', 'C2']
    target_cols = ['Gain', 'Cutoff_Frequency', 'Phase_Margin']
    
    X = df[feature_cols]
    y = df[target_cols]
    
    print(f"Dataset shape: X={X.shape}, y={y.shape}")
    
    # 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor surrogate model...")
    base_rf = RandomForestRegressor(n_estimators=100, max_depth=18, random_state=42, n_jobs=-1)
    model = MultiOutputRegressor(base_rf)
    model.fit(X_train, y_train)
    
    print("\n--- Model Evaluation on Test Set ---")
    y_pred = model.predict(X_test)
    y_pred_df = pd.DataFrame(y_pred, columns=target_cols, index=y_test.index)
    
    overall_r2 = []
    overall_mae = []
    overall_rmse = []
    
    for col in target_cols:
        r2 = r2_score(y_test[col], y_pred_df[col])
        mae = mean_absolute_error(y_test[col], y_pred_df[col])
        rmse = np.sqrt(mean_squared_error(y_test[col], y_pred_df[col]))
        
        overall_r2.append(r2)
        overall_mae.append(mae)
        overall_rmse.append(rmse)
        
        print(f" Target: {col}")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MAE:      {mae:.4f}")
        print(f"   RMSE:     {rmse:.4f}")
        print("-" * 35)
        
    print(f"\nOverall Mean R² Score: {np.mean(overall_r2):.4f}")
    
    # Save model
    model_filename = "circuit_model.pkl"
    joblib.dump({
        'model': model,
        'feature_cols': feature_cols,
        'target_cols': target_cols,
        'metrics': {
            'r2': {col: r2_score(y_test[col], y_pred_df[col]) for col in target_cols},
            'mae': {col: mean_absolute_error(y_test[col], y_pred_df[col]) for col in target_cols},
            'rmse': {col: np.sqrt(mean_squared_error(y_test[col], y_pred_df[col])) for col in target_cols}
        }
    }, model_filename)
    
    print(f"\nTrained surrogate model successfully exported to '{model_filename}'.")

if __name__ == "__main__":
    train_surrogate_model()

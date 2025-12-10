"""
Visualization utilities for training and predictions.

This module contains functions to generate plots for training history,
model predictions, and index comparisons.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from pathlib import Path


def plot_training_history(
    train_losses: List[float],
    val_losses: List[float],
    save_path: str = None,
    show: bool = True
):
    """
    Plot training and validation loss history.
    
    Args:
        train_losses: List of training losses
        val_losses: List of validation losses
        save_path: Optional path to save plot
        show: Whether to show plot

    Returns:
        None
    """
    plt.figure(figsize=(10, 6))
    
    epochs = range(1, len(train_losses) + 1)
    
    plt.plot(epochs, train_losses, 'b-', label='Training Loss', linewidth=2)
    plt.plot(epochs, val_losses, 'r-', label='Validation Loss', linewidth=2)
    
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('Training and Validation Loss', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    
    plt.close()


def plot_predictions(
    actual: np.ndarray,
    predicted: np.ndarray,
    save_path: str = None,
    show: bool = True
):
    """
    Plot actual vs predicted values.
    
    Args:
        actual: Actual values
        predicted: Predicted values
        save_path: Optional path to save plot
        show: Whether to show plot

    Returns:
        None
    """
    plt.figure(figsize=(12, 6))
    
    # Flatten arrays if needed
    if len(actual.shape) > 1:
        actual = actual[:, 0]
    if len(predicted.shape) > 1:
        predicted = predicted[:, 0]
    
    x = range(len(actual))
    
    plt.plot(x, actual, 'b-', label='Actual', linewidth=2, alpha=0.7)
    plt.plot(x, predicted, 'r--', label='Predicted', linewidth=2, alpha=0.7)
    
    plt.xlabel('Sample', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.title('Actual vs Predicted Values', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    
    plt.close()


def plot_indices_comparison(
    indices_data: Dict[str, List[float]],
    save_path: str = None,
    show: bool = True
):
    """
    Plot multiple indices for comparison.
    
    Args:
        indices_data: Dictionary mapping index names to values
        save_path: Optional path to save plot
        show: Whether to show plot

    Returns:
        None
    """
    plt.figure(figsize=(14, 8))
    
    for name, values in indices_data.items():
        plt.plot(values, label=name, linewidth=2, alpha=0.7)
    
    plt.xlabel('Time Step', fontsize=12)
    plt.ylabel('Index Value', fontsize=12)
    plt.title('AI Investment Indices Comparison', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3)
    
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    
    plt.close()

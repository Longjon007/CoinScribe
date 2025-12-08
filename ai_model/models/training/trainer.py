"""
Model Training Module
======================

Handles training, validation, and checkpointing of the AI Index Model.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, List, Tuple, Optional
import numpy as np
from pathlib import Path
import json
from datetime import datetime


class ModelTrainer:
    """Trainer class for the AI Index Model."""
    
    def __init__(
        self,
        model: nn.Module,
        config: Dict,
        device: str = None
    ):
        """
        Initialize the trainer.
        
        Args:
            model: The neural network model
            config: Training configuration dictionary
            device: Device to train on ('cuda' or 'cpu')
        """
        self.model = model
        self.config = config
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        self.model.to(self.device)
        
        # Training components
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=config.get('learning_rate', 0.001)
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            patience=5,
            factor=0.5
        )
        
        # Training state
        self.epoch = 0
        self.best_loss = float('inf')
        self.train_losses = []
        self.val_losses = []
        self.patience_counter = 0
        
        # Checkpoint directory
        self.checkpoint_dir = Path(config.get('checkpoint_dir', 'checkpoints'))
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def train_epoch(
        self,
        train_loader: DataLoader
    ) -> float:
        """
        Train for one epoch.
        
        Args:
            train_loader: DataLoader for training data
            
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            predictions, _ = self.model(data)
            loss = self.criterion(predictions, target)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(
        self,
        val_loader: DataLoader
    ) -> float:
        """
        Validate the model.
        
        Args:
            val_loader: DataLoader for validation data
            
        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                predictions, _ = self.model(data)
                loss = self.criterion(predictions, target)
                
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def train(
        self,
        train_data: Tuple[np.ndarray, np.ndarray],
        val_data: Tuple[np.ndarray, np.ndarray],
        epochs: int = None,
        batch_size: int = None
    ) -> Dict[str, List[float]]:
        """
        Full training loop.
        
        Args:
            train_data: Tuple of (X_train, y_train)
            val_data: Tuple of (X_val, y_val)
            epochs: Number of epochs to train
            batch_size: Batch size for training
            
        Returns:
            Dictionary containing training history
        """
        epochs = epochs or self.config.get('epochs', 100)
        batch_size = batch_size or self.config.get('batch_size', 32)
        patience = self.config.get('early_stopping_patience', 10)
        
        # Create data loaders
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train),
            torch.FloatTensor(y_train)
        )
        val_dataset = TensorDataset(
            torch.FloatTensor(X_val),
            torch.FloatTensor(y_val)
        )
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False
        )
        
        print(f"Training on {self.device}")
        print(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
        
        # Training loop
        for epoch in range(epochs):
            self.epoch = epoch
            
            # Train
            train_loss = self.train_epoch(train_loader)
            self.train_losses.append(train_loss)
            
            # Validate
            val_loss = self.validate(val_loader)
            self.val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Print progress
            print(f"Epoch {epoch+1}/{epochs} - "
                  f"Train Loss: {train_loss:.6f}, "
                  f"Val Loss: {val_loss:.6f}")
            
            # Save best model
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.patience_counter = 0
                self.save_checkpoint('best_model.pth')
                print(f"  → Saved best model (val_loss: {val_loss:.6f})")
            else:
                self.patience_counter += 1
            
            # Early stopping
            if self.patience_counter >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs")
                break
            
            # Save periodic checkpoint
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth')
        
        # Save final model
        self.save_checkpoint('final_model.pth')
        
        # Save training history
        self.save_training_history()
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }
    
    def save_checkpoint(self, filename: str):
        """
        Save model checkpoint.
        
        Args:
            filename: Name of checkpoint file
        """
        checkpoint_path = self.checkpoint_dir / filename
        
        torch.save({
            'epoch': self.epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_loss': self.best_loss
        }, checkpoint_path)
    
    def load_checkpoint(self, filename: str):
        """
        Load model checkpoint.
        
        Args:
            filename: Name of checkpoint file
        """
        checkpoint_path = self.checkpoint_dir / filename
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_path} not found")
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.epoch = checkpoint['epoch']
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
        self.best_loss = checkpoint['best_loss']
    
    def save_training_history(self):
        """Save training history to JSON file."""
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_loss': self.best_loss,
            'final_epoch': self.epoch,
            'timestamp': datetime.now().isoformat()
        }
        
        history_path = self.checkpoint_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)

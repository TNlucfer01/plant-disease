"""
Sample Test Dataset Creator and Accuracy Tester
Creates a test folder with 10-20 random images per class and tests accuracy
"""

import os
import shutil
import random
from pathlib import Path
from plant_disease_cnn import PlantDiseaseCNN
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

def create_test_dataset(val_dir='dataset/val', test_dir='dataset/test', samples_per_class=15):
    """
    Create a test dataset with random samples from validation set
    
    Args:
        val_dir: Source validation directory
        test_dir: Destination test directory
        samples_per_class: Number of samples to take from each class
    """
    print("="*70)
    print("CREATING TEST DATASET")
    print("="*70)
    
    # Remove existing test directory if it exists
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    os.makedirs(test_dir, exist_ok=True)
    
    # Get all class folders
    class_folders = [f for f in os.listdir(val_dir) if os.path.isdir(os.path.join(val_dir, f))]
    
    print(f"\nFound {len(class_folders)} classes")
    print(f"Sampling {samples_per_class} images per class\n")
    
    total_images = 0
    
    for class_name in tqdm(class_folders, desc="Creating test set"):
        source_path = os.path.join(val_dir, class_name)
        dest_path = os.path.join(test_dir, class_name)
        
        # Create destination folder
        os.makedirs(dest_path, exist_ok=True)
        
        # Get all images in this class
        images = [f for f in os.listdir(source_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Randomly sample images
        sample_size = min(samples_per_class, len(images))
        sampled_images = random.sample(images, sample_size)
        
        # Copy sampled images
        for img in sampled_images:
            src = os.path.join(source_path, img)
            dst = os.path.join(dest_path, img)
            shutil.copy2(src, dst)
        
        total_images += sample_size
    
    print(f"\n✅ Test dataset created: {total_images} images across {len(class_folders)} classes")
    print(f"   Location: {test_dir}\n")
    
    return test_dir


def test_model_accuracy(model, test_dir='dataset/test'):
    """
    Test model on all images in test directory and calculate accuracy
    
    Args:
        model: PlantDiseaseCNN model instance
        test_dir: Path to test directory
        
    Returns:
        dict: Results with accuracy per class
    """
    print("="*70)
    print("TESTING MODEL ACCURACY")
    print("="*70)
    
    # Get all class folders
    class_folders = sorted([f for f in os.listdir(test_dir) 
                           if os.path.isdir(os.path.join(test_dir, f))])
    
    results = {}
    total_correct = 0
    total_images = 0
    
    print(f"\nTesting on {len(class_folders)} classes...\n")
    
    for class_name in tqdm(class_folders, desc="Testing"):
        class_path = os.path.join(test_dir, class_name)
        
        # Get all images
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        correct = 0
        predictions = []
        
        for img in images:
            img_path = os.path.join(class_path, img)
            
            try:
                # Get prediction
                result = model.predict(img_path)
                predicted_class = result['raw_class']
                
                # Check if correct
                if predicted_class == class_name:
                    correct += 1
                
                predictions.append({
                    'image': img,
                    'predicted': predicted_class,
                    'confidence': result['confidence']
                })
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        # Calculate accuracy for this class
        accuracy = (correct / len(images) * 100) if len(images) > 0 else 0
        
        results[class_name] = {
            'total': len(images),
            'correct': correct,
            'accuracy': accuracy,
            'predictions': predictions
        }
        
        total_correct += correct
        total_images += len(images)
    
    # Calculate overall accuracy
    overall_accuracy = (total_correct / total_images * 100) if total_images > 0 else 0
    
    results['_overall'] = {
        'total': total_images,
        'correct': total_correct,
        'accuracy': overall_accuracy
    }
    
    return results


def plot_accuracy_bar_chart(results, save_path='test_accuracy.png'):
    """
    Plot accuracy as a bar chart
    
    Args:
        results: Results dictionary from test_model_accuracy
        save_path: Path to save the chart
    """
    print("\n" + "="*70)
    print("GENERATING ACCURACY BAR CHART")
    print("="*70)
    
    # Extract class results (excluding overall)
    classes = []
    accuracies = []
    
    for class_name, data in results.items():
        if class_name != '_overall':
            classes.append(class_name)
            accuracies.append(data['accuracy'])
    
    # Sort by accuracy for better visualization
    sorted_indices = np.argsort(accuracies)
    classes = [classes[i] for i in sorted_indices]
    accuracies = [accuracies[i] for i in sorted_indices]
    
    # Create figure
    plt.figure(figsize=(16, 12))
    
    # Create color gradient based on accuracy
    colors = []
    for acc in accuracies:
        if acc >= 90:
            colors.append('#4caf50')  # Green
        elif acc >= 75:
            colors.append('#8bc34a')  # Light green
        elif acc >= 60:
            colors.append('#ffc107')  # Yellow
        elif acc >= 40:
            colors.append('#ff9800')  # Orange
        else:
            colors.append('#f44336')  # Red
    
    # Create horizontal bar chart
    bars = plt.barh(range(len(classes)), accuracies, color=colors, alpha=0.8, edgecolor='black')
    
    # Customize plot
    plt.yticks(range(len(classes)), classes, fontsize=9)
    plt.xlabel('Accuracy (%)', fontsize=14, fontweight='bold')
    plt.title('Plant Disease Classification Accuracy by Class', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add overall accuracy line
    overall_acc = results['_overall']['accuracy']
    plt.axvline(x=overall_acc, color='blue', linestyle='--', linewidth=2.5,
               label=f'Overall Accuracy: {overall_acc:.1f}%')
    
    # Add value labels on bars
    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        plt.text(acc + 1, i, f'{acc:.1f}%', va='center', fontsize=8)
    
    # Add grid
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add legend
    plt.legend(fontsize=12, loc='lower right')
    
    # Set x-axis limits
    plt.xlim(0, 105)
    
    plt.tight_layout()
    
    # Save figure
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Bar chart saved to: {save_path}")
    
    plt.close()


def print_results_summary(results):
    """Print a summary of test results"""
    print("\n" + "="*70)
    print("ACCURACY TEST RESULTS")
    print("="*70)
    
    overall = results['_overall']
    print(f"\n📊 Overall Results:")
    print(f"   Total Images: {overall['total']}")
    print(f"   Correct Predictions: {overall['correct']}")
    print(f"   Overall Accuracy: {overall['accuracy']:.2f}%")
    
    # Find best and worst
    class_results = {k: v for k, v in results.items() if k != '_overall'}
    best = max(class_results.items(), key=lambda x: x[1]['accuracy'])
    worst = min(class_results.items(), key=lambda x: x[1]['accuracy'])
    
    print(f"\n✅ Best Performing Class:")
    print(f"   {best[0]}: {best[1]['accuracy']:.1f}% ({best[1]['correct']}/{best[1]['total']})")
    
    print(f"\n❌ Worst Performing Class:")
    print(f"   {worst[0]}: {worst[1]['accuracy']:.1f}% ({worst[1]['correct']}/{worst[1]['total']})")
    
    # Classes with 100% accuracy
    perfect = [k for k, v in class_results.items() if v['accuracy'] == 100.0]
    if perfect:
        print(f"\n🎯 Classes with 100% Accuracy ({len(perfect)}):")
        for cls in perfect[:5]:  # Show first 5
            print(f"   - {cls}")
        if len(perfect) > 5:
            print(f"   ... and {len(perfect) - 5} more")
    
    # Classes below 70%
    poor = [(k, v) for k, v in class_results.items() if v['accuracy'] < 70.0]
    if poor:
        print(f"\n⚠️  Classes Below 70% Accuracy ({len(poor)}):")
        for cls, data in sorted(poor, key=lambda x: x[1]['accuracy'])[:5]:
            print(f"   - {cls}: {data['accuracy']:.1f}%")
    
    print("="*70)


def main():
    """Main function"""
    print("\n" + "="*70)
    print("PLANT DISEASE MODEL TESTING")
    print("="*70)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Step 1: Create test dataset
    test_dir = create_test_dataset(
        val_dir='dataset/val',
        test_dir='dataset/test',
        samples_per_class=15  # 15 images per class
    )
    
    # Step 2: Load model
    print("="*70)
    print("LOADING MODEL")
    print("="*70)
    model = PlantDiseaseCNN(num_classes=38, confidence_threshold=0.7)
    model.load_model('best_plant_disease_model.pth')
    print("✅ Model loaded successfully\n")
    
    # Step 3: Test accuracy
    results = test_model_accuracy(model, test_dir)
    
    # Step 4: Print results
    print_results_summary(results)
    
    # Step 5: Plot bar chart
    plot_accuracy_bar_chart(results, save_path='test_accuracy_bar_chart.png')
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("  - test_accuracy_bar_chart.png")
    print("  - dataset/test/ (test dataset folder)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

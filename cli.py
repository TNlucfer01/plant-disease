#!/usr/bin/env python3
"""
Command Line Interface for Plant Disease Detection
Quick testing without the full Streamlit UI
"""

import argparse
import json
from pathlib import Path
from plant_disease_pipeline import PlantDiseaseAssistant


def analyze_single_image(image_path, assistant, save_json=False):
    """Analyze a single image"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {image_path}")
    print('='*60)
    
    result = assistant.analyze_and_display(image_path)
    
    if save_json:
        output_path = Path(image_path).stem + '_result.json'
        assistant.save_result(result, output_path)


def analyze_folder(folder_path, assistant, output_dir='cli_results'):
    """Analyze all images in a folder"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist")
        return
    
    # Get all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    images = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
    
    if not images:
        print(f"No images found in {folder}")
        return
    
    print(f"\nFound {len(images)} images in {folder}")
    print(f"Results will be saved to: {output_dir}/\n")
    
    results = assistant.batch_analyze(folder_path, output_dir)
    
    print("\n" + "="*60)
    print("BATCH ANALYSIS SUMMARY")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        det = result['detection']
        print(f"\n{i}. {Path(result['image_path']).name}")
        print(f"   Plant: {det['plant']}")
        print(f"   Disease: {det['disease']}")
        print(f"   Confidence: {det['confidence']:.1%}")


def interactive_mode(assistant):
    """Interactive command-line mode"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  analyze <image_path>  - Analyze a single image")
    print("  batch <folder_path>   - Analyze all images in folder")
    print("  test                  - Run system test")
    print("  quit                  - Exit")
    print()
    
    while True:
        try:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit' or cmd == 'exit':
                print("Goodbye!")
                break
            
            elif cmd == 'analyze' and len(command) > 1:
                image_path = ' '.join(command[1:])
                analyze_single_image(image_path, assistant, save_json=True)
            
            elif cmd == 'batch' and len(command) > 1:
                folder_path = ' '.join(command[1:])
                analyze_folder(folder_path, assistant)
            
            elif cmd == 'test':
                print("\nRunning system test...")
                import test_system
                test_system.main()
            
            else:
                print("Unknown command. Try: analyze <path>, batch <folder>, test, or quit")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Plant Disease Detection - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg                    # Analyze single image
  %(prog)s image.jpg --save             # Analyze and save JSON
  %(prog)s --folder images/             # Analyze folder
  %(prog)s --interactive                # Interactive mode
  %(prog)s --test                       # Run system test

For the full web interface, use:
  streamlit run app.py
        """
    )
    
    parser.add_argument(
        'image',
        nargs='?',
        help='Path to image file'
    )
    
    parser.add_argument(
        '--folder',
        '-f',
        help='Analyze all images in folder'
    )
    
    parser.add_argument(
        '--save',
        '-s',
        action='store_true',
        help='Save results as JSON'
    )
    
    parser.add_argument(
        '--interactive',
        '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--test',
        '-t',
        action='store_true',
        help='Run system test'
    )
    
    parser.add_argument(
        '--confidence',
        '-c',
        type=float,
        default=0.7,
        help='Confidence threshold (default: 0.7)'
    )
    
    parser.add_argument(
        '--model',
        '-m',
        default='llama3.2:3b',
        help='Ollama model name (default: llama3.2:3b)'
    )
    
    parser.add_argument(
        '--num-classes',
        '-n',
        type=int,
        default=38,
        help='Number of disease classes (default: 38)'
    )
    
    args = parser.parse_args()
    
    # Run system test
    if args.test:
        import test_system
        test_system.main()
        return
    
    # Initialize assistant
    print("\n🌿 Plant Disease Detection CLI")
    print("Initializing system...\n")
    
    assistant = PlantDiseaseAssistant(
        num_classes=args.num_classes,
        confidence_threshold=args.confidence,
        llm_model=args.model
    )
    
    # Interactive mode
    if args.interactive:
        interactive_mode(assistant)
        return
    
    # Batch folder analysis
    if args.folder:
        analyze_folder(args.folder, assistant)
        return
    
    # Single image analysis
    if args.image:
        analyze_single_image(args.image, assistant, save_json=args.save)
        return
    
    # No arguments - show help
    parser.print_help()


if __name__ == '__main__':
    main()

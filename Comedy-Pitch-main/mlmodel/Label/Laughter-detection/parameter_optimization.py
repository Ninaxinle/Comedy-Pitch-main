#!/usr/bin/env python3
"""
🎯 Systematic Parameter Optimization for Laughter Detection

This script systematically tests different parameter combinations in inference.py
to find the optimal settings for best laughter detection performance.
"""

import os
import json
import subprocess
import pandas as pd
from itertools import product
import time
from datetime import datetime

class LaughterDetectionOptimizer:
    def __init__(self, audio_path, manual_labels_path, output_base_dir="optimization_results"):
        self.audio_path = audio_path
        self.manual_labels_path = manual_labels_path
        self.output_base_dir = output_base_dir
        self.results = []
        
        # Create output directory
        os.makedirs(output_base_dir, exist_ok=True)
        
    def get_parameter_combinations(self):
        """Define all adjustable parameters and their test values"""
        
        # 🎯 IDENTIFIED ADJUSTABLE PARAMETERS:
        
        # 1. Detection Threshold (Line 147 in inference.py)
        # Controls sensitivity: higher = fewer detections, lower = more detections
        detection_thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        
        # 2. Segment Length (Line 85: input_sec parameter)
        # Length of audio segments processed by the model
        segment_lengths = [5, 6, 7, 8, 9]
        
        # 3. Overlap Between Segments (Line 95: over_lap_sec)
        # Reduces missed laughter at segment boundaries
        overlap_seconds = [1.0, 1.5, 2.0, 2.5, 3.0]
        
        # 4. Batch Size (Line 85: batch_size parameter)
        # Affects memory usage and processing speed
        batch_sizes = [5, 10, 15, 20]
        
        # 5. Audio Amplification Factor (Line 60: mul_fac in custom_amplituder_small_portion)
        # Amplifies silent portions to improve detection
        amplification_factors = [3, 4, 5, 6, 7]
        
        # 6. Post-processing: Concat Close Threshold (Line 200: concat_close parameter)
        # Merges laughter segments that are close together
        concat_thresholds = [0.1, 0.2, 0.3, 0.4]
        
        # 7. Post-processing: Remove Short Threshold (Line 201: remove_short parameter)
        # Removes laughter segments that are too short
        remove_short_thresholds = [0.1, 0.2, 0.3, 0.4]
        
        # 8. IoU Threshold for Validation (in standalone_validation.py)
        # How strict the validation should be
        iou_thresholds = [0.2, 0.3, 0.4, 0.5]
        
        # Create all combinations (this will be a lot!)
        all_params = [
            detection_thresholds,
            segment_lengths,
            overlap_seconds,
            batch_sizes,
            amplification_factors,
            concat_thresholds,
            remove_short_thresholds,
            iou_thresholds
        ]
        
        # Generate all combinations
        combinations = list(product(*all_params))
        
        print(f"🎯 Total parameter combinations to test: {len(combinations)}")
        print("⚠️  This will take a while! Consider reducing parameter ranges for faster testing.")
        
        return combinations
    
    def modify_inference_script(self, params):
        """Set environment variables for parameters instead of modifying files"""
        
        # Unpack parameters
        (detection_threshold, segment_length, overlap_sec, batch_size, 
         amplification_factor, concat_threshold, remove_short_threshold, iou_threshold) = params
        
        # Set environment variables (these will be read by inference.py)
        import os
        os.environ['DETECTION_THRESHOLD'] = str(detection_threshold)
        os.environ['SEGMENT_LENGTH'] = str(segment_length)
        os.environ['OVERLAP_SEC'] = str(overlap_sec)
        os.environ['BATCH_SIZE'] = str(batch_size)
        os.environ['AMPLIFICATION_FACTOR'] = str(amplification_factor)
        os.environ['CONCAT_THRESHOLD'] = str(concat_threshold)
        os.environ['REMOVE_THRESHOLD'] = str(remove_short_threshold)
        
        return iou_threshold
    
    def run_inference(self, params):
        """Run inference with current parameters"""
        try:
            # Create unique output directory for this combination
            param_id = f"det{params[0]}_seg{params[1]}_over{params[2]}_batch{params[3]}_amp{params[4]}_concat{params[5]}_remove{params[6]}"
            output_dir = os.path.join(self.output_base_dir, param_id)
            
            # Run inference
            cmd = [
                'python', 'inference.py',
                '--audio_path', self.audio_path,
                '--output_dir', output_dir
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ Inference failed for {param_id}: {result.stderr}")
                return None
            
            return output_dir
            
        except Exception as e:
            print(f"❌ Error running inference: {e}")
            return None
    
    def run_validation(self, output_dir, iou_threshold):
        """Run validation and get F1 score"""
        try:
            # Temporarily modify standalone_validation.py with new IoU threshold
            with open('standalone_validation.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified_content = content.replace(
                'iou_threshold=0.3',
                f'iou_threshold={iou_threshold}'
            )
            
            with open('validation_temp.py', 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Run validation
            cmd = ['python', 'validation_temp.py']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ Validation failed: {result.stderr}")
                return None
            
            # Extract F1 score from output
            output_lines = result.stdout.split('\n')
            f1_score = None
            
            for line in output_lines:
                if 'F1 Score:' in line:
                    try:
                        f1_score = float(line.split(':')[1].strip())
                        break
                    except:
                        continue
            
            return f1_score
            
        except Exception as e:
            print(f"❌ Error running validation: {e}")
            return None
    
    def test_parameter_combination(self, params, combination_index, total_combinations):
        """Test a single parameter combination"""
        
        print(f"\n🔬 Testing combination {combination_index + 1}/{total_combinations}")
        print(f"Parameters: Detection={params[0]}, Segment={params[1]}s, Overlap={params[2]}s, "
              f"Batch={params[3]}, Amp={params[4]}, Concat={params[5]}, Remove={params[6]}, IoU={params[7]}")
        
        start_time = time.time()
        
        # Modify inference script
        iou_threshold = self.modify_inference_script(params)
        
        # Run inference
        output_dir = self.run_inference(params)
        if output_dir is None:
            return None
        
        # Run validation
        f1_score = self.run_validation(output_dir, iou_threshold)
        if f1_score is None:
            return None
        
        # Clean up temporary files
        for temp_file in ['validation_temp.py']:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        elapsed_time = time.time() - start_time
        
        # Store results
        result = {
            'combination_id': combination_index,
            'detection_threshold': params[0],
            'segment_length': params[1],
            'overlap_seconds': params[2],
            'batch_size': params[3],
            'amplification_factor': params[4],
            'concat_threshold': params[5],
            'remove_short_threshold': params[6],
            'iou_threshold': params[7],
            'f1_score': f1_score,
            'elapsed_time': elapsed_time,
            'output_dir': output_dir
        }
        
        self.results.append(result)
        
        print(f"✅ F1 Score: {f1_score:.3f} (Time: {elapsed_time:.1f}s)")
        
        return result
    
    def optimize(self, max_combinations=None):
        """Run the complete optimization process"""
        
        print("🚀 Starting Laughter Detection Parameter Optimization")
        print("=" * 60)
        
        # Get all parameter combinations
        combinations = self.get_parameter_combinations()
        
        if max_combinations:
            combinations = combinations[:max_combinations]
            print(f"🔧 Testing first {max_combinations} combinations for faster results")
        
        # Test each combination
        for i, params in enumerate(combinations):
            result = self.test_parameter_combination(params, i, len(combinations))
            
            # Save intermediate results every 10 combinations
            if (i + 1) % 10 == 0:
                self.save_results()
        
        # Save final results
        self.save_results()
        
        # Show best results
        self.show_best_results()
    
    def save_results(self):
        """Save results to CSV file"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimization_results_{timestamp}.csv"
        filepath = os.path.join(self.output_base_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"💾 Results saved to: {filepath}")
    
    def show_best_results(self):
        """Display the best performing parameter combinations"""
        if not self.results:
            print("❌ No results to display")
            return
        
        # Sort by F1 score
        sorted_results = sorted(self.results, key=lambda x: x['f1_score'], reverse=True)
        
        print("\n🏆 TOP 10 BEST PARAMETER COMBINATIONS:")
        print("=" * 80)
        
        for i, result in enumerate(sorted_results[:10]):
            print(f"\n{i+1}. F1 Score: {result['f1_score']:.3f}")
            print(f"   Detection Threshold: {result['detection_threshold']}")
            print(f"   Segment Length: {result['segment_length']}s")
            print(f"   Overlap: {result['overlap_seconds']}s")
            print(f"   Batch Size: {result['batch_size']}")
            print(f"   Amplification: {result['amplification_factor']}")
            print(f"   Concat Threshold: {result['concat_threshold']}")
            print(f"   Remove Short: {result['remove_short_threshold']}")
            print(f"   IoU Threshold: {result['iou_threshold']}")
            print(f"   Time: {result['elapsed_time']:.1f}s")
        
        # Show best overall
        best = sorted_results[0]
        print(f"\n🎯 BEST OVERALL COMBINATION:")
        print(f"   F1 Score: {best['f1_score']:.3f}")
        print(f"   Parameters: {best}")
        
        # Save best parameters to file
        best_params_file = os.path.join(self.output_base_dir, "best_parameters.json")
        with open(best_params_file, 'w') as f:
            json.dump(best, f, indent=2)
        print(f"💾 Best parameters saved to: {best_params_file}")

def main():
    """Main function to run optimization"""
    
    # Configuration
    audio_path = "test-data/Aziz Ansari - Dangerously Delicious - Texting With Girls.wav"
    manual_labels_path = "test-data/Aziz Ansari - Dangerously Delicious - Texting With Girls_laughter_segments.csv"
    
    # Check if files exist
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return
    
    if not os.path.exists(manual_labels_path):
        print(f"❌ Manual labels not found: {manual_labels_path}")
        return
    
    # Create optimizer
    optimizer = LaughterDetectionOptimizer(audio_path, manual_labels_path)
    
    # Run optimization (limit to first 50 combinations for faster testing)
    optimizer.optimize(max_combinations=50)

if __name__ == "__main__":
    main() 
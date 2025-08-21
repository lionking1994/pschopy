#!/usr/bin/env python3
"""
Data Analysis Script for Mood Induction + SART Study
Provides basic analysis functions for the collected data.
"""

import pandas as pd
import numpy as np
# FIXED: Set matplotlib backend before importing pyplot to avoid GUI issues
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless environments
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add config to path
sys.path.append(str(Path(__file__).parent.parent / 'config'))
import experiment_config as config

class MoodSARTAnalyzer:
    """Data analyzer for the Mood SART experiment"""
    
    def __init__(self, data_file=None):
        """Initialize analyzer with data file"""
        if data_file:
            self.data = pd.read_csv(data_file)
        else:
            self.data = None
    
    def load_data(self, data_file):
        """Load data from CSV file"""
        self.data = pd.read_csv(data_file)
        print(f"Loaded data with {len(self.data)} rows")
    
    def combine_data_files(self, data_dir):
        """Combine multiple participant data files"""
        data_dir = Path(data_dir)
        csv_files = list(data_dir.glob("participant_*.csv"))
        
        if not csv_files:
            print("No participant data files found")
            return
        
        combined_data = []
        for file in csv_files:
            df = pd.read_csv(file)
            combined_data.append(df)
        
        self.data = pd.concat(combined_data, ignore_index=True)
        print(f"Combined {len(csv_files)} files with {len(self.data)} total rows")
    
    def get_basic_stats(self):
        """Get basic descriptive statistics"""
        if self.data is None:
            print("No data loaded")
            return
        
        print("=== BASIC STATISTICS ===")
        print(f"Total participants: {self.data['participant_code'].nunique()}")
        print(f"Total trials: {len(self.data)}")
        
        # SART performance
        sart_data = self.data[self.data['phase'] == 'sart_task'].copy()
        if len(sart_data) > 0:
            print(f"\nSART Performance:")
            print(f"  Total SART trials: {len(sart_data)}")
            print(f"  Overall accuracy: {sart_data['accuracy'].mean():.3f}")
            print(f"  Mean RT (correct trials): {sart_data[sart_data['accuracy']==1]['reaction_time'].mean():.3f}s")
            
            # By condition
            for condition in ['RI', 'NRI']:
                cond_data = sart_data[sart_data['block_type'] == condition]
                if len(cond_data) > 0:
                    print(f"  {condition} accuracy: {cond_data['accuracy'].mean():.3f}")
                    print(f"  {condition} RT: {cond_data[cond_data['accuracy']==1]['reaction_time'].mean():.3f}s")
        
        # Mood ratings
        mood_data = self.data[self.data['phase'].str.contains('mood_rating', na=False)].copy()
        if len(mood_data) > 0:
            print(f"\nMood Ratings:")
            print(f"  Mean mood rating: {mood_data['mood_rating'].mean():.2f}")
            print(f"  Mood rating range: {mood_data['mood_rating'].min():.2f} - {mood_data['mood_rating'].max():.2f}")
        
        # Mind-wandering probes
        mw_data = self.data[self.data['phase'] == 'mind_wandering_probe'].copy()
        if len(mw_data) > 0:
            print(f"\nMind-Wandering Probes:")
            print(f"  Mean TUT rating: {mw_data['mw_tut_rating'].mean():.2f}")
            print(f"  Mean FMT rating: {mw_data['mw_fmt_rating'].mean():.2f}")
    
    def analyze_sart_performance(self):
        """Detailed SART performance analysis"""
        sart_data = self.data[self.data['phase'] == 'sart_task'].copy()
        
        if len(sart_data) == 0:
            print("No SART data found")
            return
        
        print("=== SART PERFORMANCE ANALYSIS ===")
        
        # Overall performance
        print("Overall Performance:")
        print(f"  Accuracy: {sart_data['accuracy'].mean():.3f} ± {sart_data['accuracy'].std():.3f}")
        
        correct_trials = sart_data[sart_data['accuracy'] == 1]
        print(f"  RT (correct): {correct_trials['reaction_time'].mean():.3f} ± {correct_trials['reaction_time'].std():.3f}s")
        
        # By condition
        print("\nBy Condition:")
        for condition in ['RI', 'NRI']:
            cond_data = sart_data[sart_data['block_type'] == condition]
            if len(cond_data) > 0:
                print(f"  {condition}:")
                print(f"    Accuracy: {cond_data['accuracy'].mean():.3f} ± {cond_data['accuracy'].std():.3f}")
                cond_correct = cond_data[cond_data['accuracy'] == 1]
                if len(cond_correct) > 0:
                    print(f"    RT: {cond_correct['reaction_time'].mean():.3f} ± {cond_correct['reaction_time'].std():.3f}s")
        
        # Target vs non-target analysis (for RI condition)
        ri_data = sart_data[sart_data['block_type'] == 'RI']
        if len(ri_data) > 0:
            target_trials = ri_data[ri_data['stimulus'] == 3]
            nontarget_trials = ri_data[ri_data['stimulus'] != 3]
            
            print(f"\nResponse Inhibition Analysis:")
            if len(target_trials) > 0:
                print(f"  Target trials (should not respond): {target_trials['accuracy'].mean():.3f} accuracy")
                print(f"  Commission errors: {(1 - target_trials['accuracy'].mean()):.3f}")
            
            if len(nontarget_trials) > 0:
                print(f"  Non-target trials: {nontarget_trials['accuracy'].mean():.3f} accuracy")
                print(f"  Omission errors: {(1 - nontarget_trials['accuracy'].mean()):.3f}")
    
    def analyze_mood_effects(self):
        """Analyze mood induction effects"""
        mood_data = self.data[self.data['phase'].str.contains('mood_rating', na=False)].copy()
        
        if len(mood_data) == 0:
            print("No mood rating data found")
            return
        
        print("=== MOOD ANALYSIS ===")
        
        # Extract mood phases
        mood_data['mood_phase'] = mood_data['phase'].str.replace('mood_rating_', '')
        
        print("Mood ratings by phase:")
        for phase in mood_data['mood_phase'].unique():
            phase_data = mood_data[mood_data['mood_phase'] == phase]
            print(f"  {phase}: {phase_data['mood_rating'].mean():.2f} ± {phase_data['mood_rating'].std():.2f}")
    
    def analyze_mind_wandering(self):
        """Analyze mind-wandering probe responses"""
        mw_data = self.data[self.data['phase'] == 'mind_wandering_probe'].copy()
        
        if len(mw_data) == 0:
            print("No mind-wandering data found")
            return
        
        print("=== MIND-WANDERING ANALYSIS ===")
        
        print("Overall mind-wandering:")
        print(f"  TUT rating: {mw_data['mw_tut_rating'].mean():.2f} ± {mw_data['mw_tut_rating'].std():.2f}")
        print(f"  FMT rating: {mw_data['mw_fmt_rating'].mean():.2f} ± {mw_data['mw_fmt_rating'].std():.2f}")
        
        # By SART condition
        print("\nBy SART condition:")
        for condition in ['RI', 'NRI']:
            cond_data = mw_data[mw_data['block_type'] == condition]
            if len(cond_data) > 0:
                print(f"  {condition}:")
                print(f"    TUT: {cond_data['mw_tut_rating'].mean():.2f} ± {cond_data['mw_tut_rating'].std():.2f}")
                print(f"    FMT: {cond_data['mw_fmt_rating'].mean():.2f} ± {cond_data['mw_fmt_rating'].std():.2f}")
    
    def create_plots(self, output_dir=None):
        """Create visualization plots - FIXED for headless environments"""
        if self.data is None:
            print("❌ No data loaded")
            return
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            print(f"📊 Creating plots in: {output_dir}")
        else:
            print("📊 Creating plots (no output directory specified)")
        
        # Set style for better-looking plots
        plt.style.use('default')
        plt.rcParams['figure.facecolor'] = 'white'
        
        # SART performance by condition
        sart_data = self.data[self.data['phase'] == 'sart_task'].copy()
        if len(sart_data) > 0:
            print("📈 Creating SART performance plots...")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Accuracy by condition
            accuracy_by_cond = sart_data.groupby('block_type')['accuracy'].mean()
            accuracy_by_cond.plot(kind='bar', ax=ax1, color=['skyblue', 'lightcoral'])
            ax1.set_title('SART Accuracy by Condition')
            ax1.set_ylabel('Accuracy')
            ax1.set_xlabel('Condition')
            ax1.set_ylim(0, 1)
            
            # RT by condition (correct trials only)
            correct_sart = sart_data[sart_data['accuracy'] == 1]
            rt_by_cond = correct_sart.groupby('block_type')['reaction_time'].mean()
            rt_by_cond.plot(kind='bar', ax=ax2, color=['skyblue', 'lightcoral'])
            ax2.set_title('SART Reaction Time by Condition')
            ax2.set_ylabel('Reaction Time (s)')
            ax2.set_xlabel('Condition')
            
            plt.tight_layout()
            if output_dir:
                plt.savefig(output_dir / 'sart_performance.png', dpi=300, bbox_inches='tight')
                print(f"✅ Saved SART performance plot: {output_dir / 'sart_performance.png'}")
            plt.close()  # FIXED: Close instead of show for headless compatibility
        
        # Mood ratings over time
        mood_data = self.data[self.data['phase'].str.contains('mood_rating', na=False)].copy()
        if len(mood_data) > 0:
            print("📈 Creating mood ratings plot...")
            mood_data['mood_phase'] = mood_data['phase'].str.replace('mood_rating_', '')
            
            plt.figure(figsize=(10, 6))
            mood_summary = mood_data.groupby('mood_phase')['mood_rating'].agg(['mean', 'std'])
            # FIXED: Remove capsize parameter and fix fill_between
            x_pos = range(len(mood_summary))
            plt.plot(x_pos, mood_summary['mean'], marker='o', linewidth=2, markersize=8)
            
            # Add error bars if std is available
            valid_std = mood_summary['std'].fillna(0)
            plt.fill_between(x_pos, 
                           mood_summary['mean'] - valid_std,
                           mood_summary['mean'] + valid_std,
                           alpha=0.3)
            plt.title('Mood Ratings Throughout Experiment')
            plt.ylabel('Mood Rating')
            plt.xlabel('Phase')
            plt.xticks(x_pos, mood_summary.index, rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if output_dir:
                plt.savefig(output_dir / 'mood_ratings.png', dpi=300, bbox_inches='tight')
                print(f"✅ Saved mood ratings plot: {output_dir / 'mood_ratings.png'}")
            plt.close()  # FIXED: Close instead of show for headless compatibility
        
        # Mind-wandering by condition
        mw_data = self.data[self.data['phase'] == 'mind_wandering_probe'].copy()
        if len(mw_data) > 0:
            print("📈 Creating mind-wandering plots...")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # TUT by condition
            tut_by_cond = mw_data.groupby('block_type')['mw_tut_rating'].mean()
            tut_by_cond.plot(kind='bar', ax=ax1, color=['lightgreen', 'orange'])
            ax1.set_title('Task-Unrelated Thought by Condition')
            ax1.set_ylabel('TUT Rating')
            ax1.set_xlabel('Condition')
            
            # FMT by condition
            fmt_by_cond = mw_data.groupby('block_type')['mw_fmt_rating'].mean()
            fmt_by_cond.plot(kind='bar', ax=ax2, color=['lightgreen', 'orange'])
            ax2.set_title('Freely Moving Thought by Condition')
            ax2.set_ylabel('FMT Rating')
            ax2.set_xlabel('Condition')
            
            plt.tight_layout()
            if output_dir:
                plt.savefig(output_dir / 'mind_wandering.png', dpi=300, bbox_inches='tight')
                print(f"✅ Saved mind-wandering plot: {output_dir / 'mind_wandering.png'}")
            plt.close()  # FIXED: Close instead of show for headless compatibility
    
    def export_summary(self, output_file):
        """Export summary statistics to file"""
        if self.data is None:
            print("No data loaded")
            return
        
        summary = {}
        
        # Basic info
        summary['total_participants'] = self.data['participant_code'].nunique()
        summary['total_trials'] = len(self.data)
        
        # SART performance
        sart_data = self.data[self.data['phase'] == 'sart_task']
        if len(sart_data) > 0:
            summary['sart_accuracy'] = sart_data['accuracy'].mean()
            summary['sart_rt'] = sart_data[sart_data['accuracy']==1]['reaction_time'].mean()
            
            for condition in ['RI', 'NRI']:
                cond_data = sart_data[sart_data['block_type'] == condition]
                if len(cond_data) > 0:
                    summary[f'{condition}_accuracy'] = cond_data['accuracy'].mean()
                    summary[f'{condition}_rt'] = cond_data[cond_data['accuracy']==1]['reaction_time'].mean()
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(output_file, index=False)
        print(f"Summary exported to {output_file}")

def main():
    """Main function for running analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Mood SART experiment data')
    parser.add_argument('--data_file', type=str, help='Single data file to analyze')
    parser.add_argument('--data_dir', type=str, default='../data', help='Directory containing data files')
    parser.add_argument('--output_dir', type=str, help='Directory for output plots')
    parser.add_argument('--combine', action='store_true', help='Combine multiple data files')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = MoodSARTAnalyzer()
    
    # Load data
    if args.data_file:
        analyzer.load_data(args.data_file)
    elif args.combine:
        analyzer.combine_data_files(args.data_dir)
    else:
        print("Please specify either --data_file or --combine with --data_dir")
        return
    
    # Run analyses
    analyzer.get_basic_stats()
    print("\n" + "="*50 + "\n")
    analyzer.analyze_sart_performance()
    print("\n" + "="*50 + "\n")
    analyzer.analyze_mood_effects()
    print("\n" + "="*50 + "\n")
    analyzer.analyze_mind_wandering()
    
    # Create plots
    if args.output_dir:
        analyzer.create_plots(args.output_dir)
    
    # Export summary
    if args.output_dir:
        analyzer.export_summary(Path(args.output_dir) / 'summary_stats.csv')

if __name__ == '__main__':
    main() 
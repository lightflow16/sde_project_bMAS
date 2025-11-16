"""
Results aggregator for generating comparison tables similar to paper format.

Generates:
- Table 1: Performance comparison across benchmarks
- Table 3: Token cost and performance comparison
"""
import os
import json
from typing import Dict, Any, List, Optional
from collections import defaultdict


class ResultsAggregator:
    """Aggregates results across benchmarks and generates comparison tables."""
    
    def __init__(self, results_dir: str = "benchmark_evaluator/results"):
        """Initialize results aggregator."""
        self.results_dir = results_dir
    
    def load_benchmark_results(self, benchmark_name: str) -> Dict[str, Any]:
        """Load results for a benchmark."""
        filepath = os.path.join(self.results_dir, f"{benchmark_name}_summary.json")
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def aggregate_all_benchmarks(self, benchmark_names: List[str]) -> Dict[str, Any]:
        """Aggregate results across all benchmarks."""
        all_results = {}
        
        for benchmark_name in benchmark_names:
            summary = self.load_benchmark_results(benchmark_name)
            if summary:
                all_results[benchmark_name] = summary
        
        return all_results
    
    def generate_performance_table(self, benchmark_results: Dict[str, Dict[str, Any]],
                                   output_file: Optional[str] = None) -> str:
        """
        Generate Table 1: Performance comparison across benchmarks.
        
        Format similar to paper Table 1:
        Method | MMLU | ARC-Challenge | GPQA-Diamond | BBH | MATH | GSM8K | Avg.
        """
        # System order (as in paper)
        system_order = ['cot', 'static_mas', 'orig_bMAS', 'bMAS']
        system_display_names = {
            'cot': 'CoT',
            'static_mas': 'Static MAS',
            'orig_bMAS': 'orig_impl_bMAS',
            'bMAS': 'LbMAS'
        }
        
        # Benchmark order
        benchmark_order = ['mmlu', 'arc_challenge', 'gpqa_diamond', 'bbh', 'math', 'gsm8k']
        benchmark_display_names = {
            'mmlu': 'MMLU',
            'arc_challenge': 'ARC-Challenge',
            'gpqa_diamond': 'GPQA-Diamond',
            'bbh': 'BBH',
            'math': 'MATH',
            'gsm8k': 'GSM8K'
        }
        
        # Collect data
        table_data = {}
        for system_name in system_order:
            table_data[system_name] = {}
            for benchmark_name in benchmark_order:
                if benchmark_name in benchmark_results:
                    summary = benchmark_results[benchmark_name]
                    if system_name in summary.get('systems', {}):
                        metrics = summary['systems'][system_name]
                        table_data[system_name][benchmark_name] = metrics['accuracy']
                    else:
                        table_data[system_name][benchmark_name] = None
                else:
                    table_data[system_name][benchmark_name] = None
        
        # Calculate averages
        for system_name in system_order:
            accuracies = [v for v in table_data[system_name].values() if v is not None]
            table_data[system_name]['avg'] = sum(accuracies) / len(accuracies) if accuracies else None
        
        # Generate table
        lines = []
        lines.append("="*100)
        lines.append("Table 1: Comparing MAS systems across benchmarks. Accuracy (%)")
        lines.append("="*100)
        lines.append("")
        
        # Header
        header = f"{'Method':<20}"
        for bench in benchmark_order:
            header += f" {benchmark_display_names[bench]:<15}"
        header += f" {'Avg.':<10}"
        lines.append(header)
        lines.append("-"*100)
        
        # Rows
        for system_name in system_order:
            if system_name not in table_data:
                continue
            
            row = f"{system_display_names.get(system_name, system_name):<20}"
            for bench in benchmark_order:
                acc = table_data[system_name].get(bench)
                if acc is not None:
                    row += f" {acc:>14.2f}%"
                else:
                    row += f" {'N/A':>14}"
            
            avg = table_data[system_name].get('avg')
            if avg is not None:
                row += f" {avg:>9.2f}%"
            else:
                row += f" {'N/A':>9}"
            
            lines.append(row)
        
        lines.append("")
        lines.append("="*100)
        
        table_text = "\n".join(lines)
        
        # Save to file
        if output_file:
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(table_text)
            print(f"Saved performance table to {output_file}")
        
        return table_text
    
    def generate_token_cost_table(self, benchmark_results: Dict[str, Dict[str, Any]],
                                  benchmark_name: str = "math",
                                  output_file: Optional[str] = None) -> str:
        """
        Generate Table 3: Token cost and performance comparison.
        
        Format similar to paper Table 3:
        Method | Prompt tokens | Completion tokens | Total tokens | Performance
        """
        if benchmark_name not in benchmark_results:
            return f"No results found for benchmark: {benchmark_name}"
        
        summary = benchmark_results[benchmark_name]
        
        # System order
        system_order = ['cot', 'static_mas', 'orig_bMAS', 'bMAS']
        system_display_names = {
            'cot': 'CoT',
            'static_mas': 'Static MAS',
            'orig_bMAS': 'orig_impl_bMAS',
            'bMAS': 'LbMAS'
        }
        
        # Collect data
        table_data = []
        for system_name in system_order:
            if system_name in summary.get('systems', {}):
                metrics = summary['systems'][system_name]
                table_data.append({
                    'system': system_display_names.get(system_name, system_name),
                    'prompt_tokens': metrics.get('prompt_tokens', 0),
                    'completion_tokens': metrics.get('completion_tokens', 0),
                    'total_tokens': metrics.get('total_tokens', 0),
                    'accuracy': metrics.get('accuracy', 0)
                })
        
        # Sort by total tokens (ascending)
        table_data.sort(key=lambda x: x['total_tokens'])
        
        # Generate table
        lines = []
        lines.append("="*100)
        lines.append(f"Table 3: Comparing token cost and performance on {benchmark_name.upper()} dataset")
        lines.append("The lowest total tokens and highest performances are highlighted.")
        lines.append("="*100)
        lines.append("")
        
        # Header
        header = f"{'Method':<20} {'Prompt Token':<15} {'Completion Token':<18} {'Total Token':<15} {'Performance':<12}"
        lines.append(header)
        lines.append("-"*100)
        
        # Find best values for highlighting
        min_tokens = min(d['total_tokens'] for d in table_data) if table_data else 0
        max_accuracy = max(d['accuracy'] for d in table_data) if table_data else 0
        
        # Rows
        for data in table_data:
            row = f"{data['system']:<20}"
            row += f" {data['prompt_tokens']:>14,}"
            row += f" {data['completion_tokens']:>17,}"
            
            # Highlight lowest total tokens
            if data['total_tokens'] == min_tokens:
                row += f" {data['total_tokens']:>14,} **"
            else:
                row += f" {data['total_tokens']:>14,}"
            
            # Highlight highest accuracy
            if data['accuracy'] == max_accuracy:
                row += f" {data['accuracy']:>11.2f}% **"
            else:
                row += f" {data['accuracy']:>11.2f}%"
            
            lines.append(row)
        
        lines.append("")
        lines.append("** = Best in category")
        lines.append("="*100)
        
        table_text = "\n".join(lines)
        
        # Save to file
        if output_file:
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(table_text)
            print(f"Saved token cost table to {output_file}")
        
        return table_text
    
    def generate_markdown_report(self, benchmark_results: Dict[str, Dict[str, Any]],
                                  output_file: Optional[str] = None) -> str:
        """Generate a comprehensive markdown report."""
        lines = []
        lines.append("# Benchmark Evaluation Report")
        lines.append("")
        lines.append(f"Generated: {benchmark_results.get('timestamp', 'N/A')}")
        lines.append("")
        
        # Performance table
        lines.append("## Performance Comparison (Table 1)")
        lines.append("")
        perf_table = self.generate_performance_table(benchmark_results)
        lines.append("```")
        lines.append(perf_table)
        lines.append("```")
        lines.append("")
        
        # Token cost table for MATH
        if 'math' in benchmark_results:
            lines.append("## Token Cost Comparison on MATH Dataset (Table 3)")
            lines.append("")
            token_table = self.generate_token_cost_table(benchmark_results, 'math')
            lines.append("```")
            lines.append(token_table)
            lines.append("```")
            lines.append("")
        
        # Detailed results per benchmark
        lines.append("## Detailed Results by Benchmark")
        lines.append("")
        
        for benchmark_name, summary in benchmark_results.items():
            lines.append(f"### {benchmark_name.upper()}")
            lines.append("")
            
            if 'systems' in summary:
                lines.append("| System | Accuracy | Total Tokens | Avg Time | Avg Rounds |")
                lines.append("|--------|----------|--------------|----------|------------|")
                
                for system_name, metrics in summary['systems'].items():
                    lines.append(
                        f"| {metrics['display_name']} | "
                        f"{metrics['accuracy']:.2f}% | "
                        f"{metrics['total_tokens']:,} | "
                        f"{metrics['avg_time_per_problem']:.2f}s | "
                        f"{metrics['avg_rounds']:.2f} |"
                    )
            
            lines.append("")
        
        report_text = "\n".join(lines)
        
        # Save to file
        if output_file:
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(report_text)
            print(f"Saved markdown report to {output_file}")
        
        return report_text


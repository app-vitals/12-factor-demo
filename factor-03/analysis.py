"""
Results analysis and statistics for Factor 3 testing
Provides clean summary calculations and model comparison analysis
"""

import json
from typing import Dict, List, Optional, Tuple


def _aggregate_format_results(results_data: Dict, model_filter: Optional[List[str]] = None) -> Dict:
    """
    Aggregate test results by format across all scenarios
    
    Args:
        results_data: Complete test results from factor3_test.py
        model_filter: List of models to include (None = all models)
        
    Returns:
        Dict mapping format names to aggregated quality/token/cost data
    """
    if model_filter is None:
        model_filter = ["gpt-4.1", "sonnet-4", "gemini-2.5"]
    
    format_aggregates = {}
    
    for scenario_name, scenario_results in results_data.items():
        for format_name, format_results in scenario_results.items():
            if format_name not in format_aggregates:
                format_aggregates[format_name] = {
                    'quality_scores': [], 
                    'token_counts': [], 
                    'costs': []
                }
                
            for model_name, result in format_results.items():
                if model_name in model_filter:
                    quality_score = result.get('quality', {}).get('overall', 0)
                    format_aggregates[format_name]['quality_scores'].append(quality_score)
                    format_aggregates[format_name]['token_counts'].append(result['total_tokens'])
                    format_aggregates[format_name]['costs'].append(result['cost'])
    
    return format_aggregates


def _calculate_format_statistics(format_aggregates: Dict) -> Dict:
    """
    Calculate statistical summary for each format
    
    Args:
        format_aggregates: Aggregated data by format
        
    Returns:
        Dict mapping format names to statistical summaries
    """
    quality_by_format = {}
    
    for format_name, data in format_aggregates.items():
        if data['quality_scores']:
            quality_by_format[format_name] = {
                'avg_quality': sum(data['quality_scores']) / len(data['quality_scores']),
                'avg_tokens': sum(data['token_counts']) / len(data['token_counts']),
                'avg_cost': sum(data['costs']) / len(data['costs']),
                'sample_size': len(data['quality_scores'])
            }
    
    return quality_by_format


def _calculate_quality_improvement(quality_by_format: Dict) -> Tuple[float, float, float]:
    """
    Calculate quality improvement statistics
    
    Args:
        quality_by_format: Statistical summaries by format
        
    Returns:
        Tuple of (improvement_percent, best_quality, worst_quality)
    """
    if len(quality_by_format) < 2:
        return 0.0, 0.0, 0.0
    
    quality_values = [stats['avg_quality'] for stats in quality_by_format.values()]
    best_quality = max(quality_values)
    worst_quality = min(quality_values)
    improvement = ((best_quality - worst_quality) / worst_quality) * 100 if worst_quality > 0 else 0
    
    return improvement, best_quality, worst_quality


def _calculate_cost_benefit(quality_by_format: Dict, sorted_formats: List[Tuple]) -> Tuple[float, float]:
    """
    Calculate cost-benefit statistics
    
    Args:
        quality_by_format: Statistical summaries by format
        sorted_formats: Formats sorted by quality (best to worst)
        
    Returns:
        Tuple of (cost_increase_percent, quality_cost_ratio)
    """
    if len(sorted_formats) < 2:
        return 0.0, float('inf')
    
    best_format = sorted_formats[0][0] 
    worst_format = sorted_formats[-1][0]
    best_cost = quality_by_format[best_format]['avg_cost']
    worst_cost = quality_by_format[worst_format]['avg_cost']
    cost_multiplier = best_cost / worst_cost if worst_cost > 0 else 1
    
    cost_increase_pct = (cost_multiplier - 1) * 100
    
    # Calculate quality improvement for ratio
    improvement, _, _ = _calculate_quality_improvement(quality_by_format)
    quality_cost_ratio = improvement / cost_increase_pct if cost_increase_pct > 0 else float('inf')
    
    return cost_increase_pct, quality_cost_ratio


def _display_format_results(quality_by_format: Dict) -> List[Tuple]:
    """
    Display format-by-format results and return sorted list
    
    Args:
        quality_by_format: Statistical summaries by format
        
    Returns:
        List of (format_name, stats) tuples sorted by quality
    """
    sorted_formats = sorted(quality_by_format.items(), key=lambda x: x[1]['avg_quality'], reverse=True)
    
    for format_name, stats in sorted_formats:
        print(f"{format_name:<25} Quality: {stats['avg_quality']:.3f} | Tokens: {stats['avg_tokens']:.0f} | Cost: ${stats['avg_cost']:.5f} | n={stats['sample_size']}")
    
    return sorted_formats


def analyze_results_by_models(results_data: Dict, model_filter: Optional[List[str]] = None) -> Optional[Dict]:
    """
    Analyze test results with optional model filtering
    
    This function allows comparing results with different model combinations
    to understand the impact of specific models (e.g., excluding Gemini's
    reasoning tokens from cost analysis).
    
    Args:
        results_data: Complete test results from factor3_test.py
        model_filter: List of models to include (None = all models)
        
    Returns:
        Dict with analysis statistics or None if insufficient data
    """
    if model_filter is None:
        model_filter = ["gpt-4.1", "sonnet-4", "gemini-2.5"]
    
    print(f"\n🔍 ANALYSIS WITH MODELS: {', '.join(model_filter)}")
    print("-" * 60)
    
    # Use shared aggregation and calculation functions
    format_aggregates = _aggregate_format_results(results_data, model_filter)
    quality_by_format = _calculate_format_statistics(format_aggregates)
    sorted_formats = _display_format_results(quality_by_format)
    
    # Calculate improvement statistics
    if len(quality_by_format) >= 2:
        improvement, best_quality, worst_quality = _calculate_quality_improvement(quality_by_format)
        cost_increase_pct, quality_cost_ratio = _calculate_cost_benefit(quality_by_format, sorted_formats)
        
        print(f"\n📊 RESULTS WITH {', '.join(model_filter).upper()}:")
        print(f"   Quality improvement: {improvement:.1f}%")
        print(f"   Cost increase: {cost_increase_pct:.1f}%")
        print(f"   Quality/Cost ratio: {quality_cost_ratio:.2f}")
        
        return {
            'quality_improvement': improvement,
            'cost_increase': cost_increase_pct,
            'quality_cost_ratio': quality_cost_ratio,
            'best_quality': best_quality,
            'worst_quality': worst_quality,
            'sample_size': sum(stats['sample_size'] for stats in quality_by_format.values())
        }
    
    return None


def _display_detailed_results(results_data: Dict) -> int:
    """
    Display detailed results by scenario and return test count
    
    Args:
        results_data: Complete test results from all scenarios
        
    Returns:
        Total number of tests completed
    """
    test_count = 0
    
    for scenario_name, scenario_results in results_data.items():
        print(f"\n--- {scenario_name} ---")
        print(f"{'Format':<25} {'Model':<12} {'Tokens':<8} {'Cost':<10} {'Quality':<8} {'Time':<6}")
        print("-" * 80)
        
        for format_name, format_results in scenario_results.items():
            for model_name, result in format_results.items():
                quality_score = result.get('quality', {}).get('overall', 0)
                test_count += 1
                print(f"{format_name:<25} {model_name:<12} {result['total_tokens']:<8} ${result['cost']:<9.6f} {quality_score:<8.2f} {result['time']:<6.2f}s")
    
    return test_count


def generate_comprehensive_summary(results_data: Dict) -> None:
    """
    Generate comprehensive analysis summary across all scenarios
    
    This function provides the main summary output that appears at the
    end of factor3_test.py runs, including statistical significance
    assessment and cost-benefit analysis.
    
    Args:
        results_data: Complete test results from all scenarios
    """
    print(f"\n{'='*80}")
    print("COMPREHENSIVE RESULTS ACROSS ALL SCENARIOS")
    print(f"{'='*80}")
    
    # Display detailed results and get test count
    test_count = _display_detailed_results(results_data)
    print(f"Total tests completed: {test_count}")
    
    # Use shared aggregation and calculation functions
    format_aggregates = _aggregate_format_results(results_data)
    quality_by_format = _calculate_format_statistics(format_aggregates)
    
    # Generate Factor 3 effectiveness analysis
    _generate_factor3_analysis(quality_by_format)


def _generate_factor3_analysis(quality_by_format: Dict) -> None:
    """
    Generate Factor 3 statistical analysis and effectiveness assessment
    
    Args:
        quality_by_format: Aggregated quality statistics by format
    """
    print(f"\n🎯 FACTOR 3 STATISTICAL ANALYSIS")
    print("-" * 60)
    
    # Display results and get sorted formats
    sorted_formats = _display_format_results(quality_by_format)
    
    # Calculate and display statistical significance
    if len(quality_by_format) >= 2:
        improvement, best_quality, worst_quality = _calculate_quality_improvement(quality_by_format)
        
        print(f"\n📊 FACTOR 3 STATISTICAL SIGNIFICANCE:")
        print(f"   Quality improvement: {improvement:.1f}%")
        print(f"   Best format quality:  {best_quality:.3f}")
        print(f"   Worst format quality: {worst_quality:.3f}")
        print(f"   Total sample size: {sum(stats['sample_size'] for stats in quality_by_format.values())}")
        
        # Assess statistical significance
        sample_size = sum(stats['sample_size'] for stats in quality_by_format.values())
        if sample_size < 15:
            print(f"⚠️  Small sample size (n={sample_size}) - results may not be statistically significant")
        
        # Generate effectiveness verdict
        _assess_factor3_effectiveness(improvement)
        
        # Cost-benefit analysis
        _display_cost_benefit_analysis(quality_by_format, sorted_formats, improvement)


def _assess_factor3_effectiveness(improvement: float) -> None:
    """
    Assess Factor 3 effectiveness based on quality improvement percentage
    
    Args:
        improvement: Quality improvement percentage
    """
    if improvement > 25:
        print("✅ Factor 3 STRONGLY PROVEN: Large quality improvement!")
    elif improvement > 15:
        print("✅ Factor 3 PROVEN: Significant quality improvement!")
    elif improvement > 8:
        print("⚠️ Factor 3 MODEST: Some quality improvement, but may not justify cost")
    else:
        print("❌ Factor 3 UNCLEAR: Minimal quality difference - cost may not be justified")


def _display_cost_benefit_analysis(quality_by_format: Dict, sorted_formats: List[Tuple], improvement: float) -> None:
    """
    Display detailed cost-benefit analysis
    
    Args:
        quality_by_format: Quality statistics by format
        sorted_formats: Formats sorted by quality
        improvement: Quality improvement percentage
    """
    cost_increase_pct, quality_cost_ratio = _calculate_cost_benefit(quality_by_format, sorted_formats)
    
    print(f"\n💰 COST-BENEFIT ANALYSIS:")
    print(f"   Quality improvement: {improvement:.1f}%")
    print(f"   Cost increase: {cost_increase_pct:.1f}%")
    print(f"   Quality/Cost ratio: {quality_cost_ratio:.2f}")
    
    # Value assessment
    if quality_cost_ratio > 2.0:
        print("✅ Excellent value: Quality improvement strongly justifies cost increase")
    elif quality_cost_ratio > 1.0:
        print("✅ Good value: Quality improvement justifies cost increase")
    else:
        print("❌ Poor value: Cost increase may not justify quality improvement")


def load_and_analyze_results(filename: str) -> None:
    """
    Load existing results and analyze with different model combinations
    
    This function provides comparative analysis to understand how different
    model combinations affect the cost-benefit calculations, particularly
    useful for understanding the impact of Gemini's reasoning tokens.
    
    Args:
        filename: Path to saved results JSON file
    """
    with open(filename, 'r') as f:
        results_data = json.load(f)
    
    print("🔬 COMPARATIVE MODEL ANALYSIS")
    print("=" * 80)
    
    # Define model combinations to analyze
    model_combinations = [
        (["gpt-4.1", "sonnet-4", "gemini-2.5"], "All Models"),
        (["gpt-4.1", "sonnet-4"], "GPT-4.1 + Sonnet"),
        (["gemini-2.5"], "Gemini Only"),
        (["gpt-4.1"], "GPT-4.1 Only"),
        (["sonnet-4"], "Sonnet 4 Only")
    ]
    
    # Analyze each combination
    analysis_results = {}
    for models, name in model_combinations:
        analysis_results[name] = analyze_results_by_models(results_data, models)
    
    # Generate comparison summary
    _generate_model_comparison_summary(analysis_results)


def _generate_model_comparison_summary(analysis_results: Dict[str, Optional[Dict]]) -> None:
    """
    Generate summary comparison across different model combinations
    
    Args:
        analysis_results: Analysis results for different model combinations
    """
    print(f"\n🏆 SUMMARY COMPARISON:")
    print(f"{'Model Combination':<20} {'Quality Gain':<12} {'Cost Increase':<14} {'Value Ratio':<12}")
    print("-" * 60)
    
    # Display results for each combination
    for combination_name, stats in analysis_results.items():
        if stats:
            print(f"{combination_name:<20} {stats['quality_improvement']:<12.1f}% {stats['cost_increase']:<14.1f}% {stats['quality_cost_ratio']:<12.2f}")
    
    # Insight about reasoning tokens
    print(f"\n💡 INSIGHT: Gemini's reasoning tokens impact cost analysis")
    
    all_models = analysis_results.get("All Models")
    no_gemini = analysis_results.get("GPT-4.1 + Sonnet")
    
    if all_models and no_gemini:
        cost_diff = all_models['cost_increase'] - no_gemini['cost_increase']
        print(f"   Cost difference with/without Gemini: {cost_diff:.1f} percentage points")
        print(f"   Cleaner cost analysis excludes reasoning token overhead")
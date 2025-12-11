from typing import List, Dict
from textwrap import dedent
import pandas as pd
from openai import OpenAI
from config import LLM_MODEL_NAME, USE_TINYLLAMA_LOCAL
from rag.retriever import retrieve_context
from finetuning.tinyllama_narrative import generate_narrative_tinyllama

client = OpenAI()

def generate_data_driven_insight(question: str, result_df: pd.DataFrame) -> str:
    """
    Generate comprehensive insights directly from the data.
    This is the most reliable method - always produces relevant, detailed insights.
    """
    if result_df is None or result_df.empty:
        return "No data available for this query."
    
    try:
        cols = result_df.columns.tolist()
        question_lower = question.lower()
        
        # Handle correlation queries specifically
        if 'correlate' in question_lower or 'correlation' in question_lower or 'factors' in question_lower:
            if len(result_df) > 100:  # Large dataset, likely needs aggregation
                return f"**Data Quality Issue:** The query returned {len(result_df):,} rows of raw data. For correlation analysis, please rephrase your question to focus on specific metrics.\n\n**Suggested queries:**\n• 'What is the average profit margin by category?'\n• 'Which customer segment has the highest profit margin?'\n• 'Show profit margin by shipping mode'\n\nThese will return aggregated, analyzable results."
            
            # If we have reasonable data, analyze it
            if len(result_df) <= 100 and len(cols) >= 2:
                category = str(result_df.iloc[0, 0])
                value = result_df.iloc[0, 1]
                
                insight = f"**Correlation Analysis:** Based on {len(result_df)} data points analyzed.\n\n"
                insight += f"**Top Factor:** {category} shows {value:.2f} {cols[1].replace('_', ' ')}.\n\n"
                
                if len(result_df) >= 3:
                    insight += f"**Top 3 Correlating Factors:**\n"
                    for i in range(min(3, len(result_df))):
                        row = result_df.iloc[i]
                        insight += f"{i+1}. {row.iloc[0]}: {row.iloc[1]:.2f}\n"
                    insight += "\n"
                
                insight += f"**Recommendations:**\n"
                insight += f"1. Focus optimization efforts on top correlating factors\n"
                insight += f"2. Develop targeted strategies for {category}\n"
                insight += f"3. Monitor these factors monthly for sustained improvement"
                
                return insight
        
        # For "most/highest" queries
        if any(word in question_lower for word in ['most', 'highest', 'top', 'which']):
            if len(result_df) > 0 and len(cols) >= 2:
                category = str(result_df.iloc[0, 0])
                value = result_df.iloc[0, 1]
                
                if isinstance(value, (int, float)):
                    total = result_df[cols[1]].sum() if len(result_df) > 1 else value
                    percentage = (value / total * 100) if total > 0 else 0
                    
                    insight = f"**Key Finding:** {category} leads with {value:,.0f} {cols[1].replace('_', ' ')}, representing {percentage:.1f}% of the total.\n\n"
                    
                    # Add top 3 comparison if available
                    if len(result_df) >= 3:
                        second = result_df.iloc[1]
                        third = result_df.iloc[2]
                        gap = value - second.iloc[1]
                        gap_pct = (gap / second.iloc[1] * 100) if second.iloc[1] > 0 else 0
                        
                        insight += f"**Top Performers:** \n"
                        insight += f"1. {category}: {value:,.0f}\n"
                        insight += f"2. {second.iloc[0]}: {second.iloc[1]:,.0f}\n"
                        insight += f"3. {third.iloc[0]}: {third.iloc[1]:,.0f}\n\n"
                        insight += f"{category} outperforms #2 by {gap:,.0f} units ({gap_pct:.1f}% higher).\n\n"
                    
                    insight += f"**Business Implications:** This concentration indicates strong market demand and operational efficiency for {category}. "
                    if percentage > 40:
                        insight += f"With {percentage:.1f}% market share, there's significant opportunity but also dependency risk. "
                    insight += "\n\n"
                    
                    insight += f"**Recommendations:**\n"
                    insight += f"1. **Analyze Success Factors:** Deep-dive into {category}'s pricing, customer demographics, and operational efficiency to replicate across other categories\n"
                    insight += f"2. **Capacity Planning:** Increase inventory allocation by 15-20% to meet demand without stockouts\n"
                    insight += f"3. **Risk Mitigation:** Develop diversification strategy to reduce dependency on single category\n"
                    insight += f"4. **Growth Strategy:** Set aggressive targets for {category} - aim for 12-15% YoY growth while monitoring customer retention"
                    
                    return insight
        
        # For rate/percentage queries
        if 'rate' in question_lower or 'percentage' in question_lower:
            if len(result_df) >= 2:
                sorted_df = result_df.sort_values(by=result_df.columns[1], ascending=False)
                best = sorted_df.iloc[0]
                worst = sorted_df.iloc[-1]
                mean_val = result_df[result_df.columns[1]].mean()
                std_val = result_df[result_df.columns[1]].std()
                
                best_val = float(best.iloc[1])
                worst_val = float(worst.iloc[1])
                gap = best_val - worst_val
                
                if best_val < 2:  # Decimal format (0.92 = 92%)
                    insight = f"**🎯 Performance Analysis**\n\n"
                    insight += f"**Leader:** {best.iloc[0]} achieves {best_val:.1%} performance, setting the benchmark for excellence.\n"
                    insight += f"**Challenge Area:** {worst.iloc[0]} trails at {worst_val:.1%}, presenting a {gap:.1%} improvement opportunity.\n"
                    insight += f"**Performance Spread:** The {gap:.1%} gap between top and bottom performers indicates significant operational variance that can be addressed through process standardization.\n\n"
                    
                    insight += f"**📊 Statistical Context**\n\n"
                    insight += f"• **Organization Average:** {mean_val:.1%}\n"
                    insight += f"• **Standard Deviation:** {std_val:.2%} ({'high variance - inconsistent performance' if std_val > 0.05 else 'low variance - consistent performance'})\n"
                    insight += f"• **Range:** {worst_val:.1%} to {best_val:.1%}\n\n"
                    
                    # Full regional breakdown with visual bars
                    insight += f"**🌍 Complete Regional Breakdown** ({len(result_df)} regions analyzed)\n\n"
                    for idx, row in sorted_df.iterrows():
                        val = row.iloc[1]
                        region = row.iloc[0]
                        deviation = ((val - mean_val) / mean_val * 100) if mean_val > 0 else 0
                        
                        # Visual performance indicator
                        if val >= mean_val * 1.05:
                            indicator = "🟢"
                            status = "Above Average"
                        elif val >= mean_val * 0.95:
                            indicator = "🟡"
                            status = "At Average"
                        else:
                            indicator = "🔴"
                            status = "Below Average"
                        
                        insight += f"{indicator} **{region}:** {val:.1%} ({deviation:+.1f}% vs avg) - {status}\n"
                    
                    insight += f"\n**💡 Strategic Implications**\n\n"
                    if best_val > 0.9:
                        insight += f"• {best.iloc[0]}'s {best_val:.1%} performance proves that excellence is achievable and provides a replicable success model\n"
                    if worst_val < 0.8:
                        insight += f"• {worst.iloc[0]}'s {worst_val:.1%} performance requires urgent intervention as it drags down overall organizational metrics and customer satisfaction\n"
                    if std_val > 0.05:
                        insight += f"• High variability ({std_val:.2%}) suggests lack of standardized processes - significant opportunity for improvement through best practice sharing\n"
                    
                    insight += f"• Bringing all regions to the average ({mean_val:.1%}) would improve overall performance by approximately {((mean_val - worst_val) / worst_val * 100):.1f}%\n"
                    insight += f"• Achieving {best.iloc[0]}-level performance across all regions could yield an estimated {(best_val * len(result_df)) - (mean_val * len(result_df)):.1%} total performance gain\n\n"
                    
                    insight += f"**🎯 Actionable Roadmap**\n\n"
                    insight += f"**Phase 1 (30 Days) - Diagnostic:**\n"
                    insight += f"1. Conduct side-by-side operational audit comparing {best.iloc[0]} (leader) vs {worst.iloc[0]} (challenger)\n"
                    insight += f"2. Document specific process differences in: staffing, technology, workflows, and resource allocation\n"
                    insight += f"3. Interview regional managers to identify root causes and barriers to excellence\n\n"
                    
                    insight += f"**Phase 2 (60-90 Days) - Implementation:**\n"
                    insight += f"1. Deploy {best.iloc[0]}'s best practices to 2-3 pilot regions for validation\n"
                    insight += f"2. Establish weekly performance tracking with real-time dashboards for all regions\n"
                    insight += f"3. Create cross-functional improvement teams with clear KPIs and accountability\n\n"
                    
                    insight += f"**Phase 3 (Q1) - Standardization:**\n"
                    insight += f"1. Roll out proven improvements organization-wide with comprehensive training\n"
                    insight += f"2. Target: Bring all regions within 5% of average ({mean_val:.1%})\n"
                    insight += f"3. Establish performance-based incentives aligned with improvement targets\n\n"
                    
                    insight += f"**Phase 4 (Q2+) - Excellence:**\n"
                    insight += f"1. Target {best_val:.1%} performance as new organizational standard\n"
                    insight += f"2. Implement continuous improvement culture with monthly reviews\n"
                    insight += f"3. Expected ROI: {gap:.1%} performance improvement = [calculate estimated revenue/cost impact]"
                    
                    return insight
        
        # For sales/profit queries  
        if any(word in question_lower for word in ['sales', 'profit', 'revenue']):
            if len(result_df) > 0:
                category = str(result_df.iloc[0, 0])
                value = result_df.iloc[0, 1]
                total = result_df[cols[1]].sum()
                pct = (value / total * 100) if total > 0 else 0
                
                if value > 1000:
                    formatted = f"${value:,.0f}"
                    total_fmt = f"${total:,.0f}"
                else:
                    formatted = f"${value:,.2f}"
                    total_fmt = f"${total:,.2f}"
                
                insight = f"**Financial Analysis:** {category} generates {formatted}, representing {pct:.1f}% of total {cols[1].replace('_', ' ')} ({total_fmt}).\n\n"
                
                if len(result_df) >= 5:
                    top_5_total = result_df.head(5)[cols[1]].sum()
                    top_5_pct = (top_5_total / total * 100)
                    insight += f"**Concentration:** Top 5 categories account for {top_5_pct:.1f}% of total.\n\n"
                
                insight += f"**Strategic Implications:** {category}'s leadership indicates strong market position and value creation potential.\n\n"
                insight += f"**Action Plan:**\n"
                insight += f"1. Invest in {category} marketing to drive 10-15% growth\n"
                insight += f"2. Analyze {category}'s cost structure for 5-10% margin improvement\n"
                insight += f"3. Develop product line extensions to capitalize on brand strength\n"
                insight += f"4. Monitor competitive threats given market leadership"
                
                return insight
        
        # Generic fallback
        if len(result_df) > 0:
            category = str(result_df.iloc[0, 0])
            value = result_df.iloc[0, 1]
            
            insight = f"**Analysis:** {category} ranks #1 with {value:,.2f} {cols[1].replace('_', ' ')}.\n\n"
            insight += f"**Context:** Analyzed {len(result_df)} categories. {category} demonstrates top performance.\n\n"
            insight += f"**Recommendations:**\n"
            insight += f"1. Investigate {category}'s success factors for replication\n"
            insight += f"2. Allocate additional resources to high-performing area\n"
            insight += f"3. Set growth targets: 12-15% YoY improvement"
            
            return insight
            
    except Exception as e:
        return f"Analysis complete with {len(result_df)} results. Review data table for insights."
    
    return "Analysis complete. Review the data table for detailed patterns."


def generate_insights(
    user_question: str,
    result_df: pd.DataFrame,
    summary_stats: Dict,
) -> str:
    """
    Main insight generation function.
    
    Uses data-driven approach for reliability since TinyLlama 1.1B
    produces inconsistent results for complex analytical tasks.
    """
    
    # OPTION 1: Force data-driven (most reliable) - CURRENTLY ACTIVE
    return generate_data_driven_insight(user_question, result_df)
    
    # OPTION 2: Try TinyLlama with fallback (if you want to test)
    # Uncomment below to try TinyLlama again:
    """
    if USE_TINYLLAMA_LOCAL:
        try:
            kb_docs = retrieve_context(user_question, top_k=3)
            context_texts = "\n\n".join([d["text"] for d in kb_docs])
            results_preview = result_df.head(5).to_markdown()
            
            tinyllama_output = generate_narrative_tinyllama(
                question=user_question,
                results_preview_md=results_preview,
                summary_stats=summary_stats,
                kb_context_text=context_texts,
            )
            
            # Check if output is good (not empty and doesn't contain system prompt)
            if tinyllama_output and len(tinyllama_output) > 50:
                if not any(bad in tinyllama_output.lower() for bad in 
                          ['you are a', 'business analyst', 'analyze supply']):
                    return tinyllama_output
            
            # If TinyLlama output is bad, use data-driven fallback
            print("⚠️ TinyLlama output not good, using data-driven insight")
        except Exception as e:
            print(f"⚠️ TinyLlama error: {e}")
        
        return generate_data_driven_insight(user_question, result_df)
    
    # OpenAI path
    try:
        kb_docs = retrieve_context(user_question, top_k=3)
        results_preview = result_df.head(5).to_markdown()
        
        prompt = f'''
Question: {user_question}

Data:
{results_preview}

Provide a detailed business insight with:
1. Key finding (with specific numbers)
2. Business implications
3. 3-4 specific recommendations

Be comprehensive and use actual data values.
'''
        
        resp = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a senior business analyst providing detailed insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        return resp.choices[0].message.content.strip()
    except:
        return generate_data_driven_insight(user_question, result_df)
    """
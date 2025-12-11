import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline.data_runner import load_processed_df
from pipeline.orchestrator import answer_question
from datetime import datetime

# Page configuration with dark theme
st.set_page_config(
    page_title="InsightWeaver - Data Storytelling Copilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark mode and modern styling
st.markdown("""
<style>
    /* Dark mode colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --background-dark: #0e1117;
        --card-background: #1e1e2e;
        --text-primary: #ffffff;
        --text-secondary: #b4b4b4;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    
    /* Ensure all text is visible */
    p, div, span, label {
        color: #e0e0e0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .info-card {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        color: #e0e0e0;
    }
    
    .info-card h3, .info-card h4 {
        color: #8b9cff;
        margin-bottom: 0.8rem;
    }
    
    .info-card p, .info-card li {
        color: #d0d0d0;
        line-height: 1.7;
    }
    
    .info-card ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .info-card li {
        margin-bottom: 0.5rem;
    }
    
    .info-card strong {
        color: #ffffff;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border: 1px solid rgba(102, 126, 234, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: #1e1e2e !important;
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 1px #667eea;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #0e1117 100%);
    }
    
    [data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 30, 46, 0.5);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255,255,255,0.7);
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border-left: 4px solid #00ff00;
        border-radius: 8px;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border-left: 4px solid #ff0000;
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 46, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Narrative box */
    .narrative-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
        border: 2px solid rgba(102, 126, 234, 0.4);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
        color: #e0e0e0;
    }
    
    .narrative-box h3 {
        color: #8b9cff;
        margin-bottom: 1rem;
    }
    
    .narrative-box p, .narrative-box li, .narrative-box div {
        color: #e0e0e0 !important;
        line-height: 1.8;
    }
    
    .narrative-box strong {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧠 InsightWeaver</h1>
    <p>AI-Powered Data Storytelling Copilot using RAG + LLMs</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    # Stats section
    with st.expander("📊 Session Statistics", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{st.session_state.query_count}</p>
                <p class="metric-label">Queries Run</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{len(st.session_state.history)}</p>
                <p class="metric-label">Saved Results</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How to use section
    with st.expander("💡 How to Use", expanded=True):
        st.markdown("""
        **Ask questions like:**
        
        🎯 **Delivery Performance**
        - "What is the on-time delivery rate by order_region?"
        - "Where are average shipping_delay_days the highest?"
        
        💰 **Revenue Analysis**
        - "Which customer_segment generates the most sales and profit?"
        - "Compare benefit_per_order across category_name and market"
        
        📈 **Trend Analysis**
        - "Show profit trends over time by region"
        - "Which products have declining delivery performance?"
        
        🔍 **Deep Dive**
        - "Analyze late deliveries by customer segment"
        - "What factors correlate with high profit margins?"
        """)
    
    st.markdown("---")
    
    # Sample data toggle
    show_data = st.checkbox("🔍 Show Sample Data", value=False)
    if show_data:
        try:
            with st.spinner("Loading sample data..."):
                df_sample = load_processed_df().head(100)
                st.dataframe(df_sample, use_container_width=True, height=300)
                
                # Quick stats
                st.markdown("**Quick Stats:**")
                st.write(f"• Total rows: {len(df_sample):,}")
                st.write(f"• Columns: {len(df_sample.columns)}")
                st.write(f"• Numeric cols: {len(df_sample.select_dtypes(include='number').columns)}")
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
    
    st.markdown("---")
    
    # Export history
    if st.session_state.history:
        if st.button("📥 Export History"):
            history_text = "\n\n".join([
                f"Query {i+1}: {h['question']}\nCode:\n{h['code']}\n"
                for i, h in enumerate(st.session_state.history)
            ])
            st.download_button(
                "Download History",
                history_text,
                file_name=f"insightweaver_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Clear history
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.query_count = 0
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; color: rgba(255,255,255,0.6);'>
        <p style='font-size: 0.9rem;'>Built with ❤️ by Sruthi Gandla</p>
        <p style='font-size: 0.8rem;'>Northeastern University</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
tab1, tab2, tab3 = st.tabs(["🎯 Analysis", "📜 History", "ℹ️ About"])

with tab1:
    # Query input section
    st.markdown("### 💬 Ask Your Question")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input(
            "Enter your natural language question:",
            placeholder="e.g., What is the on-time delivery rate by order_region?",
            label_visibility="collapsed"
        )
    with col2:
        analyze_btn = st.button("🚀 Analyze", use_container_width=True)
    
    # Sample questions chips
    st.markdown("**Quick examples:**")
    sample_cols = st.columns(4)
    sample_questions = [
        "On-time delivery by region",
        "Top profitable segments",
        "Shipping delays analysis",
        "Sales by category"
    ]
    
    for idx, (col, sample) in enumerate(zip(sample_cols, sample_questions)):
        with col:
            if st.button(sample, key=f"sample_{idx}", use_container_width=True):
                question = sample
                analyze_btn = True
    
    st.markdown("---")
    
    # Process query
    if analyze_btn and question:
        st.session_state.query_count += 1
        
        with st.spinner("🔮 Analyzing your question..."):
            try:
                result = answer_question(question)
                
                # Store in history
                st.session_state.history.append({
                    'question': question,
                    'code': result['code'],
                    'result_df': result['result_df'],
                    'narrative': result['narrative'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()
        
        # Success indicator
        st.success("✅ Analysis complete!")
        
        # Results section with tabs
        result_tabs = st.tabs(["📝 Code", "📊 Data", "📈 Visualization", "🧠 Insights"])
        
        with result_tabs[0]:
            st.markdown("### Generated Code")
            st.code(result["code"], language="python", line_numbers=True)
            
            # Copy button simulation
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📋 Copy Code"):
                    st.info("Code copied to clipboard! (simulation)")
        
        with result_tabs[1]:
            st.markdown("### Results Preview")
            df_res = result["result_df"]
            
            if df_res is not None and not df_res.empty:
                # Show metrics if available
                if len(df_res.columns) <= 3:
                    st.markdown("**Quick Metrics:**")
                    metric_cols = st.columns(len(df_res))
                    for idx, (_, row) in enumerate(df_res.head(len(metric_cols)).iterrows()):
                        with metric_cols[idx]:
                            if len(df_res.columns) == 2:
                                st.metric(
                                    label=str(row.iloc[0]),
                                    value=f"{row.iloc[1]:.2f}" if isinstance(row.iloc[1], (int, float)) else str(row.iloc[1])
                                )
                
                # Show full dataframe
                st.dataframe(
                    df_res,
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                csv = df_res.to_csv(index=False)
                st.download_button(
                    "📥 Download Results (CSV)",
                    csv,
                    file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to display")
        
        with result_tabs[2]:
            st.markdown("### Visualization")
            df_res = result["result_df"]
            
            if df_res is not None and not df_res.empty:
                num_cols = df_res.select_dtypes(include="number").columns.tolist()
                cat_cols = df_res.select_dtypes(exclude="number").columns.tolist()
                
                if num_cols and cat_cols:
                    # Interactive Plotly chart
                    x_col = cat_cols[0]
                    y_col = num_cols[0]
                    
                    # Create multiple chart types
                    chart_type = st.radio(
                        "Chart type:",
                        ["Bar Chart", "Line Chart", "Pie Chart"],
                        horizontal=True
                    )
                    
                    if chart_type == "Bar Chart":
                        fig = px.bar(
                            df_res,
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} by {x_col}",
                            template="plotly_dark",
                            color=y_col,
                            color_continuous_scale="Viridis"
                        )
                    elif chart_type == "Line Chart":
                        fig = px.line(
                            df_res,
                            x=x_col,
                            y=y_col,
                            title=f"{y_col} by {x_col}",
                            template="plotly_dark",
                            markers=True
                        )
                    else:  # Pie Chart
                        fig = px.pie(
                            df_res,
                            names=x_col,
                            values=y_col,
                            title=f"{y_col} Distribution by {x_col}",
                            template="plotly_dark"
                        )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif num_cols:
                    # If only numeric columns, show correlation heatmap
                    if len(num_cols) > 1:
                        st.markdown("**Correlation Analysis**")
                        corr = df_res[num_cols].corr()
                        fig = px.imshow(
                            corr,
                            template="plotly_dark",
                            color_continuous_scale="RdBu_r",
                            aspect="auto"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(df_res.set_index(df_res.columns[0]))
            else:
                st.info("📊 No visualization available for this query")
        
        with result_tabs[3]:
            st.markdown("### Business Insights")
            st.markdown(f"""
            <div class="narrative-box">
                <h3>🎯 AI-Generated Analysis</h3>
                <div style="color: #e0e0e0; font-size: 1.05rem;">
                    {result["narrative"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional context
            with st.expander("🔍 Methodology"):
                st.markdown("""
                <div style="color: #d0d0d0;">
                This narrative was generated using:<br><br>
                <strong>1. RAG Context Retrieval</strong> - Domain knowledge from knowledge base<br>
                <strong>2. Code Execution Results</strong> - Actual data analysis<br>
                <strong>3. Fine-tuned TinyLlama</strong> - Supply chain domain adaptation<br>
                <strong>4. Business Context</strong> - KPI interpretation and recommendations
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 📜 Analysis History")
    
    if st.session_state.history:
        st.info(f"💡 You have {len(st.session_state.history)} saved analysis results")
        
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"🔍 Query {len(st.session_state.history) - idx}: {item['question'][:60]}...", expanded=(idx==0)):
                st.markdown(f"**⏰ Timestamp:** {item['timestamp']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📝 Code:**")
                    st.code(item['code'], language="python")
                
                with col2:
                    st.markdown("**📊 Result:**")
                    if item['result_df'] is not None and not item['result_df'].empty:
                        st.dataframe(item['result_df'].head(), use_container_width=True)
                
                st.markdown("**🧠 Insights:**")
                st.markdown(f'<div style="color: #d0d0d0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border-left: 3px solid #667eea;">{item["narrative"]}</div>', unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.info("🔍 No analysis history yet. Run your first query!")

with tab3:
    st.markdown("### ℹ️ About InsightWeaver")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🎯 What is InsightWeaver?</h3>
            <p>An end-to-end AI-powered data storytelling copilot that transforms natural language 
            questions into executable analytics, visualizations, and business narratives.</p>
            
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🛠️ Technology Stack</h3>
            <ul>
                <li><strong>Code Generation:</strong> OpenAI GPT-4</li>
                <li><strong>RAG:</strong> ChromaDB + SentenceTransformers</li>
                <li><strong>Narrative:</strong> Fine-tuned TinyLlama + LoRA</li>
                <li><strong>Execution:</strong> Secure Python sandbox</li>
                <li><strong>UI:</strong> Streamlit</li>
                <li><strong>Dataset:</strong> DataCo Supply Chain</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Links
    st.markdown("### 🔗 Project Links")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/SruthiGandla01/Data_Storytelling_Copilot_using_RAG_LLM)")
    with col2:
        st.markdown("[![Docs](https://img.shields.io/badge/Documentation-Website-blue?style=for-the-badge&logo=read-the-docs)](https://sruthigandla01.github.io/Data_Storytelling_Copilot_using_RAG_LLM/)")
    with col3:
        st.markdown("[![Paper](https://img.shields.io/badge/Report-PDF-red?style=for-the-badge&logo=adobe)](https://github.com/SruthiGandla01/Data_Storytelling_Copilot_using_RAG_LLM)")
    
    st.markdown("---")
    
    # Credits
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: rgba(30, 30, 46, 0.5); border-radius: 10px;'>
        <h3 style='color: #667eea;'>👩‍💻 Built by Sruthi Gandla</h3>
        <p>Northeastern University</p>
        <p>Prompt Engineering and AI Course Final Project | 2025</p>
        <p style='margin-top: 1rem; color: rgba(255,255,255,0.6);'>
            Implements: Prompt Engineering • RAG • Fine-Tuning (LoRA)
        </p>
    </div>
    """, unsafe_allow_html=True)
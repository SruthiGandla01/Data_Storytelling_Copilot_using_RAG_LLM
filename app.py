import streamlit as st
import tabulate
from pipeline.data_runner import load_processed_df
from pipeline.orchestrator import answer_question

st.set_page_config(
    page_title="Data Storytelling Copilot using RAG LLM",
    layout="wide",
)

st.title("📦 Data Storytelling Copilot using RAG LLM")
st.write(
    "Ask natural language questions about orders, deliveries, delays, "
    "customer segments, and profitability."
)

with st.sidebar:
    st.header("ℹ️ How to use")
    st.markdown(
        """
**Example questions:**
- "What is the on-time delivery rate by order_region?"
- "Which customer_segment generates the most sales and profit?"
- "Where are average shipping_delay_days the highest?"
- "Compare benefit_per_order across category_name and market."
        """
    )

    if st.checkbox("Show sample data"):
        try:
            df_sample = load_processed_df().head(100)
            st.dataframe(df_sample)
        except Exception as e:
            st.error(f"Error loading processed data: {e}")

question = st.text_input("Enter your question:", "")

if st.button("Analyze") and question:
    with st.spinner("Analyzing..."):
        try:
            result = answer_question(question)
        except Exception as e:
            st.error(f"Error answering question: {e}")
        else:
            st.subheader("🧮 Generated Code")
            st.code(result["code"], language="python")

            st.subheader("📊 Results Preview")
            st.dataframe(result["result_df"])

            df_res = result["result_df"]
            if df_res is not None and not df_res.empty:
                st.markdown("#### Quick Visualization (if applicable)")
                num_cols = df_res.select_dtypes(include="number").columns.tolist()
                cat_cols = df_res.select_dtypes(exclude="number").columns.tolist()

                if num_cols and cat_cols:
                    x = cat_cols[0]
                    y = num_cols[0]
                    st.bar_chart(df_res.set_index(x)[y])

            st.subheader("🧠 Narrative Insights")
            st.markdown(result["narrative"])

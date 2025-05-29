import os
import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDs_WSLm63v1DdK-KotL-wBZfWMTQ9E4DQs"

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.5)

# Define a prompt template
prompt_template = PromptTemplate(
    input_variables=["query", "tariff_data"],
    template="Answer the question based on the tariff data:\nTariff Data: {tariff_data}\nQuestion: {query}\nAnswer:"
)

# Create a LangChain chain
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

def process_uploaded_file(uploaded_file):
    try:
        # Check the file type and process accordingly
        if uploaded_file.name.endswith('.csv'):
            tariff_data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            tariff_data = pd.read_json(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            try:
                # Read Excel without openpyxl
                tariff_data = pd.read_excel(uploaded_file)
            except:
                try:
                    # Fallback to xlrd for older Excel files
                    tariff_data = pd.read_excel(uploaded_file, engine='xlrd')
                except Exception as e:
                    st.error("Could not read Excel file. Please try converting to CSV format.")
                    return None
        else:
            st.error("Supported formats: CSV, JSON, Excel (.xlsx)")
            return None

        # Validate that we have data
        if tariff_data.empty:
            st.warning("The uploaded file contains no data.")
            return None

        # Convert DataFrame to formatted string
        return tariff_data.to_string(index=False)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def main():
    st.title("Hospital Reimbursement Assistant")
    
    # Add file type information
    st.info("Supported file types: CSV, JSON, Excel (.xlsx)")
    
    uploaded_file = st.file_uploader("Upload Tariff Document", type=["csv", "json", "xlsx"])

    if uploaded_file is not None:
        # Show loading spinner while processing file
        with st.spinner("Processing uploaded file..."):
            tariff_data = process_uploaded_file(uploaded_file)
            
        if tariff_data is not None:
            # Show preview of the data
            st.subheader("Data Preview")
            st.text(tariff_data[:500] + "..." if len(tariff_data) > 500 else tariff_data)
            
            query = st.text_input("Ask a question about reimbursement:")

            if query:
                with st.spinner("Generating response..."):
                    try:
                        response = llm_chain.run(query=query, tariff_data=tariff_data)
                        st.write("Answer:", response)
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()

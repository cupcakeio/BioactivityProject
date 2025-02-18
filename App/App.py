import streamlit as st
import pandas as pd
import base64
import pickle
from rdkit import Chem
from rdkit.Chem import Descriptors
import numpy as np

def desc_calc(smile):
    mol = Chem.MolFromSmiles(smile)
    if mol is None:
        return None
    
    all_desc = {name: func(mol) for name, func in Descriptors.descList}

    df=pd.DataFrame([all_desc])
    df.to_csv('descriptors_output.csv', index=False)
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def build_model(input_data):
    load_model= pickle.load(open('App/acetylcholinesterase_model.pickle', 'rb'))
    prediction = load_model.predict(input_data)
    st.header('***Prediction Output***')
    df = pd.Series(prediction, name='pIC50')
    st.write(prediction)
    if prediction[0] > 6:
        st.write("Molecule is predicted to be Bioaccessible")
    elif prediction[0] < 5:
        st.write("Molecule is predicted to be inactive")
    else:
        st.write("Molecule is predicted to be intermediate")
    st.markdown(filedownload(df), unsafe_allow_html=True)

    


with st.sidebar.header('Enter your molecule'):
    input_smile = st.text_input("Type the smile string of the molecule you wish to predict")
    st.sidebar.markdown('Example: CCOc1nn(-c2cccc(OCc3ccccc3)c2)c(=O)o1')

if st.sidebar.button('Predict'):
    st.header('**The Input Smile String**')
    st.write(input_smile)
    with st.spinner("Calculating descriptors...."):
        descriptors_df=desc_calc(input_smile)

        if descriptors_df is None:
            st.error("Invalid smile string please try again")
        else:
            st.header('**Calculated descriptors**')
            descriptors = pd.read_csv('descriptors_output.csv')
            st.write(descriptors)
            st.write(descriptors.shape)
    
            st.header('**Subset of descriptors from previously built models**')
            Xlist = list(pd.read_csv("App/descriptor_list.csv").columns)
            desc_subset = descriptors[Xlist]
            st.write(desc_subset)
            st.write(desc_subset.shape)

            build_model(desc_subset)
else:
    st.info('Input smile string in text box to begin!')
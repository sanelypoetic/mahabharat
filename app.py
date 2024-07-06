import streamlit as st
import pandas as pd
import re

def load_and_segment_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    paragraphs = [para.strip() for para in text.split('\n\n') if para.strip()]
    return paragraphs

def find_paragraph_indices(paragraphs):
    indices = [0]
    for paragraph in paragraphs:
        indices.append(indices[-1] + len(paragraph) + 1) 
    return indices

def split_paragraph(paragraph_text):

    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\,|\;|\?|\")\s'
    slices = re.split(pattern, paragraph_text)
    return slices

@st.cache_data
def load_data():
    verses_df = pd.read_csv('verses.csv')
    paragraphs = load_and_segment_text('ganguly_1.txt')


    if len(verses_df) > len(paragraphs):

        for _ in range(len(paragraphs), len(verses_df)):
            paragraphs.append("")

    initial_translations = {
        'Verse Number': verses_df['Verse Number'],
        'Translation': paragraphs[:len(verses_df)] 
    }

    df_master = pd.DataFrame(initial_translations)

    return verses_df, paragraphs, df_master


def update_master_dataframe(df_master, verse_number, translation):
    existing_index = df_master[df_master['Verse Number'] == verse_number].index
    if not existing_index.empty:
        df_master.loc[existing_index, 'Translation'] = translation
    else:
        df_master = df_master.append({'Verse Number': verse_number, 'Translation': translation}, ignore_index=True)

    df_master.to_csv('master_translations.csv', index=False)


st.title('Mahabharata Translation Mapping')
st.markdown("---")

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

verses_df, paragraphs, df_master = load_data()

def display_verse_and_options(index):
    if index < len(verses_df):
        st.header(f"Section {index + 1}")

        verse_id = verses_df.loc[index, 'Verse Number']
        verse_text = verses_df.loc[index, 'Sanskrit Text']
        paragraph_text = paragraphs[index]

        st.markdown(f"**Verse Number:** {verse_id}")
        st.markdown(f"**Verse:** {verse_text}")
        st.markdown("---")

        st.markdown("**Initially Mapped Paragraph:**")
        st.markdown(paragraph_text)
        st.markdown("---")

        st.markdown("**Translation Options:**")

        slices = split_paragraph(paragraph_text)
        #flawed logic
        prev_translation = df_master.loc[df_master['Verse Number'] == verse_id, 'Translation'].values
        if len(prev_translation) > 0:
            prev_translation = prev_translation[0]
        else:
            prev_translation = ""

        option1_selected = st.checkbox("Option 1 (Complete Paragraph)")
        if option1_selected:
            selected_translation = paragraph_text
        else:
            selected_translation = ""

        for i, slice_text in enumerate(slices):
            key = f"{verse_id}_option_{i}"
            if st.checkbox(slice_text, key=key, value=slice_text in prev_translation):
                selected_translation += slice_text + " "

        push_translation_key = f"push_translation_{index}"
        if st.button("Push Translation", key=push_translation_key):
            if selected_translation.strip():
                update_master_dataframe(df_master, verse_id, selected_translation.strip())

            st.session_state[f'options_{index}'] = []

            st.markdown("---")
            st.subheader("Latest Translation")
            latest_translation = df_master.loc[df_master['Verse Number'] == verse_id, 'Translation'].values
            if len(latest_translation) > 0:
                latest_translation = latest_translation[0]
            else:
                latest_translation = ""
            st.markdown(f"**Verse Number:** {verse_id}")
            st.markdown(f"**Translation:** {latest_translation}")
            st.markdown("---")

    else:
        st.warning("Verse index out of range.")

display_verse_and_options(st.session_state.current_index)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:

    st.markdown("---")
    if st.session_state.current_index > 0:
        prev_key = f'prev_{st.session_state.current_index}'
        if st.button(f'Previous', key=prev_key):
            st.session_state.current_index -= 1

    if st.session_state.current_index < len(verses_df) - 1:
        next_key = f'next_{st.session_state.current_index}'
        if st.button(f'Next', key=next_key):
            st.session_state.current_index += 1

st.markdown("---")
st.subheader("Master Translations")
st.write(df_master)
st.markdown("---")

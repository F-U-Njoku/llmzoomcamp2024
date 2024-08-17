# Import necessary decorators if not already in the global namespace
import io
import requests
import docx

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def clean_line(line):
    line = line.strip()
    line = line.strip('\uFEFF')
    return line

def read_faq(file_id):
    url = f'https://docs.google.com/document/d/{file_id}/export?format=docx'
    
    response = requests.get(url)
    response.raise_for_status()
    
    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)

    questions = []

    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'
    
    heading_id = ''
    section_title = ''
    question_title = ''
    answer_text_so_far = ''
     
    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)
    
        if len(p_text) == 0:
            continue
    
        if style == section_heading_style:
            section_title = p_text
            continue
    
        if style == question_heading_style:
            answer_text_so_far = answer_text_so_far.strip()
            if answer_text_so_far != '' and section_title != '' and question_title != '':
                questions.append({
                    'text': answer_text_so_far,
                    'section': section_title,
                    'question': question_title,
                })
                answer_text_so_far = ''
    
            question_title = p_text
            continue
        
        answer_text_so_far += '\n' + p_text
    
    answer_text_so_far = answer_text_so_far.strip()
    if answer_text_so_far != '' and section_title != '' and question_title != '':
        questions.append({
            'text': answer_text_so_far,
            'section': section_title,
            'question': question_title,
        })

    return questions
@data_loader
def load_data(*args, **kwargs) -> list[dict]:
    """
    Load data from a Google Docs document using its file ID and extract sections and questions.

    Args:
        file_id (str): The Google Docs file ID.

    Returns:
        List[dict]: A list of dictionaries containing questions and their corresponding sections and answers.
    """
    # Check if file_id is provided; if not, raise an error

    # Construct the URL for downloading the document as a DOCX file
    file_id = "1T3MdwUvqCL3jrh3d3VCXQ8xE0UqRzI3bfgpfBq3ZWG0"
    questions = read_faq(file_id)
    
    return questions

@test
def test_output(documents, *args) -> None:
    """
    Test the output of the `load_data` function.
    """
    faq_documents = {
        'llm-zoomcamp': '1T3MdwUvqCL3jrh3d3VCXQ8xE0UqRzI3bfgpfBq3ZWG0',
    }
    
    documents = []

    for course, file_id in faq_documents.items():
        print(course)
        course_documents = load_data(file_id = file_id)
        documents.append({'course': course, 'documents': course_documents})

    assert documents is not None, 'The output is undefined.'

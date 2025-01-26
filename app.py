import streamlit as st
from RSM_Solver import solve_problem, solve_from_latex, solve_from_image

st.title("Russian School of Math Solver")

# Input method selection
input_method = st.radio(
    "Choose input method",
    ["RSM Login", "LaTeX Input", "Image Upload"]
)

if input_method == "RSM Login":
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        question_num = st.number_input("Question Number", min_value=0, step=1)
        submit = st.form_submit_button("Solve Problem")
        
    if submit:
        with st.spinner('Processing...'):
            try:
                latex_form, solution, thinking = solve_problem(username, password, question_num)
                show_solution = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                show_solution = False

elif input_method == "LaTeX Input":
    with st.form("latex_form"):
        latex_input = st.text_area("Enter LaTeX expression")
        submit = st.form_submit_button("Solve Problem")
        
    if submit and latex_input:
        with st.spinner('Processing...'):
            try:
                latex_form, solution, thinking = solve_from_latex(latex_input)
                show_solution = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                show_solution = False

else:  # Image Upload
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        with st.spinner('Processing...'):
            try:
                image_bytes = uploaded_file.getvalue()
                latex_form, solution, thinking = solve_from_image(image_bytes)
                show_solution = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                show_solution = False

# Display solution if available
if 'show_solution' in locals() and show_solution:
    st.subheader("Problem")
    st.latex(latex_form)
    
    st.subheader("Solution")
    paragraphs = solution.split('\n\n')
    for para in paragraphs:
        if para.strip():
            if para.strip().startswith('$$') and para.strip().endswith('$$'):
                st.latex(para.strip()[2:-2])
            else:
                st.markdown(para)
    
    with st.expander("Show AI Thinking Process"):
        st.markdown(thinking)

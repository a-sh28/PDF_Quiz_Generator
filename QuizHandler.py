import streamlit as st
import os
import sys
import json
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
sys.path.append(os.path.abspath('../../'))


class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.question_bank = [] # Initialize the question bank to store questions
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
    
    def init_llm(self):
        self.llm = VertexAI(
            model_name = "gemini-pro",
            temperature = 0.8, 
            max_output_tokens = 1000
        )

    def generate_question_with_vectorstore(self):
        if not self.llm:
            self.init_llm()
        if not self.vectorstore.db:
            st.error("No PDF was submitted",icon='🚨')
            return
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel
        retriever = self.vectorstore.db.as_retriever()
        prompt = PromptTemplate.from_template(self.system_template)
        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        chain = setup_and_retrieval | prompt | self.llm 
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        self.question_bank = [] 
        while(len(self.question_bank)<self.num_questions):
        
            question_str = self.generate_question_with_vectorstore()
         
            try:
                question_str = json.loads(question_str)
                # Convert the JSON String to a dictionary
            except json.JSONDecodeError:
                print("Failed to decode question JSON.")
                continue 
        
            question = question_str["question"]
        
    
            if self.validate_question(question):
                print("Successfully generated unique question")
                self.question_bank.append(question_str)
               
            else:
                print("Duplicate or invalid question detected.")
   

        return self.question_bank

    def validate_question(self, question: dict) -> bool:
        
        is_unique=False
        questions =[i["question"] for i in self.question_bank]
        if question not in questions:
            is_unique=True
        return is_unique

class QuizManager:
    def __init__(self, questions: list):
        self.questions = questions
        self.total_questions= len(self.questions)
  
    def get_question_at_index(self, index: int):
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    def next_question_index(self, direction=1):
        current_index = st.session_state['question_index']
        current_index = (current_index + direction)%self.total_questions
        st.session_state['question_index'] = current_index
  



          
             
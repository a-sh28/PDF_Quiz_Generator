# PDF_Quiz_Generator
A Quiz generator that generates MCQs based on certain input PDFs and a topic of interest.
##Description
The Quiz Generator is a web application that aims in building a quiz based on the content from uploaded PDFs and a topic of interest.
The UI is built using StreamLit, while the quiz generation algorithm is developed using Langchain, Chroma DB and Google Vertex AI. 
Gemini API is used for generation of questions.

## UseCases
1. Can be utilised for effective learning by testing oneself with custom questions from a specific topic based on the reading PDF materials.
2. Can be utilised by instructors to generate questions for testing students.
3. Can be utilised for on-spot and customised quiz making in competitions.

## Helpfulness
### How does utilising the application differ from uploading the PDFs to a LLM and prompting for questions?
1. The application ensures that the questions generated are to the point with the input contexts - PDFs and topic.
2. It does not leverage the memory of the LLM to generate questions based on the topic, hence hallucination is eliminated.
3. A more sophisticated UI to naviagte the quiz, with explanation of why each answer is correct/incorrect.

## Usage
### Installation



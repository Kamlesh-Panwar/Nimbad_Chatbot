import json
from rank_bm25 import BM25Okapi

class ChatbotModel:
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        self.questions = []
        self.answers = []
        self.labels = []

        for idx, item in enumerate(data):
            if isinstance(item['question'], list):
                questions = item['question']
            else:
                questions = [item['question']]

            for q in questions:
                self.questions.append(q.lower())
                self.answers.append(item['answer'])
                self.labels.append(idx)

        # Tokenize questions
        self.tokenized_questions = [q.split() for q in self.questions]

        # BM25 model
        self.bm25 = BM25Okapi(self.tokenized_questions)

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        tokenized_query = user_input.split()

        scores = self.bm25.get_scores(tokenized_query)

        best_idx = scores.argmax()
        best_score = scores[best_idx]

        print("BM25 Score:", best_score)

        if best_score < 1.0:
            return "Sorry, I didn't understand. Please contact our team."

        return self.answers[best_idx]
# import json
# import random
# from rank_bm25 import BM25Okapi

# class ChatbotModel:
#     def __init__(self, json_path):
#         with open(json_path, 'r') as f:
#             data = json.load(f)

#         self.patterns = []
#         self.responses = []
#         self.tags = []
#         self.suggestions_map = {}
#         self.last_suggestions = []

#         for item in data:
#             tag = item['tag']
#             patterns = item['patterns']
#             responses = item['responses']

#             self.suggestions_map[tag] = item.get("suggestions") or []

#             for pattern in patterns:
#                 self.patterns.append(pattern.lower())
#                 self.responses.append(responses)
#                 self.tags.append(tag)

#         self.tokenized_patterns = [p.split() for p in self.patterns]
#         self.bm25 = BM25Okapi(self.tokenized_patterns)

#     def generate_suggestions(self, user_input, top_n=3):
#         tokenized_query = user_input.lower().split()
#         scores = self.bm25.get_scores(tokenized_query)

#         ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

#         suggestions = []
#         for idx in ranked_indices:
#             q = self.patterns[idx]
#             if q == user_input:
#                 continue
#             if q in self.last_suggestions:
#                 continue
#             if q in suggestions:
#                 continue
#             suggestions.append(q)

#             if len(suggestions) < top_n:
#                 remaining = list(set(self.patterns) - set(suggestions))
#                 random.shuffle(remaining)

#                 for q in remaining:
#                     if q not in self.last_suggestions:
#                         suggestions.append(q)
#                     if len(suggestions) >= top_n:
#                         break
#             self.last_suggestions = suggestions
#             return suggestions

#     def get_response(self, user_input):
#         user_input = user_input.lower().strip()
#         tokenized_query = user_input.split()

#         scores = self.bm25.get_scores(tokenized_query)
#         best_idx = scores.argmax()
#         best_score = scores[best_idx]

#         print("BM25 Score:", best_score)
#         auto_suggestions = self.generate_suggestions(user_input) or []

#         if best_score < 1:
#             return {
#                 "response": "Sorry, I didn't understand. Can you rephrase your question?",
#                 "suggestions": auto_suggestions
#             }

#         tag = self.tags[best_idx]
#         response = random.choice(self.responses[best_idx])

#         dataset_suggestions = self.suggestions_map.get(tag) or [] 

#         final_suggestions = list(dict.fromkeys((dataset_suggestions or []) + (auto_suggestions or [])))[:3]

#         return {
#             "response": response,
#             "suggestions": final_suggestions
#         }
import json
import random
import re
from rank_bm25 import BM25Okapi
import requests

class ChatbotModel:
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        self.patterns = []
        self.responses = []
        self.tags = []
        self.suggestions_map = {}
        self.last_suggestions = []

        for item in data:
            tag = item.get('tag', "")
            patterns = item.get('patterns', [])
            responses = item.get('responses', [])

            self.suggestions_map[tag] = item.get("suggestions") or []

            for pattern in patterns:
                cleaned = self.clean_text(pattern)
                self.patterns.append(cleaned)
                self.responses.append(responses)
                self.tags.append(tag)

        self.tokenized_patterns = [p.split() for p in self.patterns]
        self.bm25 = BM25Okapi(self.tokenized_patterns)

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
        return text.strip()


    def generate_suggestions(self, user_input, top_n=3):
        cleaned_input = self.clean_text(user_input)
        tokenized_query = cleaned_input.split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        suggestions = []

        for idx in ranked_indices:
            q = self.patterns[idx]

            if q == cleaned_input:
                continue
            if q in suggestions:
                continue
            if q in self.last_suggestions:
                continue

            suggestions.append(q)

            if len(suggestions) >= top_n:
                break

        if len(suggestions) < top_n:
            remaining = list(set(self.patterns) - set(suggestions))
            random.shuffle(remaining)

            for q in remaining:
                if q not in suggestions and q not in self.last_suggestions:
                    suggestions.append(q)
                if len(suggestions) >= top_n:
                    break

        self.last_suggestions = suggestions
        return suggestions

    def get_response(self, user_input):
        if not user_input or not user_input.strip():
            return {
                "response": "Please enter a message.",
                "suggestions": ["services", "pricing", "contact"]
            }

        cleaned_input = self.clean_text(user_input)
        tokenized_query = cleaned_input.split()

        scores = self.bm25.get_scores(tokenized_query)

        best_idx = scores.argmax()
        best_score = scores[best_idx]

        print("BM25 Score:", best_score)

        THRESHOLD = 5.5

        auto_suggestions = self.generate_suggestions(cleaned_input) or []

        if best_score < THRESHOLD:
            ai_response = get_ollama_response(user_input)

            return {
                "response": ai_response,
                "suggestions": auto_suggestions
            }

        tag = self.tags[best_idx]
        response = random.choice(self.responses[best_idx])

        dataset_suggestions = self.suggestions_map.get(tag) or []

        final_suggestions = list(dict.fromkeys(dataset_suggestions + auto_suggestions))[:3]

        return {
            "response": response,
            "suggestions": final_suggestions
        }
    
def get_ollama_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",   # you can change model
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"].strip()
    except Exception as e:
        return "AI service is not available right now."
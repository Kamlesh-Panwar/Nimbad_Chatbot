import json
import random
from flask.cli import load_dotenv
from rank_bm25 import BM25Okapi
import requests
import os
import random
class ChatbotModel:
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)

        self.patterns = []
        self.responses = []
        self.tags = []
        self.suggestions_map = {}
        self.used_patterns = set()
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

        response = random.choice(self.responses[best_idx])

        patterns_suggestions = self.get_unique_suggestions()

        return {
            "response": response,
            "suggestions": patterns_suggestions
        }
    def get_unique_suggestions(self, count=3):

        pattern_tag_pairs = list(zip(self.patterns, self.tags))
        filtered = [
            p for p, t in pattern_tag_pairs
            if t.lower() not in ["greeting", "goodbye"]
        ]
    
        available = [p for p in filtered if p not in self.used_patterns]

        if len(available) == 0:
            self.used_patterns.clear()
            available = self.patterns.copy()

        selected = random.sample(available, min(count, len(available)))

        for s in selected:
            self.used_patterns.add(s)

        return selected
    
def get_ollama_response(prompt):
    try:
        response = requests.post(
            os.getenv("AI_API_URL"),
            json={
                "model": "mistral",
                # "model": "phi",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"].strip()
    except Exception as e:
        return "AI service is not available right now."
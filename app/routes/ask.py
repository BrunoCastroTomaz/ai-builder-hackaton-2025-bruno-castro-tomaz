from flask import Blueprint, request, jsonify
from app.services.rag_service import RagService

ask_bp = Blueprint("ask", __name__)
rag = RagService()  

@ask_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    answer = rag.answer_question(question)
    return jsonify({"answer": answer})

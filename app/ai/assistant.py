# app/ai/assistant.py

from app.models.product import Product

class ChatAssistant:
    """
    A rule-based AI assistant for the Celia Fashion Live store.
    Handles customer queries and provides product recommendations.
    """

    def get_response(self, message, session_data=None):
        """
        Generates a response to a user's message based on simple rules.

        Args:
            message (str): The user's input message.
            session_data (dict, optional): Data from the user's session. Defaults to None.

        Returns:
            dict: A response dictionary containing the reply and other actions.
        """
        # TODO: Replace this simple logic with a proper NLP/NLU engine (e.g., Rasa, Dialogflow, or a custom model with OpenAI).

        lower_message = message.lower().strip()

        # Greeting
        if any(greeting in lower_message for greeting in ['hello', 'hi', 'hey', 'مرحبا', 'أهلاً', 'ازيك']):
            return self._greeting_response()

        # Basic Questions
        if 'سعر' in lower_message or 'price' in lower_message:
            return self._static_response("أسعارنا تنافسية جداً! ممكن تقوليلي إيه المنتج اللي بتسألي عليه عشان أقولك سعره؟")

        if 'مقاس' in lower_message or 'size' in lower_message:
            return self._static_response("عندنا كل المقاسات من S لـ XXL. تحبي تعرفي مقاسات موديل معين؟")

        if 'خامات' in lower_message or 'material' in lower_message:
            return self._static_response("بنستخدم أجود الخامات زي القطن المصري والحرير الصناعي. إيه الموديل اللي بتسألي على خامته؟")

        if 'توصيل' in lower_message or 'shipping' in lower_message:
            return self._static_response("التوصيل متاح لكل محافظات مصر. بيوصلك في خلال 3-5 أيام عمل.")

        if 'استرجاع' in lower_message or 'return' in lower_message:
            return self._static_response("تقدري تسترجعي أو تستبدلي المنتج خلال 14 يوم من الاستلام، بس اتأكدي إنه في حالته الأصلية.")

        # Follow-up Questions (Leading to recommendations)
        if 'مناسبة' in lower_message or 'event' in lower_message:
            return self._ask_for_occasion()

        # Fallback response
        return self._fallback_response()

    def _greeting_response(self):
        return {
            "reply": "أهلاً بيكي في سيليا فاشون! ✨ إزاي أقدر أساعدك النهاردة؟",
            "action": "none"
        }

    def _ask_for_occasion(self):
        return {
            "reply": "طبعاً! قوليلي المناسبة دي خروجة عادية ولا سهرة؟ عشان أرشحلك أنسب حاجة. 😉",
            "action": "awaiting_occasion_type"
        }

    def _static_response(self, reply):
        return {
            "reply": reply,
            "action": "none"
        }

    def _fallback_response(self):
        return {
            "reply": "عفواً، ممكن توضحي سؤالك أكتر؟ مقدرتش أفهمك.",
            "action": "none"
        }

# Global instance of the assistant
chat_assistant = ChatAssistant()

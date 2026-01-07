import os
from openai import OpenAI
from app.models.product import Product

class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.system_prompt = """
        أنت مساعد ذكي لمتجر ملابس أونلاين اسمه "Celia Fashion Live".
        جمهورك: نساء في مصر.
        اللغة: عربي مصري احترافي (سهل – ودي – بيع من غير ضغط).
        أسلوب الرد:
        - عربي مصري
        - ودود
        - ذكي
        - مختصر
        - بيع غير مباشر
        مثال: "تمام 👌 قولي بس هتلبسيه خروج ولا شغل وأنا أظبطك على مزاجك"
        
        مهامك:
        1. الرد على أسئلة العملاء (الأسعار، المقاسات، الخامات، التوصيل، الاسترجاع).
        2. طرح أسئلة ذكية لفهم العميل (كاجوال ولا خروج؟ مناسبة إيه؟ مقاسك؟ ألوان غامقة ولا فاتحة؟).
        3. ترشيح منتجات بناءً على (نوع الاستخدام، الذوق، المقاس، اللون، الموسم).
        """

    def get_response(self, user_message, context=None):
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            if context:
                messages.append({"role": "system", "content": f"سياق المنتجات المتاحة: {context}"})
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in AI Assistant: {e}")
            return "يا هلا بيكي! نورتي Celia Fashion. قوليلي محتاجة مساعدة في إيه وأنا معاكي؟ 😊"

assistant = AIAssistant()

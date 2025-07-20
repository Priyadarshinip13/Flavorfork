import google.generativeai as genai

# genai.configure(api_key="AIzaSyC6SlJq9twu2Sy4d9BaqCqsi9V-Z1oiREw")
# for m in genai.list_models():
#     print(m.name)

import google.generativeai as genai

genai.configure(api_key="AIzaSyC6SlJq9twu2Sy4d9BaqCqsi9V-Z1oiREw")

# Correct model name: "models/gemini-pro"
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

response = model.generate_content("What's on the menu today?")
print(response.text)


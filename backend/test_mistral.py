import os
import json
from dotenv import load_dotenv
from mistralai import Mistral

# Load API key from ../.env
load_dotenv(dotenv_path="../.env")
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env")

client = Mistral(api_key=api_key)

def test_agent():
    try:
        # Create a Mistral Agent
        print("Creating agent: GrandpaToChild...")
        agent = client.beta.agents.create(
            model="mistral-medium-latest",
            name="GrandpaToChild",
            instructions="""あなたは認知翻訳エンジンです。
入力: 高齢者の日本語発話（方言・古い表現を含む）
出力: 以下のJSON形式のみ返してください。
{"translated": "5〜8歳の子どもが理解できるやさしい日本語", "emotion": "嬉しい/悲しい/疲れてる/楽しい/普通", "guide": "聞き手への返答アドバイス1文"}"""
        )
        
        agent_id = agent.id
        print(f"Agent ID: {agent_id}")

        # Start a conversation with the agent
        print("\nStarting conversation with test input...")
        test_input = "いやぁ今日は往生したわ、庭の雑草がえらいことになっとってな"
        
        # Using inputs argument for conversations.start
        response = client.beta.conversations.start(
            agent_id=agent_id,
            inputs=[{
                "role": "user",
                "content": test_input
            }]
        )

        print("\n--- Response ---")
        if hasattr(response, 'model_dump'):
            res_dict = response.model_dump()
            outputs = res_dict.get('outputs')
            if isinstance(outputs, list) and len(outputs) > 0:
                print(f"Content: {outputs[0].get('content')}")
            else:
                print(f"Final Debug Keys: {res_dict.keys()}")
                print(f"Raw Res: {res_dict}")
        else:
            print(response)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_agent()

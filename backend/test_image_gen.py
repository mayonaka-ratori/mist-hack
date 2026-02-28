import os
import sys
import time
import json
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv(dotenv_path=".env")
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env")

client = Mistral(api_key=api_key)

benchmark_prompt = "Generate a warm, child-friendly watercolor illustration of a smiling elderly Japanese man in a garden pointing at bright red tomatoes on the vine. Sunny day, gentle soft style."

def benchmark_image_agent(model_name: str):
    print(f"\n--- Testing Approach ({model_name}) ---")
    start_time = time.time()

    try:
        # エージェントを作成 (画像生成ツールを有効化)
        print(f"Creating agent with model: {model_name}...")
        from mistralai.models import ImageGenerationTool
        agent = client.beta.agents.create(
            name=f"ImageGenerator_{model_name}_{int(time.time())}",
            model=model_name,
            instructions="あなたは優秀なイラストレーターです。ユーザーの指示に従ってイラストを生成してください。",
            tools=[ImageGenerationTool()]
        )

    except Exception as e:
        print(f"Failed to create agent: {e}")
        return

    agent_id = agent.id
    print(f"Agent ID: {agent_id}")

    print("Sending prompt to generate image...")
    try:
        response = client.beta.conversations.start(
            agent_id=agent_id,
            inputs=[{
                "role": "user",
                "content": benchmark_prompt
            }]
        )
        
        end_time = time.time()
        elapsed = end_time - start_time

        print(f"Elapsed Time: {elapsed:.2f} seconds")
        
        # 画像生成の結果（URLやファイルID）を取得
        if hasattr(response, 'model_dump'):
            res_dict = response.model_dump()
            outputs = res_dict.get('outputs')
            if isinstance(outputs, list) and len(outputs) > 0:
                output_text = outputs[0].get('content')
                if output_text is None:
                    output_text = json.dumps(res_dict, indent=2)
            else:
                output_text = f"Raw Res: {res_dict}"
        else:
            output_text = str(response)

        print(f"Result for {model_name} written to {model_name}.md")
        with open(f"{model_name}.md", "w", encoding="utf-8") as f:
            f.write(str(output_text))

    except Exception as e:
        end_time = time.time()
        print(f"Exception during conversation after {end_time - start_time:.2f} seconds: {e}")

if __name__ == "__main__":
    benchmark_image_agent("mistral-medium-latest")
    benchmark_image_agent("mistral-small-latest")

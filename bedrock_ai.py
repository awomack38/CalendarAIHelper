import boto3
import json
from botocore.exceptions import BotoCoreError, ClientError

def generate_schedule(user_input, current_events):
    # Format calendar context
    context = "Upcoming calendar events:\n"
    for e in current_events:
        context += f"- {e['summary']} at {e['start']}\n"

    full_prompt = (
        f"{context}\n"
        f"\nBased on the above, create a schedule from this request:\n"
        f"\"{user_input}\"\n"
        f"Respond with a list of events. Each should include: summary, start time (plain English), and duration in minutes."
    )

    try:
        client = boto3.client("bedrock-runtime", region_name="us-east-1")

        body = {
            "prompt": f"Human: {full_prompt}\nAssistant:",
            "max_tokens_to_sample": 500,
            "temperature": 0.7,
            "stop_sequences": ["\n\n"]
        }

        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        text = result.get("completion", "")

        suggestions = []
        for line in text.splitlines():
            if line.strip().startswith("-"):
                parts = line[1:].split(" at ")
                if len(parts) == 2:
                    summary = parts[0].strip()
                    time_part = parts[1].strip()
                    if " for " in time_part:
                        start, duration = time_part.split(" for ")
                        suggestions.append({
                            "summary": summary,
                            "start": start.strip(),
                            "duration": int(''.join(filter(str.isdigit, duration)))
                        })

        return suggestions

    except (BotoCoreError, ClientError) as e:
        print(f"❌ Error calling Bedrock: {e}")
        return []

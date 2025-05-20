from bedrock_ai import generate_schedule
from gcal import list_upcoming_events, create_event

def main():
    print("\n🧠 AI Calendar Assistant (AWS-Powered)")
    print("----------------------------------")

    # Step 1: Get upcoming calendar events
    print("\n📅 Fetching upcoming events...")
    events = list_upcoming_events()
    for e in events:
        print(f"- {e['summary']} at {e['start']}")

    # Step 2: Get user input
    user_input = input("\nWhat would you like to schedule?\n> ")

    # Step 3: Generate suggestions using Claude via Bedrock
    print("\n🤖 Generating suggestions with Claude...")
    suggestions = generate_schedule(user_input, events)

    # Step 4: Show suggestions
    if not suggestions:
        print("\n⚠️ No suggestions generated.")
        return

    print("\n✅ Suggested Schedule:")
    for idx, event in enumerate(suggestions):
        print(f"{idx + 1}. {event['summary']} at {event['start']} for {event['duration']} minutes")

    # Step 5: Confirm and write to Google Calendar
    confirm = input("\nDo you want to add these to your calendar? (y/n): ")
    if confirm.lower() == 'y':
        for event in suggestions:
            create_event(event)
        print("\n🎉 Events added to your Google Calendar!")
    else:
        print("\n❌ No changes made.")


if __name__ == "__main__":
    main()

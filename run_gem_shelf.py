from agents.shelf_analyst.gem_agent import chat

while True:
    question = input("> ")

    if question.lower() in ["exit", "quit"]:
        break

    response = chat.send_message(question)

    print()
    print(response.text)
    print()
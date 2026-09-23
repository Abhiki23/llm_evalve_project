## Responsible for runing the main project, which will take the user input

from rag_chain import generate_answer

def main():
    print("Hello from rag-project!")

    while True:
        query = input("\n Ask a question: ").strip()

        ## Handle empty input:

        if not query:
            print("Please enter a valid question")
            continue

        ## Exit condition
        if query.lower() in ["exit", "quit"]:
            print("Exiting RAG application")
            break

        ## Execute RAG pipeline
        try:
            answer = generate_answer(query)
            print("\n Answer: ")
            print(answer)
        except Exception as e:
            print(f"\nError : {e}")


if __name__ == "__main__":
    main()

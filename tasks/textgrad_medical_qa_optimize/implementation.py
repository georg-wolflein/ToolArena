def textgrad_medical_qa_optimize(
    csv_path: str = "/mount/input/sample_0.csv",
    backward_engine: str = "gpt-4o",
    forward_engine: str = "gpt-3.5-turbo",
    starting_system_prompt: str = "You are ChatGPT...",
    optimizer_constraint: str = "The last line of your response should be of the format: 'Answer: $LETTER' ..."
) -> dict:
    """
    Optimize answers to multiple-choice medical QA questions using TextGrad.

    Args:
        csv_path: Path to a CSV file with columns: 'index', 'question', 'objective'
        backward_engine: The model used for generating textual gradients (e.g., 'gpt-4o')
        forward_engine: The model used for initial zero-shot answers (e.g., 'gpt-3.5-turbo')
        starting_system_prompt: The system prompt passed to the LLM for zero-shot answer generation
        optimizer_constraint: Constraint string that guides the optimizer to produce well-formatted answers

    Returns:
        dict with the following structure:
        {
            'optimized_answers': list of dicts with keys:
                - index (int)
                - init_answer (str)
                - optimized_answer (str)
        }
    """
    import pandas as pd
    import textgrad as tg

    df = pd.read_csv(csv_path)

    tg.set_backward_engine(backward_engine, override=True)
    llm_engine = tg.get_engine(forward_engine)

    def get_zeroshot_answer(question):
        system_prompt = tg.Variable(starting_system_prompt, requires_grad=False, role_description="system prompt to the language model")
        model = tg.BlackboxLLM(llm_engine, system_prompt)
        response = model(tg.Variable(question, requires_grad=False, role_description="question to the language model"))
        return response

    optimized_answers = []

    for _, row in df.iterrows():
        question = row["question"]
        objective = row["objective"]
        sample_index = row["index"]

        print(f"🔍 Processing question index {sample_index}...")

        zero_shot = get_zeroshot_answer(question)
        zero_shot_text = zero_shot.value.strip()

        answer_var = tg.Variable(
            zero_shot_text,
            requires_grad=True,
            role_description="concise and precise prediction for the multiple choice question"
        )

        optimizer = tg.TextualGradientDescent(
            engine=llm_engine,
            parameters=[answer_var],
            constraints=[optimizer_constraint]
        )
        loss_fn = tg.TextLoss(objective)

        loss = loss_fn(answer_var)
        loss.backward()
        optimizer.step()

        optimized_answers.append({
            "index": int(sample_index),
            "init_answer": zero_shot_text,
            "optimized_answer": answer_var.value.strip()
        })

    return {"optimized_answers": optimized_answers}

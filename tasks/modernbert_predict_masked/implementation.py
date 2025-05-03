def modernbert_predict_masked(
    input_string: str = "Paris is the [MASK] of France.",
) -> dict:
    """
    Given a masked sentence string, predict the original sentence using the pretrained ModernBERT-base model on CPU.

    Args:
        input_string: The masked sentence string. The masked part is represented by "[MASK]"".

    Returns:
        dict with the following structure:
        {
          'prediction': str  # The predicted original sentence
        }
    """
    # Adapted from https://huggingface.co/answerdotai/ModernBERT-base
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    model_id = "answerdotai/ModernBERT-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForMaskedLM.from_pretrained(model_id)

    inputs = tokenizer(input_string, return_tensors="pt")
    outputs = model(**inputs)

    masked_index = inputs["input_ids"][0].tolist().index(tokenizer.mask_token_id)
    predicted_token_id = outputs.logits[0, masked_index].argmax(axis=-1)
    predicted_token = tokenizer.decode(predicted_token_id)

    # Replace the masked part with the predicted token
    predicted_sentence = input_string.replace("[MASK]", predicted_token)

    return {"prediction": predicted_sentence}

def esm_fold_predict(
    sequence: str = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
) -> dict:
    """
    Generate the representation of a protein sequence and the contact map using Facebook Research's pretrained esm2_t33_650M_UR50D model.

    Args:
        sequence: Protein sequence to for which to generate representation and contact map.

    Returns:
        dict with the following structure:
        {
          'sequence_representation': list  # Token representations for the protein sequence as a list of floats, i.e. a 1D array of shape L where L is the number of tokens.
          'contact_map': list  # Contact map for the protein sequence as a list of list of floats, i.e. a 2D array of shape LxL where L is the number of tokens.
        }
    """
    import esm
    import torch

    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()

    batch_converter = alphabet.get_batch_converter()
    data = [("protein1", sequence)]
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    tokens_len = (batch_tokens != alphabet.padding_idx).sum(1).squeeze(0)

    # Extract per-residue representations (on CPU)
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=True)
    token_representations = results["representations"][33]

    # Generate per-sequence representations via averaging
    # NOTE: token 0 is always a beginning-of-sequence token, so the first residue is token 1.
    sequence_representation = token_representations[0, 1 : tokens_len - 1].mean(0)

    return {
        "sequence_representation": sequence_representation.tolist(),
        "contact_map": results["contacts"][0, :tokens_len, :tokens_len].tolist(),
    }

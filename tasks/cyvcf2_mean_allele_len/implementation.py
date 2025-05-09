def cyvcf2_mean_allele_len(
    input_vcf: str = "/mount/input/SRR2058984_zc.vcf",
) -> int:
    """
    Extract mean allele length amongst all variants in the input VCF file.

    Args:
        input_vcf: Path to the input VCF file

    Returns:
        integer value of the mean allele length of all variants in the input file 
    """
    import os
    import numpy as np
    from cyvcf2 import VCF

    len_values = []
    for variant in VCF(input_vcf):
        allele_len = variant.INFO.get('LEN')
        if allele_len is not None:
            len_values.append(variant.INFO.get('LEN'))

    mean_len = int(np.mean(len_values))

    return mean_len

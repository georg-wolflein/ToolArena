def cyvcf2_count_alterations(
    input_vcf: str = "/mount/input/SRR2058984_zc.vcf",
    reference_nucleotide: str = "A",
    alternate_nucleotide: str = "C",
) -> dict:
    """
        Use the cyvcf2 to parse through VCF file containing detected sequence variants to identify the number of single
    nucleotide polymorphisms (SNPs) from a specific reference nucleotide to a specific alternate nucleotide.

        Args:
            input_vcf: Path to the input VCF file
            reference_nucleotide: The reference nucleotide to compare against ("A", "C", "G", or "T")
            alternate_nucleotide: The alternate nucleotide to compare against ("A", "C", "G", or "T")

        Returns:
            dict with the following structure:
            {
              'num_snps': int  # The number of SNPs that are altered from reference `reference_nucleotide` to
    `alternate_nucleotide`.
            }
    """
    from cyvcf2 import VCF

    # Initialize counters
    num_snps = 0

    # Iterate over each variant
    for variant in VCF(input_vcf):
        if (
            variant.is_snp
            and variant.REF == reference_nucleotide
            and variant.ALT
            and variant.ALT[0] == alternate_nucleotide
        ):
            num_snps += 1

    return {"num_snps": num_snps}

# Voting System Analysis - README

## Overview

This directory contains an analysis of End-to-End Verifiable (E2E-V) voting systems, with a focus on answering questions raised in [FreeAndFair/VoteSecure Issue #2](https://github.com/FreeAndFair/VoteSecure/issues/2).

## Documents

### [voting_system_analysis.md](./voting_system_analysis.md)
Comprehensive analysis addressing seven key questions about the VoteSecure E2E-V voting system SDK, including:

1. **Receipt-freeness** - Can voters prove how they voted?
2. **Verification specification** - Is there a formal spec for independent verification?
3. **Client compromise** - How is cast-as-intended verification protected?
4. **Public proofs** - Are mixing and decryption proofs on the public bulletin board?
5. **Trust assumptions** - What must trustees be trusted for?
6. **Printer security** - How are compromised printers detected?
7. **System comparison** - How does it compare to Helios, Belenios, Swiss Post, and 7th Estate?

## Key Findings

### VoteSecure Analysis
- Similar receipt-freeness challenges to Helios (allows potential vote-buying)
- Needs formal verification specification for independent auditing
- Client compromise mitigation requires better documentation
- Trust assumptions need explicit documentation

### 7th Estate Innovation
The [7th Estate / Grassroots Democracy](https://github.com/xxfoundation/7th_estate) system introduces novel approaches:

- **Decoy ballots** - Solves vote-buying through unverifiable decoy ballots mixed with real ones
- **Hybrid paper/digital** - Physical ballots protect against client malware
- **Statistical sampling** - Efficient verification through random sampling
- **Multi-channel verification** - Paper + digital + public ledger

### System Comparison

| System | Receipt-Free | E2E-V | Key Strength |
|--------|--------------|-------|--------------|
| Helios | No | Yes | Simple, well-studied |
| Belenios | No | Yes | Formal proofs |
| Swiss Post | No | Yes | Commercial scale |
| VoteSecure | Unclear | Partial | SDK flexibility |
| 7th Estate | Yes (decoys) | Yes | Coercion resistance |

## Relevance to Cosmic Neighborhoods

While this repository focuses on astronomical survey assignments, the analysis reveals interesting parallels:

### Trust and Verification Principles

1. **Deterministic Algorithms** - Both voting tallies and cosmic assignments must be verifiable
2. **Fairness Guarantees** - Mathematical distribution of votes/patches
3. **Public Auditability** - Open source enables trust through transparency
4. **Balance of Privacy and Verification** - Different but related concerns

### Statistical Methods

- 7th Estate uses random sampling for efficient verification
- Cosmic Neighborhoods uses population statistics for fair distribution
- Both rely on well-understood statistical principles

### Distributed Trust

- Voting systems use threshold cryptography to distribute trust
- Assignment systems use open algorithms and reproducible results
- Both avoid single points of failure

## Recommendations

For anyone implementing or evaluating E2E-V voting systems:

1. **Document threat model explicitly** - What are attacker capabilities?
2. **Provide formal verification spec** - Enable independent implementation
3. **Address receipt-freeness** - If sacrificed, explain mitigations
4. **Multi-device verification** - Don't rely on single compromised device
5. **Consider hybrid approaches** - Physical + digital (like 7th Estate)
6. **Publish all proofs** - Essential for true end-to-end verifiability

## Further Reading

### Voting Systems
- [Random Sample Voting](https://rsvoting.org/) - David Chaum's work on statistical voting
- [Helios Voting](https://vote.heliosvoting.org/) - Open source internet voting
- [Belenios](https://www.belenios.org/) - Formally verified voting protocol
- [ElectionGuard](https://www.electionguard.vote/) - Microsoft's open source voting SDK

### Cryptographic Verification
- [Zero-Knowledge Proofs](https://en.wikipedia.org/wiki/Zero-knowledge_proof)
- [Threshold Cryptography](https://en.wikipedia.org/wiki/Threshold_cryptosystem)
- [Verifiable Random Functions](https://en.wikipedia.org/wiki/Verifiable_random_function)

### 7th Estate Resources
- [7th Estate Repository](https://github.com/xxfoundation/7th_estate)
- [Grassroots Democracy Booklet](https://github.com/xxfoundation/7th_estate/blob/main/Grassroots%20Democracy%20Booklet.pdf)
- [Technical Diagram](https://github.com/xxfoundation/7th_estate/blob/main/7th%20estate%20technical%20description%20v1.pdf)

## License

This analysis is provided under the MIT License, consistent with the cosmic_neighborhoods repository.

## Contributing

This analysis was created to address specific questions about voting system security and verification. Corrections, updates, or additional analysis are welcome via pull requests.

## Context

- **Repository**: cosmic_neighborhoods
- **Purpose**: Astronomical survey assignment system
- **Analysis Date**: November 2025
- **Primary Issue**: [FreeAndFair/VoteSecure#2](https://github.com/FreeAndFair/VoteSecure/issues/2)

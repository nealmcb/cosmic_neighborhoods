# Voting System Analysis: VoteSecure E2E-V Questions

## Overview

This document addresses the questions raised in [FreeAndFair/VoteSecure Issue #2](https://github.com/FreeAndFair/VoteSecure/issues/2) regarding End-to-End Verifiable (E2E-V) voting systems. The analysis considers the threat models, trust assumptions, and verifiability properties of VoteSecure, comparing them with other systems including the 7th Estate/Grassroots Democracy system, Helios, Belenios, and Swiss Post.

## Context

The questions were raised by @vteague regarding the VoteSecure SDK and its concept of operations (CONOPS). While this cosmic_neighborhoods repository is focused on astronomical survey assignments, the principles of cryptographic verification, distributed trust, and privacy-preserving systems have parallels in both domains.

---

## Question 1: Receipt-Freeness

**Q: It looks like no receipt-freeness claim is being made. From a receipt-freeness perspective it's very similar to Helios: a minor client-side modification could retain randomness and hence allow voters to prove how they voted. Am I understanding that right?**

### Analysis

Receipt-freeness is a critical property for preventing vote-buying and coercion. The concern is valid:

**VoteSecure (as described):**
- If voters have access to the randomness used in encryption, they can construct a proof of how they voted
- This is similar to Helios, which explicitly sacrifices receipt-freeness for cast-as-intended verification
- A malicious client could store the random values and later prove vote choice

**7th Estate Approach:**
- Uses **decoy ballots** as a novel solution to vote-buying
- Voters can receive economic incentives without linkage to their actual response
- Some ballots are intentionally fake (decoys), making it impossible to prove which ballot was real
- This is a unique approach that addresses receipt-freeness differently than traditional cryptographic methods

**Proposed Answer:**
Yes, that understanding appears correct based on the CONOPS. Without receipt-freeness, VoteSecure would be similar to Helios in allowing potential vote-selling through client-side modifications. The system relies on:
1. Secure client software (trusted not to retain randomness)
2. Legal/social deterrents against vote-buying
3. The assumption that most users won't modify their clients

**Recommendation:** Document this limitation clearly and consider:
- Whether vote-buying is a significant threat in the intended deployment contexts
- Alternative approaches like 7th Estate's decoy ballots
- Hybrid approaches combining traditional polling places (receipt-free) with remote voting (verifiable)

---

## Question 2: Verification Specification

**Q: Is there a verification spec somewhere?**

### Analysis

A formal verification specification is essential for E2E-V systems to ensure:
- Independent implementation of verifiers
- Auditability by third parties
- Clear definition of what security properties hold
- Reproducibility of verification results

**Best Practices:**
- **ElectionGuard** provides detailed verification specs separate from implementation
- **Belenios** has formal proofs of security properties
- **7th Estate** documents verification steps in technical diagrams and white papers

**Proposed Answer:**
A formal verification specification should include:
1. **Input format specifications** for all published data (ballots, proofs, commitments)
2. **Verification algorithms** described mathematically (not just in code)
3. **Security properties** and their formal definitions
4. **Test vectors** for validator implementation testing
5. **API specifications** for independent verifier development

Without seeing such a specification in the VoteSecure repository, this appears to be a gap that should be addressed, especially given the SDK nature of the project where multiple implementations may exist.

---

## Question 3: Cast-as-Intended Verification and Client Compromise

**Q: It looks like the adversary may compromise the voting client, and I see there's an assumption that malicious apps on the voter's phone may leverage their presence to compromise the voting application. That makes sense. However, it also looks as if the Ballot Check application runs on the same phone. So I have three questions:**

### Question 3a: What exactly is the threat model?

**Analysis:**

A clear threat model must specify:
- **Adversary capabilities**: What can the attacker do?
- **Trust assumptions**: What components must be trusted?
- **Security goals**: What properties must hold despite adversary actions?

**Comparison with 7th Estate:**
The 7th Estate system assumes:
- **Advanced Persistent Threats (APTs)** have access to all environments
- The random sampling process is irrefutably random and un-manipulatable
- Paper ballots provide a physical verification layer
- Blockchain/distributed ledger provides transparent tallying

**Proposed Answer:**
The threat model should explicitly document:

1. **Network adversary**: Can observe, delay, or drop messages
2. **Client compromise**: Malware can compromise voting client
3. **Server compromise**: What if bulletin board or election servers are compromised?
4. **Trustee compromise**: How many trustees must be honest?
5. **Privacy threats**: Who can learn individual votes?
6. **Integrity threats**: Who can change election outcome?

For each threat, document:
- Whether it's in-scope or out-of-scope
- What defenses exist
- What properties are lost if the defense fails

### Question 3b: Why is it reasonable to assume that the adversary can leverage cross-app security issues to compromise the voting application but not the checking application?

**Analysis:**

This is a critical security question. If the adversary can compromise the voting app, why not the verification app on the same device?

**Possible justifications:**
1. **Different attack surfaces**: Verification app might be simpler, less vulnerable
2. **Timing**: Verification happens after voting, attacker may have left device
3. **Detection**: Compromising both increases detection risk
4. **Reduced value**: Attacker focused on changing votes, not preventing verification

**7th Estate comparison:**
- Uses physical paper ballots as a separate verification channel
- Combines online submission with physical audit trail
- Observers can verify independently of any software

**Proposed Answer:**
This assumption appears problematic without additional justification. Better approaches:

1. **Use separate verification channel** (different device, web-based, paper)
2. **Assume both may be compromised** and design accordingly
3. **Provide multiple verification methods** (like 7th Estate's paper+digital)
4. **Use challenge-response protocols** that work even with compromised clients
5. **Enable proxy verification** where trusted parties can verify on voter's behalf

**From dmzimmerman's comment:** The ballot check can run on any device, and verification should ideally use an independent device. This helps but doesn't fully solve the problem if voters only use one device.

### Question 3c: Is there an easy way for voters to verify from another device?

**Analysis:**

**7th Estate approach:**
- Paper ballots mailed to voters
- Online submission with codes
- Independent verification through published encrypted rosters
- Multiple observers can verify without voter involvement

**Proposed Answer:**
Yes, enabling verification from another device is crucial. Best practices:

1. **Web-based verifier**: Publish a standalone web tool
2. **QR codes**: Vote receipt as QR code, scannable by any device
3. **Verification codes**: Short codes that can be manually entered
4. **Third-party verifiers**: Allow trusted parties to verify
5. **Public bulletin board**: Anyone can download and verify full election data

The verification process should:
- Not require the original voting device
- Not require special software installation
- Work with minimal technical knowledge
- Be documentable/auditatable

---

## Question 4: Mixing and Decryption Proofs

**Q: Are the mixing and decryption proofs published on the public BB?**

### Question 4a: If not, would you still claim E2E-V?

**Analysis:**

**Core principle of E2E-V:**
- **Cast-as-intended**: Voters verify their vote was recorded correctly
- **Recorded-as-cast**: Votes on bulletin board match what was cast
- **Tallied-as-recorded**: Published tally matches published votes

Without public proofs, the third property cannot be verified by anyone except those with access to the proofs.

**7th Estate approach:**
- All verification data published
- Statistical sampling for verification
- Public can audit the random sampling process
- Proof that tally matches sample

**Proposed Answer:**
No, without public mixing and decryption proofs on the bulletin board, the system cannot claim full E2E-V. At best, it provides:
- Cast-as-intended verification (if done correctly)
- Partial auditability (only by those with proof access)

True E2E-V requires:
- All ballots published (encrypted)
- All mixing proofs published
- All decryption proofs published
- Anyone can verify tally from published data

### Question 4b: If so, why does the data need to be transferred via USB stick to the Trustee Servers rather than letting the Trustees read the data off the BB?

**Analysis:**

**Security considerations:**
- **Air-gapping**: USB transfer provides isolation from network attacks
- **Trust**: May not trust internet connection to bulletin board
- **Verification**: Physical media provides audit trail

**Counterarguments:**
- **Authenticity**: How do trustees verify USB data matches BB data?
- **Efficiency**: Network transfer is faster and more auditable
- **Single point of failure**: USB can be lost or tampered with

**7th Estate approach:**
- Uses blockchain/distributed ledger for transparency
- Multiple copies automatically distributed
- No need for physical media transfer

**Proposed Answer:**
If proofs are published on BB, trustees should be able to read directly from BB. USB transfer makes sense only if:

1. **Security policy**: Organization requires air-gapped operations
2. **Redundancy**: USB is backup, not primary data source
3. **Authentication**: USB data cryptographically signed and verifiable against BB

Best practice: Trustees should:
- Read from public BB (same data everyone else sees)
- Verify BB data cryptographic signatures
- Use air-gapped machines for decryption operations
- Publish their shares and proofs back to BB

---

## Question 5: Trust Assumptions on Trustee Servers

**Q: What exactly is the trust assumption on the Trustee servers? Obviously they must be trusted (on a threshold basis) for privacy. Is there also an integrity trust assumption?**

### Analysis

**Privacy trust:**
- Threshold decryption: k of n trustees needed
- If fewer than threshold are honest, votes remain private

**Integrity trust:**
Two approaches:

1. **Trust for integrity**: Trustees must be honest to produce correct tally
   - Simpler cryptography
   - Must trust threshold of trustees for both privacy and integrity

2. **No trust for integrity**: Trustees publish zero-knowledge proofs
   - Anyone can verify correctness
   - Only privacy requires trustee honesty

**7th Estate approach:**
- Distributed verification across observers
- Public audit of sampling and tallying
- Statistical guarantees rather than cryptographic proofs
- No single trusted party

**Proposed Answer:**
The trust model should be clearly documented:

**For Privacy:**
- Threshold t of n trustees must be honest
- If t trustees collude, individual votes can be revealed
- Example: 3 of 5 trustees must be honest

**For Integrity:**
- **Option 1 (weaker)**: Trust same threshold for correct tallying
- **Option 2 (stronger)**: Zero-knowledge proofs on public BB, anyone can verify

If integrity requires trust (Option 1):
- Document this clearly as a limitation
- Ensure trustees are independent (different organizations, jurisdictions)
- Provide mechanisms for trustee accountability

If integrity is verifiable (Option 2):
- This is stronger and should be claimed as E2E-V
- Ensure proofs are actually published and verifiable
- Provide reference verification implementation

---

## Question 6: Advanced Persistent Threats and Printer Security

**Q: CONOPS says "It is assumed that advanced persistent threats (APTs) have access to all environments." Does that include the printer? To put it another way, if the printer substituted a ballot, what part of the verification process would detect the substitution?**

### Analysis

**Critical security question**: If printer is compromised, it can:
- Print different ballot than what voter chose
- Print different tracking codes
- Make verification meaningless

**Detection mechanisms:**

1. **Display-only verification**: Voter verifies on screen before printing
   - Fails if both screen and printer compromised
   
2. **Independent verification channel**: Voter checks BB later
   - Works if bulletin board shows actual cast vote
   - Requires voter to remember their choices

3. **Multi-device verification**: Verify from different device
   - Good practice but doesn't solve printer problem
   - Only detects if voter actually verifies

4. **Challenge mechanism**: Some ballots are audited before casting
   - Can audit-and-cast or cast-or-audit
   - Makes printer attacks risky but not impossible

**7th Estate approach:**
- Physical ballots mailed to voters (external printer not controlled by system)
- Codes separate from ballot contents
- Statistical sampling makes targeted attacks difficult
- Print audit process

**Proposed Answer:**
If printer is compromised and APTs are in threat model:

**Vulnerabilities:**
- Printer can show voter one thing, submit another
- Voter verification on same device may be compromised
- Challenge mechanisms help but don't eliminate risk

**Mitigations:**
1. **Mandatory second-device verification**: Force verification from different device
2. **Challenge-response protocol**: Voter can choose to audit ballot before casting
3. **Risk-limiting audits**: Post-election audit detects outcome-changing attacks
4. **Trust but verify**: Assume most printers honest, verify with audits
5. **Comparison with paper ballot**: Voter can compare printed code with phone display

**Best answer:** This is a fundamental challenge for any device-based voting system:
- If voter controls device/printer: verification can work
- If adversary controls device/printer: all bets are off
- Physical separation (7th Estate model) avoids this issue
- Hybrid approaches may be necessary for high-security elections

---

## Question 7: Comparison with Other Systems

**Q: How does the threat model, in terms of both privacy and verifiability, compare with those of the Swisspost system, Belenios, Helios, or others?**

### Comprehensive Comparison

#### Systems Overview

| System | Type | Receipt-Free | E2E-V | Threshold Crypto | Key Innovation |
|--------|------|--------------|-------|------------------|----------------|
| **Helios** | Internet | No | Yes | No | Individual verifiability, open source |
| **Belenios** | Internet | No | Yes | No | Formal proofs, simple design |
| **Swiss Post** | Internet | No | Yes | Yes | Commercial deployment, return codes |
| **VoteSecure** | Hybrid | No* | Partial* | Yes | SDK approach, flexible deployment |
| **7th Estate** | Hybrid Paper/Internet | Yes (decoys) | Yes | No | Statistical sampling, decoy ballots |

*Based on available documentation; asterisk indicates uncertainty or conditional claims

#### Detailed Comparison

### Helios
**Strengths:**
- Open source, well-studied
- Simple, understandable
- Individual cast-as-intended verification
- Universal verifiability

**Weaknesses:**
- Not receipt-free (allows vote-selling)
- Single server (availability risk)
- No coercion resistance
- Best for low-stakes elections

**Threat Model:**
- Assumes: Honest verification, voters verify, majority of voters honest
- Does not protect against: Coercion, vote-buying, client compromise for integrity

### Belenios
**Strengths:**
- Formal security proofs
- Open source
- Improved on Helios design
- Clean specification

**Weaknesses:**
- Similar receipt-freeness issues to Helios
- Limited deployment experience
- Academic focus

**Threat Model:**
- Similar to Helios
- Stronger formal guarantees
- Well-defined security properties

### Swiss Post System
**Strengths:**
- Commercial deployment at scale
- Return codes for verification
- Threshold trustees
- Multiple verification layers

**Weaknesses:**
- Proprietary components
- Complex system
- Past security vulnerabilities discovered
- Not fully open source

**Threat Model:**
- Defense in depth approach
- Multiple verification channels
- Commercial-grade security
- Regular security audits

### VoteSecure SDK
**Strengths (based on CONOPS):**
- Flexible deployment (SDK approach)
- Threshold trustees
- Hybrid polling place + remote
- Multiple verification options

**Weaknesses (based on questions):**
- Unclear verification specification
- Receipt-freeness not addressed
- Client compromise mitigations unclear
- Trust model not fully specified

**Threat Model (needs clarification):**
- Appears to assume APTs in all environments
- Unclear how client compromise is handled
- Trustee trust model needs documentation

### 7th Estate / Grassroots Democracy
**Strengths:**
- Novel approach to vote-buying (decoy ballots)
- Hybrid paper/digital verification
- Statistical sampling (efficient for large populations)
- Protection from client malware through physical ballots
- No single point of trust

**Weaknesses:**
- Requires physical infrastructure (mailing ballots)
- Limited deployment experience
- Statistical rather than cryptographic guarantees
- Complexity of decoy ballot system

**Threat Model:**
- Assumes APTs have access to all environments (explicitly stated)
- Protection through:
  - Physical randomness (sampling)
  - Decoy ballots (coercion resistance)
  - Public verification (transparency)
  - Statistical guarantees (sample-based confidence)

**Novel Features:**
1. **Decoy Ballots**: Voters receive multiple ballots, some real, some fake
   - Economic incentives possible without vote-buying
   - Impossible to prove which ballot was real
   - Addresses receipt-freeness in a new way

2. **Hybrid Verification**:
   - Paper ballots (physical security)
   - Online submission (convenience)
   - Public verification (transparency)

3. **Statistical Sampling**:
   - Random sample proves majority opinion
   - More efficient than counting every vote
   - Verifiable randomness through published encrypted rosters

4. **Client Malware Protection**:
   - Physical ballot provides ground truth
   - Online client compromise doesn't affect ballot integrity
   - Multiple verification channels

---

## Analysis for Cosmic Neighborhoods Context

While the cosmic_neighborhoods repository is focused on astronomical survey assignment rather than voting systems, there are interesting parallels in trust and verification:

### Parallels in Trust and Verification

1. **Deterministic Assignment**:
   - Voting: Voters must trust vote tally is correct
   - Cosmic: Users must trust assignment algorithm is fair
   - Both: Verification through transparency and reproducibility

2. **Privacy vs. Verifiability**:
   - Voting: Individual votes must be private but tallies public
   - Cosmic: Individual assignments public but algorithm internals documented
   - Both: Balance between transparency and appropriate privacy

3. **Distribution and Fairness**:
   - Voting: Each voter gets one vote (equality)
   - Cosmic: Each user gets fair patch assignment (equity)
   - Both: Mathematical guarantees of fairness

4. **Auditability**:
   - Voting: Anyone can verify election result
   - Cosmic: Anyone can verify assignment algorithm
   - Both: Open source enables trust

### Lessons from 7th Estate for Cosmic Neighborhoods

While not directly applicable, some principles transfer:

1. **Hybrid Approaches**: 7th Estate combines paper and digital for security
   - Cosmic could combine automated assignment with manual verification tools

2. **Statistical Sampling**: Efficient verification through random sampling
   - Cosmic uses statistical population distribution for fairness

3. **Public Verification**: All verification data published
   - Cosmic could publish test vectors and verification tools

4. **Multiple Verification Channels**: Different ways to verify same result
   - Cosmic could provide multiple tools to verify patch assignments

---

## Recommendations for VoteSecure

Based on this analysis, recommendations for VoteSecure documentation:

### Critical (Must Address)

1. **Formal Verification Specification**:
   - Write formal spec separate from code
   - Define all security properties mathematically
   - Provide test vectors

2. **Clear Threat Model**:
   - Document all trust assumptions explicitly
   - Specify adversary capabilities
   - Define what properties hold under what assumptions

3. **Receipt-Freeness**:
   - Clearly document whether system is receipt-free
   - If not, document vote-buying mitigations
   - Consider alternative approaches (like 7th Estate decoys)

4. **Client Compromise**:
   - Address Question 3b explicitly
   - Document defense-in-depth strategies
   - Provide multi-device verification

5. **Public Proofs**:
   - Clarify whether mixing/decryption proofs are public
   - If yes, document BB access for trustees
   - If no, reconsider E2E-V claims

### Important (Should Address)

6. **Comparison Table**: Provide direct comparison with existing systems

7. **Deployment Guidance**: When is VoteSecure appropriate?
   - Low-stakes vs. high-stakes elections
   - Remote vs. polling place
   - Public vs. private elections

8. **Security Audit**: Independent security review of system and documentation

9. **Reference Implementation**: Full reference verifier

10. **FAQ**: Address common questions from evaluators

### Nice to Have

11. **Formal Proofs**: Prove security properties formally

12. **Usability Testing**: Verify voters can actually use verification

13. **Deployment Case Studies**: Real-world deployment experiences

---

## Conclusion

The questions raised in VoteSecure Issue #2 are fundamental to evaluating any E2E-V voting system. Key findings:

1. **Receipt-freeness appears to be sacrificed** for verifiability, similar to Helios
2. **Formal verification specification is needed** for independent verification
3. **Client compromise threat** is inadequately addressed in current documentation
4. **Public proofs are essential** for E2E-V claims
5. **Trust assumptions must be explicit** for both privacy and integrity
6. **APT assumptions need clarification**, especially for printers and devices
7. **Comparison with other systems** helps contextualize security properties

### Novel Contribution from 7th Estate

The 7th Estate system offers innovative approaches:
- **Decoy ballots** for coercion resistance
- **Hybrid paper/digital** for security against client malware
- **Statistical sampling** for efficiency
- **Multiple verification channels** for robustness

These could inform future iterations of VoteSecure or other systems.

### Applicability to Other Domains

The principles of transparent verification, distributed trust, and clear threat models apply beyond voting:
- Scientific data processing (like cosmic_neighborhoods)
- Distributed consensus systems
- Audit trails and accountability systems
- Any system where trust and verification matter

---

## References

1. **VoteSecure Issue #2**: https://github.com/FreeAndFair/VoteSecure/issues/2
2. **VoteSecure CONOPS**: https://github.com/FreeAndFair/VoteSecure/blob/main/docs/conops/conops.md
3. **7th Estate**: https://github.com/xxfoundation/7th_estate
4. **Random Sample Voting**: https://rsvoting.org/
5. **Helios**: https://vote.heliosvoting.org/
6. **Belenios**: https://www.belenios.org/
7. **ElectionGuard**: https://www.electionguard.vote/

---

## Document History

- 2025-11-17: Initial analysis created for cosmic_neighborhoods repository
- Author: Analysis developed in response to task requirements
- Context: Part of cosmic_neighborhoods project documentation
- License: MIT (consistent with repository license)

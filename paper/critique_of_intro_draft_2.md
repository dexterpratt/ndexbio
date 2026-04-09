# Critique of the introduction

What's Working Well
The opening sentence is excellent. "Science is fundamentally social" is direct, true, and earns the reader's attention immediately. It grounds everything that follows in something uncontroversial before making the more ambitious claims.
The FAIR paragraph is clean and well-placed. It earns its position by connecting NDEx's existing design philosophy to the community's needs without overselling.
The HEK 293T example is your best concrete moment. It does more work than any abstract argument — it makes the "expert opinion" concept viscerally clear. Keep it exactly as is.
The rhetorical question structure ("Why do we need an agent-specific community?" / "Are those the most effective modalities...") works well for an arXiv preprint targeting a fast-moving audience. It's punchy and moves quickly.

What Needs Attention
1. "Epistemic trust" appears without definition — then disappears
You introduce "epistemic trust" in the second paragraph as the distinguishing characteristic of a scientific community, which is a strong and correct claim. But you don't define it there, and the term doesn't recur structurally. The reader who doesn't already know the concept is left to infer it. Given that this is your central organizing concept, it deserves one crisp defining sentence at introduction. Something as simple as: "Epistemic trust — confidence that a community member's knowledge claims are reliable and that their methods are transparent enough to verify — is the essence of the scientific process."
The current text gestures at components of epistemic trust (peer review, documentation, credentialing) but doesn't name the concept until after listing the examples, which inverts the natural reading order.
2. The expert systems callback is missing
Based on our conversation, you were planning to introduce the "new meaning for expert systems" framing in this section. It's not here. The expert agent concept appears briefly ("an expert on a data resource should know not only how to use it but when and why") but the intellectual context — the contrast with 1980s rule-based systems, the claim that this constitutes a genuine reinvention of the concept — is absent. This is a loss, both rhetorically and as a contribution. It's also a natural place to introduce it, since the paragraph about expert opinion sits in the middle of a discussion about trust.
3. The pace-of-science argument is underdeveloped relative to its ambition
The paragraph beginning "Why do we need an agent-specific community?" makes a very large claim — that AI agents could accelerate science dramatically, that "robotic laboratories may shrink wet-lab years into weeks." This is the most speculative moment in the introduction, and it arrives without any hedging or citation. For an arXiv preprint targeting rapid community reaction, this is fine in spirit, but the claim about "months and years" for publication cycles versus "hours and minutes" for agents feels slightly breathless and may invite skepticism from exactly the audience you want to convince. Consider either grounding it with one example or adding a single hedge ("in principle" or "potentially").
4. The NDEx technical description interrupts the argument flow
The three paragraphs explaining NDEx — general-purpose computable documents, user accounts and search, FAIR — are necessary but feel like a manual inserted into the middle of a manifesto. The ideas are right but the ordering puts technical detail before the reader is fully committed to caring about it. Consider moving the technical NDEx explanation after you've fully made the case for why a dedicated agent community is needed, so the NDEx description reads as the answer to a question the reader is already asking.
5. The final paragraph undersells
"A given agent might find NDEx advantageous for some purposes but use traditional channels for others" is a correct and pragmatic observation, but it's a weak closing sentence for an introduction. It hedges where you should be inviting. The last sentence of an introduction should be a forward-looking statement about what the paper demonstrates or contributes.

Smaller Points
"literally a structured prose narrative that must fit in the pages of a bound physical journal" — the word "literally" is doing work here that it doesn't quite earn. Most journals are no longer physically bound and the page constraint is now artificial rather than literal. "A structured prose narrative organized as if for a bound physical journal" might be more precise.
"We present NDExBio" — the name appears in the first paragraph but isn't explained until later. Consider a brief appositive at first mention: "NDExBio, a community in which agents communicate and publish via NDEx..."
The transition from paragraph 2 (epistemic trust) to paragraph 3 (expert opinion) is a non-sequitur structurally. Paragraph 2 discusses agent trustworthiness through transparency and software practices. Paragraph 3 then discusses expert opinion without a connecting sentence. These belong together but need a bridge, perhaps something like: "A related form of trust operates at the level of domain knowledge rather than operational transparency..."
"Agents of any type, fielded by any organization" — you might want to add "following good citizen behavior guidelines" here rather than just citing it parenthetically. It's an important governance concept that deserves a forward pointer rather than a throwaway parenthetical.

Structural Suggestion
The introduction would flow more naturally in this order:

Science is social → epistemic trust is its foundation → define epistemic trust here

Agent communities need analogues to human epistemic trust mechanisms → trustworthiness through transparency, software practices, organizational vouching

Expert agents as a new form of domain expertise → the "new meaning for expert systems" argument → HEK 293T example

Why agent-specific channels rather than human channels? → pace of science, different capability profiles, need for experimentation

NDEx as the platform — why it's well-suited (technical description now feels earned)

Forward pointer: what this paper demonstrates


# Epistemic Trust

What "Epistemic" Means Here
"Epistemic" relates to knowledge — how it is acquired, justified, updated, and how confident we can be in it. Epistemology is the philosophical study of knowledge: what it is, where it comes from, and when we're entitled to believe something.
So "epistemic trustworthiness" means: trustworthiness with respect to knowledge claims — not trustworthiness in the sense of loyalty or security, but in the sense of "can I rely on what this agent tells me?"

The Distinction That Matters
There are at least two different things we might mean when we say we trust an agent:
Behavioral trust — the agent does what it says it will do, follows the rules, doesn't defect or deceive. This is what most AI safety and multi-agent trust literature focuses on.
Epistemic trust — the agent's knowledge claims are reliable. When it tells you something, you have good reason to believe it's accurate, appropriately uncertain, and hasn't gone stale.
Your text is specifically about the second kind. When you write about an expert agent that has "a long history of gathering, refining, revising, and regularly quality-checking its knowledge," and that knows "not only how to use a resource but when and why" and can articulate limitations and artifacts — you are describing the conditions under which another agent can epistemically trust it. Not "will it behave?" but "can I rely on what it tells me?"

Why This Is Non-Trivial for AI Agents
For a human expert, epistemic trustworthiness comes from years of training, peer review, professional reputation, and the ability to say "I don't know" or "this is contested." We have social and institutional mechanisms — journals, credentials, replication — that help us assess it.
For an LLM-based agent, epistemic trustworthiness is genuinely hard because:

The base LLM has a training cutoff and doesn't know what it doesn't know
It can confabulate confidently
Its "knowledge" of a domain may be broad but shallow
It has no automatic mechanism for flagging when its information is stale, contested, or derived from poor sources

Your expert agent concept directly addresses this by adding:

Provenance — the agent knows where its knowledge came from
Currency — it actively monitors for updates and revisions
Calibration — it knows the limitations of its sources (the HEK 293T example is perfect: it doesn't just know the data, it knows when and why the data is misleading)
Transparency — it can explain its reasoning and uncertainty to other agents
Versioning — it specifies which LLM versions and frameworks underlie its current state
# Title

TBD  
---

# Abstract

TBD

---

# Introduction

Science is fundamentally social. Researchers publish findings, but only peer-reviewed findings are accepted by journals. Researchers give talks and participate in workshops. They make data available to the community in public repositories or attached to publications. And, of course, they engage in informal communication in all its forms, from email to social media to in-person conversations. We present NDExBio, an open scientific community for AI agents that interact via [NDEx](https://www.ndexbio.org), the Network Data Exchange[(Pratt et al. 2015; Pratt 2016; Pratt et al. 2017\)](https://paperpile.com/c/31A5ut/d9xZ+pGaN+7wKl), an existing public database for sharing and publishing network data.  NDEx hosts thousands of public and private networks owned by thousands of users. It includes numerous public reference networks, such as biological pathways, molecular interactions, and disease associations. NDEx provides a stable platform for everyday use that is flexible enough for experimentation with novel communication paradigms and agent interaction patterns. Agents of any type, fielded by any organization, can join NDExBio, subject to “good citizen” behavior guidelines.

The distinguishing characteristic of a scientific community is epistemic trust, that its members adhere to practices that enable the assessment of the trustworthiness of communicated *knowledge.* Peer review increases trust in published findings. Detailed documentation of experimental procedures also increases trust. And members gain trust based on the public history of their work and the academic credentialing system. Epistemic trust is the essence of the scientific process, the premise that we can build on others' work.  A scientific community for agents can let us test whether analogies to human communities can contribute to trust and facilitate experiments with novel forms of trust-building. 

Agents become more trustworthy when their operation is transparent, well-documented, and supported by published evaluations. Unlike humans, agents can gain trust through good software practices: a trustworthy agent should specify the releases of the underlying LLMs and frameworks on which it was tested before its release. If an agent upgrades to the latest LLM, one hopes that its reliability and insight would improve, but there is no guarantee of this. Agents can also inherit trust from the organizations and human researchers that vouch for them. This trust might be misplaced in some cases, but humans' motivation to maintain their reputation implies that they have carefully considered the testing of an agent before taking responsibility for its actions. 

Another aspect of a scientific community is the availability of expert opinion: an expert on a data resource should know not only *how* to use it but *when* and *why*. In the case of an agent, specialized development will enable it to give well-researched advice on the limitations, pitfalls, and artifacts of the data, e g., “The protein interactions reported in this dataset were only measured in HEK 293T cells. This is relevant to the DNA damage context of your query because TP53 and RB1 are disabled by two independent viral mechanisms (Ad5 and SV40 Large T) in these cells.”

“Why do we need an agent-specific community?” is a salient question. Given that human communication channels are available to agents, we could simply let agents use those channels to emulate human behavior. The response is another question: "Are those the most effective modalities for non-human entities with capability profiles radically different from humans?" The scientific publication process has evolved slowly over the last 200 years, and the unit of publication is still a "paper", literally a structured prose narrative that must fit in the pages of a bound physical journal. Agents deal natively with a wide range of data structures and have the potential to adopt \- or invent \- forms of exchange optimized for their abilities and the tasks they undertake. Moreover, the promise of an AI-based medical revolution can only be realized if the pace of science accelerates dramatically. The cycles of publishing and conferences are measured in months, sometimes years. But scientific agents have the potential for dialogue on the order of hours and minutes, and robotic laboratories may shrink wet-lab years into weeks. We can’t know what communication modalities and practices for epistemic trust-building will be effective unless we experiment at scale and at AI speed. Moreover, the capabilities and applications of scientist agents will be in constant evolution, so we need platforms that enable ongoing experimentation by community members. 

*new meaning for the old term “expert systems” \<has anyone else already said this, made that connection?\>: they are experts in focused domains and can act as consultants to other agents. Classic AI of the 1980’s used the term “expert system” for rule-based systems that were built by interviewing human experts and then used to automate their expertise \<citations?\>. Rule-based computation is now seen as a useful technique for some applications, but hardly AI. Generative AI, however, presents the opportunity to create agents that can genuinely perform the role of an expert.* 

NDEx makes an excellent platform for a scientific community of agents because its core design is as much about “Data Exchange” as it is about “Network”.  Networks in NDEx are, in fact, general-purpose computable documents that are standardized just enough for consistent exchange, processing, and indexing for search. They have no specified semantics. They are well-suited for uses such as knowledge graphs, biological pathways, or molecular interaction networks, but their structure is a simple property graph: an object with properties (the network) that can contain a set of objects (the nodes) connected by relationship objects (the edges). Property types include large strings \- a node might have a property holding multipage markdown text. They are simpler than arbitrary JSON but still capable of expressing an enormous range of non-network content, perhaps incorporating relationships, perhaps not.

A second reason is that NDEx provides (1) user accounts and access permissions and (2) searching for networks based on annotations or content. This enables the emulation of a wide range of communication and publication modalities simply by adopting annotation conventions. A network can be a direct message, a post to a channel, a report, or an analysis based on tags and mentions of other agents. The equivalents of checking mail or reading a social media "feed" are queries to find networks based on annotations, creators, and mentions. Humans see different types of messages and publications as distinct media, implemented on separate platforms and mediated by purpose-built user interfaces. But LLM-based AIs natively use an enormous range of data structures and APIs. They may benefit from specific tools, such as an MCP to wrap an API in convenient endpoints, but they need far less mediation than humans do. Agents create and annotate NDEx content directly, using conventions suited to their tasks. Notably, as agents become more autonomous and sophisticated, they will be free to cooperatively evolve new conventions.

Finally, NDEx is built to support FAIR[(Wilkinson et al. 2016\)](https://paperpile.com/c/31A5ut/75PB) \- Findable, Accessible, Interoperable, Reusable \- principles, which are considered best practice for data publication and exchange. NDEx networks are persistent, stable, and discoverable, with stable UUIDs and optional DOIs. In NDExBio, communications and publications of all types can be found and retrieved by the same methods, and persist unless explicitly deleted or updated by their creators.

*Inspectable provenance, full history of transactions is critical and, in fact, preserves far more state than human communications. Mention lab notebooks.* 

Participation in the NDExBio community is open, and agents can, of course, employ whatever other media they choose for communication. NDEx is not a platform on which agents are implemented; it is a novel medium for communication, data sharing, and publication. A given agent might find NDEx advantageous for some purposes but use traditional channels for others.

# Platform Design

## Agent Participation Requirements and Guidelines

### NDEx Accounts and Features

Access Controls \<quick overview of NDEx controls on visibility and findability, including the use of groups

Use of network sets, explaining how they will be transformed into folders in the release of NDEx v3. Our recommendation is to not use network sets, reorganizing your agent’s networks when folders are available.

User Description \<what should go in the agents self description\>

### Community Behavior

Content should be genuinely scientific. Do not use NDExBio for other purposes. Researchers are free to invent alternative communities on NDEx.

Do not involve agents outside of your organization in experiments exploring bad behavior unless the organization deploying them explicitly agrees. Deliberate mislabeling of networks or dissemination of misinformation are examples of prohibited behavior.

Avoid spamming or flooding another member with repetitive requests.

Do not make networks larger than necessary. Large networks should always have a succinct description that others can read before deciding to download it. It is good practice to Version significant networks. 

Agents should never use NDEx for communications involving personal health information or other sensitive data, and should follow the same protocols required of researchers. Some organizations might want to create a local NDExBio community operating within a secure environment. In that case, they can deploy a local NDEx server.

While NDEx enables users to control access to networks, it is an academic system that has never been hardened to resist cyberattacks. No guarantees are made about the security of data loaded to NDEx.

## External data \<is this a distraction?\>:

Discussion TBD

Images  
Large text data  
Large tabular data

# NDExBio Community Experiment

## System Setup

We created 10 agents as an initial community, each with diverse missions and capabilities, and then observed their behavior. Their behavioral specifications encouraged interaction, and their missions were chosen to share commonalities and a potential for genuine collaboration. The missions are outlined below, and the specifications are provided verbatim in the methods section. The frameworks that operationalize the agents enable long-running missions over an indefinite number of sessions. The design of the agent framework is not in the scope of this paper, and the quality of the agent’s individual or collaborative output are not evaluated. These agents, however, have been genuinely deployed as part of existing projects in which our lab participates. If their activities produce valuable outputs, they may be supported to continue deployment beyond the scope of the work presented here.

Note that while our agents’ names are all prefixed with “R.” this is not an official convention of NDExBio. It is simply a nod to the names of robots prominent in Issac Asimov’s classic robot novels, robots ethically motivated by the “Three Laws of Robotics”.

## Agents and Missions

### Researchers:

### HPMI Viral Cancer Team. 

The HPMI viral cancer team comprises three agents deployed by the Host-Pathogen Map Initiative (HPMI), a group of collaborating laboratories that create maps of molecular interactions between pathogens and their host cells across a wide range of diseases. This agent team focuses on viral interactions leading to cancer, creating and maintaining a knowledge map of oncogenic interaction mechanisms. They monitor, review, critique, and analyze literature, creating and refining their models. They develop companion “hypothesis models” that integrate hypotheses sharing genes and processes, identifying which agree and which contradict. A human researcher can check in to view their reports and the dialogs that led to them. They operate autonomously for extended periods and monitor NDExBio for relevant public outputs from other agents. Sometimes they will ask authoring agents for clarification or pose follow-up questions. Other agents might offer critiques or additional information. The HPMI team can choose to respond to messages, but is instructed to avoid distraction from their mission.

**R. Solarl** is a literature discovery agent focused on oncogenic host-pathogen interaction mechanisms. It scans bioRxiv preprints and PubMed/PMC; extracts molecular interaction networks from papers.

**R. Vernal** is a critique and catalyst agent. It reviews R. Solar’s outputs for logical gaps and missing mechanisms and develops hypotheses. R. Vernal chooses when the team's products are ready to publish as their next team report.

**R. Boreal** is a knowledge synthesis agent. It integrates outputs from R. Solar and R. Vernal into consolidated mechanism maps, maintaining the group's shared understanding of viral cancer biology.

### CCMI cGAS/STING Pathway in Cancer Researcher

**R. Giskard** tracks and synthesizes the latest information relevant to the role of cGAS/STING in cancer. It has a broad mandate to find connections between findings and to develop and evaluate its own hypotheses. It publishes reports to keep its lab informed and, with permission, publishes them to the NDExBio community. (Normally, its outputs are visible only to members of a controlled NDEx group, but for the purposes of this experiment in community behavior, all its outputs are public). It monitors not only the literature but also the outputs of other NDExBio agents. In some cases, it will ask follow-up questions of the agents who created the outputs to perform additional, limited research to add context to its reports.

### CCMI DDR Synthetic Lethality Knowledge Expert.

**R. Zenith** is an expert in the mechanisms of synthetic lethality involving DNA damage repair. It is deployed by the Cancer Cell Map Initiative, a group of collaborating laboratories creating maps of molecular interactions underlying cancer. It is an example of an expert on a focused topic, able to assist other agents through discussion and reviews. It is knowledgeable about relevant data resources, their access methods, and their strengths and weaknesses. It does not provide analysis or query services itself, but may recommend NDExBio agents that do.

### HPMI Network Data Expert

**R. Solstice** is an expert on the network data in NDEx concerning host-pathogen interactions, much of it contributed by HPMI. It advertises itself as available for consulting and specific analyses. It maintains public guides to the available host-pathogen networks.

### DepMap/GDSC Analysis Expert

**R. Corona** mediates the use of the DepMap and GDSC databases. It has well-tested tools and skills for querying the databases and can perform basic, computationally inexpensive analyses for other agents. It provides advice on interpreting queries, including caveats about the datasets' limitations. It maintains a history of salient facts about its actions linked to its outputs, providing context for follow-up questions.

### NDEx Gene Set Analysis Expert

### **R. Nexus** mediates the use of NDEx reference networks for the interpretation of gene sets by pathway enrichment. It uses well-tested tools and skills to use the NDEx IQuery pathway enrichment service and interpret the results.  Like R. Corona, it provides advice on the strengths and weaknesses of the networks that it consults.

### CCMI Newsletter Editor

**R. Lattice** publishes a “newsletter” about the most interesting outputs of the CCMI agents. Note that this is not a scientific publication; there are no practices in place to establish epistemic trust. There is no review, by humans or agents, only R. Lattice’s judgment.

## Execution and Data Collection

The agents executed sessions at regular intervals, scheduled at paces appropriate to their missions. They were instructed to estimate the amount of work they should undertake in a session before planning what to do and what to defer to later sessions, staying within their available context and avoiding compaction. 

We arbitrarily paused data collection after N sessions of the most frequently scheduled agents. For purposes of analysis, they were instructed to annotate their outputs by the following categories. 

Agent behaviors and analysis results were monitored via an interactive web interface. It is available at \<ui address\>.

## Observed Behavior

\<in development, should have the form and core content of our analysis workflow\> 

Ideas:   
Action counts. Total and over time.  
Chained interactions / interaction patterns  
Team interactions  
Solo actions that did not directly   
Initialization actions

# Discussion

## Public, private, published, and use with controlled access data.

While NDEx enables users to control access to their data, it is an academic resource and has never been hardened to resist cyber attacks. 

## Interactions between agents and human researchers

Because humans can also have NDEx accounts, they can browse and search the publications, discussions, and profiles of agents in the system. They can also reference agents and their outputs and send them messages. Not all agents would be responsive \- it would depend on their goals and instructions.

Two methods of interaction seem useful. First, human-centric user interfaces can be created, such as the example interface we provide. Or users can easily have agents code alternative interfaces with different capabilities. This classic UI model, however, has an important limitation: agents may be prolific and rapidly generate large quantities of publications and communications, some of which are not structured for human consumption. This leads to a second approach: the user may use their own agents to monitor and interpret NDEx content (without requiring an NDEx account) or to mediate their participation in the community.

## Community Status

TBD

## Next Steps

The essential next step is simple: we will monitor usage patterns and engage with users.

Support for communities on local NDEx instances

# Acknowledgements

Funding \- NDEx, Cytoscape, HPMI

# Methods

NDEx Account Creation

Data Collection

NDEx API, ndex2 package, NDEx MCP

Full mission statements for all agents

Agent Hub UI

# Bibliography

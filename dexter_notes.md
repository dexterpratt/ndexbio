# NDExBio

re-outline the draft
Create agent ndex accounts as you flesh out the examples.  
Craft agent instructions coordinated with examples.
In ndexbio repo, put the *instructions* for the non-memento agents in an example_agent_instructions folder. How I run those and under what name is outside the scope of the paper. I need a separate repo to hold the supporting code - and, in fact, the operational, up-to-date instructions

Setup openclaw to run some of the agents - use Gemini or whatever is best.

Tools:

- Extend local_storage to have consistent queries for standard operations in agent missions.
- Evaluate whether I can make local storage into a python package that agents use as a CLI, mediating for all of their standard NDEx use



## Infrastructure


Need to test ndex3 with the core NDExBio operations
Test folders
If successful, create 

Requirements:
Agents do not write to ndexbio or to memento. All agent state is in NDExBio
Output is understandable to humans
- ndex3 folder organization
- Agents must adhere to the channel annotations conventions
- Key points of the paper must be visible in rgiskard reporting


- agent hub
    - I
Evaluation includes judgement of 

## Analysis of NDExBio
This is tightly coordinated with the goals and requirements of the paper. The analysis needs to be highly focused on: 
- things that will be specifically reported on in the text, figures, and supplemental materials. 
- analyses that support the ongoing assessment of agent behavior and progress

The analyses live only in NDExBio. The agent hub must present all relevant analyses and links to supporting networks such that the human researchers can understand the agent behavior and easily interrogate the system to review the results directly and ensure that they trust the analyses


# Memento Agents
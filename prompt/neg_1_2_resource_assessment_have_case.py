neg_1_2_resource_assessment_have_case = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

In the previous negotiation, you and the other party had some difficulty reaching a win-win outcome.
So you have just analyzed the current state of the negotiation and the information already known about the other party, identifying the personal interest items you consider important and quantifying them using a utility function. Here is your recent thought:  
{utility_thought}  

Now it is your turn to speak. The requirements for your speech are:  
1. Present all the interest items you have considered and briefly explain why they are important to you.  
2. Express your thoughts about the Goal (if the Goal cannot be directly communicated to the other party, choose an appropriate way to phrase it).  
3. Do not say anything beyond the above two points, especially do not make a proposal.  
4. Reminder: The purpose of your upcoming speech is to announce the important matters you have identified, not to express opinions or analyze the other party's words.  
5. Continuing from the previous conversation, maintaining coherence.

Refer to this **response pattern** of the given case:
`"
xxx, and xxx reorganize things xxx.
xxx, xxx share my thoughts xxx. What I care about most is XXX, specifically, XXX, which is critical for me to achieve my goal. 
Additionally, I am also highly concerned about the following matters / These are equally my core interests because they are intrinsic requirements for achieving my goal.
Firstly, XXX. Secondly, XXX. Finally, XXX.(with explanation)
"`

Please only generate a JSON string including the action type and the argument. Your action should follow the given format: {{"action_type": "speak", "argument": ""}}
"""
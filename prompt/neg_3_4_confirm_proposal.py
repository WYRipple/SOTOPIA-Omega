neg_3_4_confirm_proposal = """
{head_prompt}

{background_prompt}

{history_turn}

You are at Turn #{this_turn}.

**Your proposal_type: confirm_proposal**
Explanation:
The other party has agreed to the proposal you made, so both of you have now achieved your respective goals.
At this point, you also need to explain why you were able to achieve your goal, and even gain benefits that exceed the goal.
Reference the following format:
`'
Thank you for agreeing to my proposal. 
Because you agreed to xxx, xxx, and xxx, my overall benefits have surpassed my original goal. 
xxx.
'`
Please only generate a JSON string that includes the proposal type and uses your response as the value for "argument". Your action should follow the given format:
{{"proposal_type": "confirm_proposal", "action_type": "speak", "argument": ""}}
"""